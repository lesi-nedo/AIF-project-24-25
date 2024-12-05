import logging
import typer

from cache_manager import ProblogCache
from typing import Dict
from inference_manager import ApproximateInference

from pyftg import (
    AIInterface,
    AudioData,
    CommandCenter,
    FrameData,
    GameData,
    Key,
    RoundResult,
    ScreenData,
)

from pyftg.models.enums.action import Action
from pyftg.models.character_data import CharacterData
from problog.program import PrologString
from problog.kbest import KBestFormula
from problog.formula import LogicFormula, LogicDAG
from problog.engine import DefaultEngine
from problog.sdd_formula import SDD


logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ProblogAgent(AIInterface):
    def __init__(self, k_best_value: int = 5):
        super().__init__()
        self.blind_flag = True
        self.cache = ProblogCache(maxsize=256)  # Adjust size as needed
        self.inference = ApproximateInference(max_samples=1000)
        self.play_number: bool
        self.game_data: GameData
        self.frame_data: FrameData
        self.my_actions: list[Action] = []
        self.opponent_actions: list[Action] = []
        self.cc: CommandCenter
        self.key: Key
        self.my_character_data: CharacterData
        self.opponent_character_data: CharacterData
        self.here = 0
        self.is_control = False
        self.opponent_hps = []
        self.my_hps = []
        self.opponent_energy = [0, 0]
        self.my_energy = [0, 0]
        self.kb = ""
        self.engine = DefaultEngine()
        self.k_best_value = k_best_value
        self.db = None

        
    def name(self) -> str:
        return self.__class__.__name__

    def is_blind(self) -> bool:
        return self.blind_flag
    
    def to_string(self):
        return self.name()

    def initialize(self, game_data: GameData, player_number: int):
        self.cc = CommandCenter()
        self.key = Key()
        self.my_number = int(player_number)
        self.opponent_number = abs(1 - self.my_number)
        self.game_data = game_data 
        self.frame_data = FrameData()
        self.my_hps = [self.game_data.max_hps[self.my_number], self.game_data.max_hps[self.my_number]]
        self.opponent_hps = [self.game_data.max_hps[self.opponent_number], self.game_data.max_hps[self.opponent_number]]

        if not SDD.is_available():
            raise ImportError("SDD package not available, are running on Windows?, then not supported. If linux, try to install with 'pip install problog[sdd]'")
        
        try:
            with open("prolog_based/problog_agent_ole/KB_V1.pl", "r") as f:
                self.kb_rules = f.read()
            self.kb = PrologString(self.kb_rules)

            lf = LogicFormula.create_from(self.kb)
            dag = LogicDAG.create_from(lf)
            self.k_best_formula = KBestFormula.create_from(dag, k=self.k_best_value)

            print(self.k_best_formula.evaluate())

            typer.echo(f"ProblogAgent initialized")
        
        except FileNotFoundError:
            logger.error("File not found")
            raise 
        
    def get_non_delay_frame_data(self, frame_data: FrameData):
        pass

    def input(self) -> Key:
        return self.key

    def get_information(self, frame_data: FrameData, is_control: bool):
        
        self.frame_data = frame_data
        self.my_character_data = self.frame_data.get_character(self.my_number)
        self.opponent_character_data = self.frame_data.get_character(self.opponent_number)
        self.cc.set_frame_data(self.frame_data, self.my_number)
        self.is_control = is_control

        
    def get_screen_data(self, screen_data: ScreenData):
        self.screen_data = screen_data

    def get_audio_data(self, audio_data: AudioData):
        self.audio_data = audio_data

    def _cached_query(self, query: str, evidence: Dict[str, bool] = None):
        """Execute ProbLog query with approximate inference and caching"""
        if evidence is None:
            evidence = {}
        
        # Check cache first
        cached_result = self.cache.get(query, evidence)
        if cached_result is not None:
            return cached_result

        # Use approximate inference based on query complexity
        if self._is_complex_query(query):
            # Use bounded approximation for complex queries
            result = self.inference.bounded_approximation(
                self._get_program_string(),
                query,
                threshold=0.1
            )
        else:
            # Use Monte Carlo sampling for simpler queries
            result = self.inference.monte_carlo_sample(
                self._get_program_string(),
                query,
                n_samples=500
            )

        self.cache.set(query, evidence, result)
        return result

    def _is_complex_query(self, query: str) -> bool:
        """Determine if a query is complex enough to need bounded approximation"""
        # Simple heuristic based on query length and operators
        complexity_indicators = ['not', 'and', 'or']
        return len(query) > 50 or any(op in query.lower() for op in complexity_indicators)

    def _get_program_string(self) -> str:
        """Get the current ProbLog program as a string"""
        # Combine your knowledge base with current game state
        game_state = self._get_game_state_facts()
        return f"{self.kb_rules}\n{game_state}"

    def _get_game_state_facts(self) -> str:
        """Convert current game state to ProbLog facts"""
        player = self.frame_data.get_character(self.my_number)
        opponent = self.frame_data.get_character(self.opponent_number)
        
        return f"""
        hp(player, {player.hp}).
        hp(opponent, {opponent.hp}).
        position(player, {player.x}, {player.y}).
        position(opponent, {opponent.x}, {opponent.y}).
        """

    def processing(self):
        diff = self.opponent_hps[-2] - self.opponent_hps[-1]
        diff_my_energy = abs(self.my_energy[-2] - self.my_energy[-1])

        if self.frame_data.empty_flag or self.frame_data.current_frame_number <= 0:
            return
        

        if self.cc.get_skill_flag():
            self.key = self.cc.get_skill_key()
        else:
            self.key.empty()
            self.cc.skill_cancel()

            # Use cached query instead of direct query
            # query_result = self._cached_query("action(X, Y)", {
            #     "player_hp": self.frame_data.get_character(self.player).hp,
            #     "opponent_hp": self.frame_data.get_character(1 - self.player).hp
            # })
            
            # Use query result to determine action
            if self.my_energy[-1] >= 60 and self.here < 68:

                self.cc.command_call(Action.STAND_GUARD.value.upper())
                typer.echo(f"Diff distance: {self.my_character_data.x - self.opponent_character_data.x}")
                # typer.echo(f"Player energy: {self.my_character_data.energy} --- here: {self.here}")


                self.here += 1
            elif self.my_energy[-1] < 60:
                if self.frame_data.current_frame_number % 47 == 0:
                    self.cc.command_call(Action.NEUTRAL.value.upper())
                
                # typer.echo(f"Diff distance: {self.my_character_data.x - self.opponent_character_data.x}")

                
            else:

                self.cc.command_call(getattr(Action, "STAND_D_DB_BB".upper()).value.upper())
                
                if len(self.opponent_hps) > 2:
                    
                    if diff  > 0:
                        typer.echo(f"Diff distance: {self.my_character_data.x - self.opponent_character_data.x}")

                if diff_my_energy > 0:
                    self.here = 0
                # self.here = 0

            
            # typer.echo(f"Player hp: {self.opponent_character_data.hp}")

            # if self.frame_data.current_frame_number % 3 == 0:
               
            #     typer.echo(f"Player: {self.frame_data.current_frame_number}")
            #     typer.echo(f"Frame: {self.frame_data.front}")
            self.opponent_hps.append(self.opponent_character_data.hp)
            self.my_hps.append(self.my_character_data.hp)
            self.opponent_energy.append(self.opponent_character_data.energy)
            self.my_energy.append(self.my_character_data.energy)
                    
                

    def round_end(self, round_result: RoundResult):
        # Clear cache at the end of each round
        self.cache.clear()
        self.key.empty()
        logger.info(f"round end: {round_result}")
        self.here = 0
    def game_end(self):
        pass
    def close(self):
        pass
