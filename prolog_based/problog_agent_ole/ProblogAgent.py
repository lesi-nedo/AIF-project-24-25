import logging
import typer

from pyswip import Prolog
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

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ProblogAgent(AIInterface):
    def __init__(self):
        super().__init__()
        self.blind_flag = True
        self.cache = ProblogCache(maxsize=256)  # Adjust size as needed
        self.inference = ApproximateInference(max_samples=1000)

    def name(self) -> str:
        return self.__class__.__name__

    def is_blind(self) -> bool:
        return self.blind_flag
    
    def to_string(self):
        return self.name()

    def initialize(self, game_data: GameData, player_number: int):
        logger.info("initialize")
        self.cc = CommandCenter()
        self.key = Key()
        self.player = player_number

    def get_non_delay_frame_data(self, frame_data: FrameData):
        pass

    def input(self) -> Key:
        typer.echo(f"self object methods: {dir(self)}")
        return self.key

    def get_information(self, frame_data: FrameData, is_control: bool):
        
        self.frame_data = frame_data
        self.cc.set_frame_data(self.frame_data, self.player)

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
        player = self.frame_data.get_character(self.player)
        opponent = self.frame_data.get_character(1 - self.player)
        
        return f"""
        hp(player, {player.hp}).
        hp(opponent, {opponent.hp}).
        position(player, {player.x}, {player.y}).
        position(opponent, {opponent.x}, {opponent.y}).
        """

    def processing(self):
        if self.frame_data.empty_flag or self.frame_data.current_frame_number <= 0:
            return
        
        typer.echo(f"frame data: {self.frame_data}")

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
            self.cc.command_call("2 3 6 _ C")

    def round_end(self, round_result: RoundResult):
        # Clear cache at the end of each round
        self.cache.clear()
        logger.info(f"round end: {round_result}")

    def game_end(self):
        logger.info("game end")

    def close(self):
        pass
