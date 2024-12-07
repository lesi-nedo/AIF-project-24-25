import logging
import typer
import time
import random

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
from problog.logic import Term, Constant, Var, term2list, term2str
from problog import get_evaluatable




logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
problog_logger = logging.getLogger("problog")
problog_logger.setLevel(logging.ERROR)


class ProblogAgent(AIInterface):
    def __init__(self, k_best_value: int = 5):
        time.sleep(15)
        super().__init__()
        self.blind_flag = True
        self.cache = ProblogCache(maxsize=256)  # Adjust size as needed
        self.inference = ApproximateInference(max_samples=1000)
        self.play_number: bool
        self.game_data: GameData
        self.frame_data: FrameData
        self.my_actions: list[Action] = [Action.NEUTRAL]
        self.opponent_actions_type: list[Action] = ["movement"]
        self.my_actions_type: list[str] = ["movement"]
        self.my_state = [Action.STAND]
        self.opponent_state = [Action.STAND]
        self.my_curr_pos = [(0, 0)]
        self.opponent_curr_pos = [(0, 0)]

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
        self.db_org = None
        self.count_frames = 0
        self.sent = False
        self.enough = False
        self.prefix = "prolog_based/problog_agent_ole/"
        self.kb_rules_file_name = "KB_V1.pl"
        self.kb_path_rules = self.prefix + self.kb_rules_file_name

        self.counters = {
            'me': {
                'stand': 0,
                'down': 0,
                'air': 0,
                'crouch': 0,
                'total': 1
            },
            'opponent': {
                'stand': 0,
                'down': 0,
                'air': 0,
                'crouch': 0,
                'total': 1
            }
        }

        self.state_counters = {
            'me': {
                'stand': lambda: self._increment_counter('me', 'stand'),
                'down': lambda: self._increment_counter('me', 'down'),
                'air': lambda: self._increment_counter('me', 'air'),
                'crouch': lambda: self._increment_counter('me', 'crouch')
            },
            'opponent': {
                'stand': lambda: self._increment_counter('opponent', 'stand'),
                'down': lambda: self._increment_counter('opponent', 'down'),
                'air': lambda: self._increment_counter('opponent', 'air'),
                'crouch': lambda: self._increment_counter('opponent', 'crouch')
            }
        }

        self.name_conv = {
            "me": "my",
            "opponent": "opponent"
        }
        

        
    def name(self) -> str:
        return self.__class__.__name__

    def is_blind(self) -> bool:
        return self.blind_flag
    
    def to_string(self):
        return self.name()
    
    def _init_vars(self):
        self.cc = CommandCenter()
        self.key = Key()
        self.opponent_number = abs(1 - self.my_number)
        self.frame_data = FrameData()
        self.my_hps = [self.game_data.max_hps[self.my_number], self.game_data.max_hps[self.my_number]]
        self.opponent_hps = [self.game_data.max_hps[self.opponent_number], self.game_data.max_hps[self.opponent_number]]

        self.my_actions: list[Action] = [Action.NEUTRAL]
        self.opponent_actions_type: list[str] = ["movement"]
        self.my_actions_type: list[str] = ["movement"]
        self.my_state = [Action.STAND]
        self.opponent_state = [Action.STAND]

        self.my_curr_pos = [(0, 0)]
        self.opponent_curr_pos = [(0, 0)]


        self.db_enriched = self.db_org.extend()


        me_str_hp = f"curr_hp_value(me, {self.my_hps[0]}).\n"
        me_str_energy = f"curr_energy_value(me, {self.my_energy[0]}).\n"
        opponent_str_hp = f"curr_hp_value(opponent, {self.opponent_hps[0]}).\n"
        opponent_str_energy = f"curr_energy_value(opponent, {self.opponent_energy[0]}).\n"
        
        count_state_me, count_total_states_me = f"count_state(me, stand, {self.counters['me']['stand']}).\n", f"count_total_states(me, {self.counters['me']['total']}).\n"
        count_state_opponent, count_total_states_opponent = f"count_state(opponent, stand, {self.counters['opponent']['stand']}).\n", f"count_total_states(opponent, {self.counters['opponent']['total']}).\n"
        
        me_prev_hp, me_prev_energy = f"prev_hp_value(me, {self.my_hps[0]}).\n", f"prev_energy_value(me, {self.my_energy[0]}).\n"
        opponent_prev_hp, opponent_prev_energy = f"prev_hp_value(opponent, {self.opponent_hps[0]}).\n", f"prev_energy_value(opponent, {self.opponent_energy[0]}).\n"
        
        me_prev_action = f"prev_action_type(me, movement).\n"
        opponent_prev_action = f"prev_action_type(opponent, movement).\n"

        me_curr_pos = f"curr_pos(me, {self.my_curr_pos[0][0]}, {self.my_curr_pos[0][1]}).\n"
        opponent_curr_pos = f"curr_pos(opponent, {self.opponent_curr_pos[0][0]}, {self.opponent_curr_pos[0][1]}).\n"

        str_concat = "\n".join([
            me_str_hp, me_str_energy, opponent_str_hp, opponent_str_energy, count_state_me, 
            count_total_states_me, count_state_opponent, count_total_states_opponent,
            me_prev_hp, me_prev_energy, opponent_prev_hp, opponent_prev_energy, me_prev_action, opponent_prev_action, 
            me_curr_pos, opponent_curr_pos])
        for statement in PrologString(str_concat):
            self.db_enriched += statement
            typer.echo(f"Statement: {statement}")

        lof = self.engine.ground_all(self.db_enriched)
        self.sdd =  get_evaluatable(name='sdd')
        
        
        self.cache.clear()
        self.counters = {
            'me': {
                'stand': 0,
                'down': 0,
                'air': 0,
                'crouch': 0,
                'total': 1
            },
            'opponent': {
                'stand': 0,
                'down': 0,
                'air': 0,
                'crouch': 0,
                'total': 1
            }
        }
        self.here = 0


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
            with open(self.kb_path_rules, "r") as f:
                self.kb_rules = f.read()
            self.kb = PrologString(self.kb_rules)
            self.db_org = self.engine.prepare(self.kb)

            
        
        except FileNotFoundError:
            logger.error("File not found")
            raise 

        self._init_vars()
        typer.echo(f"ProblogAgent initialized")
        
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
    
    def select_action_from_problog_results(self, result):
        """Selects an action probabilistically from ProbLog k-best results."""
        try:
            # Check if result exists and is iterable
            if not result or not hasattr(result, 'items'):
                typer.echo(f"Result: {result}")
                logger.warning("Invalid result format from ProbLog")
                return None
                
            # Extract valid actions and their probabilities
            action_probs = []
            for res, prob_tuple in result.items():
                try:
                    # Handle different probability formats
                    prob = prob_tuple[0] if isinstance(prob_tuple, tuple) else prob_tuple

                    # typer.echo(f"Type: {type(res)}")
                    # if hasattr(res, 'args'):
                    #     typer.echo(f"Args: {res.args}")
                    # typer.echo(f"Type args: {type(res.args[1])}")
                    # Get actions   list from result
                    action = res.args[1] if hasattr(res, 'args') else res
                    if isinstance(action, Term):
                        action = term2str(action)
                        return action
                    
                    action = term2list(action)
                    

                    
                    if action:  # Skip empty lists
                        action_probs.append((action, float(prob)))
                except (AttributeError, IndexError, TypeError) as e:
                    typer.echo(f"Error processing result item: {e}")
                    continue
            
            if not action_probs:
                return None
            
            
            # Choose action list based on probabilities
            actions_list, probs = zip(*action_probs)
            chosen_actions = random.choices(actions_list, weights=probs, k=1)[0]
            
            return random.choice(chosen_actions) if chosen_actions else None
        
        except Exception as e:
            typer.echo(f"Error in select_action_from_problog_results: {e}")
            pass
            # exit(1)

    def processing(self):
        if self.frame_data.empty_flag or self.frame_data.current_frame_number <= 0:
            return
        diff = 0
        diff_my_energy = 0

        if self.sent:
            self.count_frames += 1

        if self.cc.get_skill_flag(): 
            self.key = self.cc.get_skill_key()
        else:

            self.key.empty()
            self.cc.skill_cancel()
            self.opponent_actions_type.append(self.estimate_opponent_action())
            self.my_actions_type.append(self._get_type_action(self.my_character_data.action.value))
            self.my_state.append(self.my_character_data.state)
            self.opponent_state.append(self.opponent_character_data.state)
            self.my_curr_pos.append((self.my_character_data.x, self.my_character_data.y))
            self.opponent_curr_pos.append((self.opponent_character_data.x, self.opponent_character_data.y))

            diff_my_energy = abs(self.my_energy[-1] - self.my_character_data.energy)

            
            self._increment_counter('me', self.my_character_data.state.value)
            self._increment_counter('opponent', self.opponent_character_data.state.value)

        
            query_state = Term("possible_state", Term(self.my_character_data.state.value))


            db = self._add_to_db_hp_energy_state()
            lf = self.engine.ground_all(
                db,
                evidence=[
                    # (my_state_evid, True), 
                    # (opponent_state_evid, True),
                ]
            )
            
            self.sdd_formula = self.sdd.create_from(lf)
            result = self.sdd_formula.evaluate()
            action = self.select_action_from_problog_results(result)

            

            action = term2str(action).upper()
            typer.echo(f"Action to Take: {action}")
            if action:
                self.cc.command_call(action)
            

            # if self.frame_data.current_frame_number % 37 == 0:
            #     typer.echo(f"Action: {result}")

                # typer.echo(f"Player state: {self.my_character_data.state.value}")
                # pass
                
                
                # for ev in  self.sdd_formula.evidence():
                #     typer.echo(f"Evidence: {ev}")
                
           

            # # Use cached query instead of direct query
            # query_result = self._cached_query("action(X, Y)", {
            #     "player_hp": self.frame_data.get_character(self.player).hp,
            #     "opponent_hp": self.frame_data.get_character(1 - self.player).hp
            # })
            
            # # Use query result to determine action
            # if self.my_energy[-1] >= 5 and self.here < 6:
            #     self.enough = True

            #     self.cc.command_call(Action.STAND_GUARD.value.upper())
            #     # typer.echo(f"Player energy: {self.my_character_data.energy} --- here: {self.here}")


            #     self.here += 1
            # elif self.my_energy[-1] < 5:
            #     if self.frame_data.current_frame_number % 47 == 0:
            #         self.cc.command_call(Action.NEUTRAL.value.upper())
                
            #     # typer.echo(f"Diff distance: {self.my_character_data.x - self.opponent_character_data.x}")

                
            # else:
            #     self.sent = True
            #     self.cc.command_call(getattr(Action, "air_d_db_ba".upper()).value.upper())
                
            
            # if diff_my_energy > 0 and self.enough:
            #     self.sent = False
            #     # typer.echo(f"Player energy: {self.my_character_data.energy} --- here: {self.here} --- count_frames: {self.count_frames}")
            #     self.count_frames = 0
            #     self.here = 0


            
            # typer.echo(f"Player hp: {self.opponent_character_data.hp}")

            # if self.frame_data.current_frame_number % 3 == 0:
               
            #     typer.echo(f"Player: {self.frame_data.current_frame_number}")
            #     typer.echo(f"Frame: {self.frame_data.front}")
            self.my_actions.append(self.my_character_data.action) 
            self.opponent_hps.append(self.opponent_character_data.hp)
            self.my_hps.append(self.my_character_data.hp)
            self.opponent_energy.append(self.opponent_character_data.energy)
            self.my_energy.append(self.my_character_data.energy)
            self.my_actions.append(self.my_character_data.action)
                    
    def _get_hp_energ_evd(self, player: str):

        health_value = Term("health_value", Term(player), Constant(int(getattr(self, f"{self.name_conv.get(player)}_character_data").hp)), arity=2)
        energy_value = Term("energy_value", Term(player), Constant(int(getattr(self, f"{self.name_conv.get(player)}_character_data").energy)), arity=2)
        return health_value, energy_value
    
    def _get_state_evd(self, player: str):
        character = getattr(self, f"{self.name_conv.get(player)}_character_data")

        count_state_evid = Term(
            "state", Term(player), Term(character.state.value),
            Constant(self.counters[player][character.state.value]),
            Constant(self.counters[player]['total']),
            arity=4
        )
        return count_state_evid
    

    def _get_state_evd(self, player: str):
        character = getattr(self, f"{self.name_conv.get(player)}_character_data")

        count_state_evid = Term(
            "count_state", Term(player), Term(character.state.value),
            Constant(self.counters[player][character.state.value]), arity=3
        )

        count_total_states_evid = Term(
            "count_total_states", Term(player),
            Constant(self.counters[player]['total']), arity=2
        )
        return count_state_evid, count_total_states_evid

    def _get_clause_eng_hp(self, player: str):
        str_hp = f"curr_hp_value({player}, {getattr(self, f'{self.name_conv.get(player)}_character_data').hp})"
        str_energy = f"curr_energy_value({player}, {getattr(self, f'{self.name_conv.get(player)}_character_data').energy})"
        return f"{str_hp}.\n", f"{str_energy}.\n"
    
    def _get_clause_state(self, player: str):
        character = getattr(self, f"{self.name_conv.get(player)}_character_data")
        return f"count_state({player}, {character.state.value}, {self.counters[player][character.state.value]}).\n", f"count_total_states({player}, {self.counters[player]['total']}).\n"
    
    def _get_prev_hp_energy(self, player: str):
        prev_hp = getattr(self, f"{self.name_conv.get(player)}_hps")[-1]
        prev_energy = getattr(self, f"{self.name_conv.get(player)}_energy")[-1] 
        return f"prev_hp_value({player}, {prev_hp}).\n", f"prev_energy_value({player}, {prev_energy}).\n"
    
    def _get_clause_prev_action(self, player: str):
        prev_action = getattr(self, f"{self.name_conv.get(player)}_actions_type")[-1]
        return f"prev_action_type({player}, {prev_action}).\n"
    
    def _get_clause_curr_pos(self, player: str):
        curr_pos = getattr(self, f"{self.name_conv.get(player)}_curr_pos")[-1]
        return f"curr_pos({player}, {curr_pos[0]}, {curr_pos[1]}).\n"
        
    def _check_changed(self,):
        to_ret = []
        my_health_value, my_energy_value = self._get_hp_energ_evd("me")
        opponent_health_value, opponent_energy_value = self._get_hp_energ_evd("opponent")
        
        my_state_evid, my_total_states_evid = self._get_state_evd("me")
        opponent_state_evid, opponent_total_states_evid = self._get_state_evd("opponent")
        if self.my_character_data.hp != self.my_hps[-1]:
            to_ret.append((my_health_value, True))
        if self.my_character_data.energy != self.my_energy[-1]:
            to_ret.append((my_energy_value, True))
        
        if self.opponent_character_data.hp != self.opponent_hps[-1]:
            to_ret.append((opponent_health_value, True))
        if self.opponent_character_data.energy != self.opponent_energy[-1]:
            to_ret.append((opponent_energy_value, True))
        
        return to_ret
    
    def _add_to_db_hp_energy_state(self):
        db = self.db_org.extend()
        changed = False
        
        my_str_hp, my_str_energy = self._get_clause_eng_hp("me")
        opponent_str_hp, opponent_str_energy = self._get_clause_eng_hp("opponent")
        my_state_clause, my_total_states_clause = self._get_clause_state("me")
        opponent_state_clause, opponent_total_states_clause = self._get_clause_state("opponent")
        my_prev_hp, my_prev_energy = self._get_prev_hp_energy("me")
        opponent_prev_hp, opponent_prev_energy = self._get_prev_hp_energy("opponent")
        my_curr_pos = self._get_clause_curr_pos("me")
        opponent_curr_pos = self._get_clause_curr_pos("opponent")
        my_prev_action_type = self._get_clause_prev_action("me")
        opponent_prev_action_type = self._get_clause_prev_action("opponent")

        if self.my_character_data.hp != self.my_hps[-1] or self.my_character_data.energy != self.my_energy[-1]:
            concat_str = "\n".join([
                my_str_hp, my_str_energy, my_state_clause, my_total_states_clause, 
                my_prev_hp, my_prev_energy, my_curr_pos, my_prev_action_type
            ])
            for statement in PrologString(concat_str):
                db += statement
            changed = True

        if self.opponent_character_data.hp != self.opponent_hps[-1] or self.opponent_character_data.energy != self.opponent_energy[-1]:
            concat_str = "\n".join([
                opponent_str_hp, opponent_str_energy, opponent_state_clause, opponent_total_states_clause, 
                opponent_prev_hp, opponent_prev_energy, opponent_curr_pos, opponent_prev_action_type
            ])
            for statement in PrologString(concat_str):
                db += statement
            changed = True
        
        if changed:        
            self.db_enriched = db
            
        return self.db_enriched
        
        
    def _increment_counter(self, agent: str, state: str) -> None:
        self.counters[agent][state] += 1
        self.counters[agent]['total'] += 1


    def estimate_opponent_action(self):
        my_prev_type_action = self._get_type_action(self.my_actions[-1])
        my_hp_diff = self.my_hps[-1] - self.my_character_data.hp

        if my_hp_diff > 0:
           return "attack"
        opponent_energy = self.opponent_energy[-1] - self.opponent_character_data.energy

        if opponent_energy > 0 and (my_prev_type_action == "movement" or my_prev_type_action == "defense"):
            return "energy"
        


    def _get_type_action(self, action: str):
        attack_actions = {
            "stand_d_df_fc": "energy",
            "stand_f_d_dfb": "attack",
            "air_d_df_fa": "energy",
            "stand_d_db_bb": "attack",
            "air_d_db_ba": "attack",
            "stand_f_d_dfa": "attack",
            "stand_fa": "attack",
            "air_fb": "attack",
            "stand_fb": "attack",
            "crouch_fb": "attack",
            "stand_a": "attack",
            "stand_b": "attack",
            "dash": "movement",
            "back_step": "movement",
            "for_jump": "movement",
            "back_jump": "movement",
            "stand_guard": "defense",
            "crouch_guard": "defense",
            "air_guard": "defense",

        }
      
        type = attack_actions.get(action, "defense")
        if type is None:
            typer.echo(f"Action type None: {action}")
        return type

    def round_end(self, round_result: RoundResult):
        # Clear cache at the end of each round
        self._init_vars()
        logger.info(f"round end: {round_result}")

    def game_end(self):
        pass
    def close(self):
        pass
