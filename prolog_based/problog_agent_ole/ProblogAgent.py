import logging
import queue
import numpy as np
import typer
import time
import random
import os
import sys
import matplotlib.pyplot as plt
import cv2
import matplotlib
import logging

logging.getLogger().setLevel(logging.WARNING)
# Suppress PIL debug logging
logging.getLogger('PIL').setLevel(logging.WARNING)

# Suppress matplotlib font manager debug logging
logging.getLogger('matplotlib.font_manager').setLevel(logging.WARNING)

# Suppress matplotlib debug logging
logging.getLogger('matplotlib').setLevel(logging.WARNING)

# Suppress debug messages for PNG handling
logging.getLogger('PIL.PngImagePlugin').setLevel(logging.WARNING)
matplotlib.use('Agg') 


# Get the absolute path of the project root directory 
project_root = os.path.abspath(os.path.join(os.getcwd()))

# Add both the root and problog agent directory to Python path
sys.path.append(project_root)
sys.path.append(os.path.join(project_root, 'prolog_based', 'problog_agent_ole'))

print(f"Project root: {project_root}")

from display_thread import DisplayThread
from typing import Dict

from IPython import display

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

from mappings import actions_type
from terms import attack_b_actions


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
problog_logger = logging.getLogger("problog")
problog_logger.setLevel(logging.ERROR)

class ProblogAgent(AIInterface):
    def __init__(self, k_best_value: int = 5, plot_scenes: bool = False):
        # time.sleep(20)
        super().__init__()
        self.blind_flag = False
        self.width = 960
        self.height = 640
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
        self.plot_scenes = plot_scenes
        self.cc: CommandCenter
        self.key: Key
        self.empty_key_dict = Key().to_dict()
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
        self.time_taken = []
        self.enough = False
        self.prefix = "./prolog_based/problog_agent_ole/"
        self.kb_rules_file_name = "KB_V1.pl"
        self.kb_path_rules = self.prefix + self.kb_rules_file_name
        self.exec_action = ["dash"]
        self.my_hboxes = []
        self.opponent_hboxes = []
        self.screen_data_raw = None
        self.echo = typer.echo
     
        # Initialize plot on first frame if not already done
        if self.plot_scenes:
            self._init_plots()
            self.echo = self.display_thread.add_log

        self.default_positions = {
            0: (720, 537),
            1: (240, 537)
        }
        self.default_hbox = {
            1: {
                "left": 200,
                "right": 260,
                "top": 435,
                "bottom":640
            },
            0: {
                "left": 700,
                "right": 740,
                "top": 435,
                "bottom": 640
            }
        }
        self.default_dir = {
            0: -1,
            1: 1
        }
        self.direction = {
                    1: 1,
                    0: -1
                }
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
        self.my_hboxes.append(self.default_hbox.get(self.my_number))
        self.opponent_hboxes.append(self.default_hbox.get(self.opponent_number))

        self.my_curr_pos = [self.default_positions.get(self.my_number)]
        self.opponent_curr_pos = [self.default_positions.get(self.opponent_number)]
        
        

        self.db_enriched = self.db_org.extend()

        my_prev_action = f"my_prev_action(stand).\n"
        me_str_hp = f"curr_hp_value(me, {self.my_hps[0]}).\n"
        me_str_energy = f"curr_energy_value(me, {self.my_energy[0]}).\n"
        opponent_str_hp = f"curr_hp_value(opponent, {self.opponent_hps[0]}).\n"
        opponent_str_energy = f"curr_energy_value(opponent, {self.opponent_energy[0]}).\n"
        opp_action_type = f"opp_action_type(stand).\n"
        count_state_opponent, count_total_states_opponent = f"count_state(stand, {self.counters['opponent']['stand']}).\n", f"count_total_states({self.counters['opponent']['total']}).\n"
        my_facing_dir = f"facing_dir(me, {self.default_dir.get(self.my_number)}).\n"
        opponent_facing_dir = f"facing_dir(opponent, {self.default_dir.get(self.opponent_number)}).\n"
        me_curr_pos = f"1.0::curr_pos(me, {self.my_curr_pos[0][0]}, {self.my_curr_pos[0][1]}).\n"
        opponent_curr_pos = f"0.9::curr_pos(opponent, {self.opponent_curr_pos[0][0]}, {self.opponent_curr_pos[0][1]}).\n"
        my_state = f"my_state(stand).\n"

        self.exec_action = ["dash"]
        self.count_frames = 0


        str_concat = "\n".join([
            me_str_hp, me_str_energy, opponent_str_hp, opponent_str_energy,
            count_state_opponent, count_total_states_opponent, my_state,
            me_curr_pos, opponent_curr_pos, my_facing_dir, opponent_facing_dir,
            opp_action_type, my_prev_action])
        for statement in PrologString(str_concat):
            self.db_enriched += statement
            typer.echo(f"Statement: {statement}")

        lof = self.engine.ground_all(self.db_enriched)
        self.sdd =  get_evaluatable(name='sdd')
        
        
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

        logger.info(f"Is blind: {self.is_blind()}")
        if self.is_blind():
            exit(1)
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
        (f"ProblogAgent initialized")
        
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

    def get_audio_data(self, audio_data: AudioData):
        self.audio_data = audio_data


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
        position(player, {player.x}, {player.y}).$
        position(opponent, {opponent.x}, {opponent.y}).
        """ 
    
    def select_action_from_problog_results(self, result):
        """Selects an action probabilistically from ProbLog k-best results."""
        try:
            # self.echo(f"Result: {result}")
            # Check if result exists and is iterable
            
            if not result or not hasattr(result, 'items'):
                self.echo(f"Result: {result}")
                logger.warning("Invalid result format from ProbLog")
                return None
                
            # Extract valid actions and their probabilities
            action_weights_dit = {}
            for res, prob in result.items():
                # Remember the arity of the term
                weight = prob
                try:
                    if isinstance(res, Term):
                        
                        # self.echo(f"Res- prob: {res.probability}")
                        action = term2str(res.args[0])
                        if action == "stand_d_df_fc":
                            return action
                        if hasattr(res.args[1], 'compute_value'):
                            weight += res.args[1].compute_value()
                        else:
                            weight += res.args[1]
                            action = term2str(random.choice(attack_b_actions))

                        
     
                        if action not in action_weights_dit:
                            action_weights_dit[action] = weight
                        else:
                            action_weights_dit[action] += weight
                    else:
                        self.echo(f"Result not isinstance: {res}")
                        action = term2list(res)
                        return random.choice(action)
                    
                except (AttributeError, IndexError, TypeError) as e:
                    self.echo(f"Error processing result item: {e}")
                    continue
            

            action_weights_list = [(action, prob) for action, prob in action_weights_dit.items() if prob > 0.0]
            if not action_weights_list:
                self.echo(f"Result-in not action_prob_list: {result}")
                return 'dash'
            
           
            # Choose action list based on probabilities
            actions_list, weights = zip(*action_weights_list)
            return random.choices(actions_list, weights=weights, k=1)[0]
        
        except Exception as e:
            self.echo(f"Result: {result}")
            self.echo(f"Error in select_action_from_problog_results: {e}")
            pass
            # exit(1)

    def processing(self):
        if self.frame_data.empty_flag or self.frame_data.current_frame_number <= 0:
            return
        
        if self.sent:
            self.count_frames += 1
        
        if self.cc.get_skill_flag():
            self.key = self.cc.get_skill_key()
        elif self.frame_data.current_frame_number % 2 == 0:

            self.sent = False
            self.key.empty()
            self.cc.skill_cancel()
            self.opponent_actions_type.append(self.estimate_opponent_action())
            self.my_state.append(self.my_character_data.state)
            self.opponent_state.append(self.opponent_character_data.state)
           
            self.my_curr_pos.append((self.my_character_data.x, self.my_character_data.y))

            px = (self.opponent_character_data.attack_data.impact_x + self.opponent_character_data.speed_x)*self.count_frames
            py = (self.opponent_character_data.attack_data.impact_x +self.opponent_character_data.speed_y)*self.count_frames
            
            px *= self.default_dir.get(self.opponent_character_data.front)
            py *= self.default_dir.get(self.opponent_character_data.front)
            self.opponent_curr_pos.append((self.opponent_character_data.x+px, 
                                           self.opponent_character_data.y+py))

            
            self._increment_counter('me', self.my_character_data.state.value)
            self._increment_counter('opponent', self.opponent_character_data.state.value)
            # opp_facing_dir_evd = self._get_opp_facing_dir_evd()
            # opp_action_type_evd = self._get_opp_prev_action_type_evd()
     
        
            before_exec = time.time()
            db = self._add_to_db_hp_energy_state()
            lf = self.engine.ground_all(
                db,
                evidence=[
                    # opp_facing_dir_evd, 
                    # *opp_action_type_evd
                ]
            )
            
            self.sdd_formula = self.sdd.create_from(lf)
            result = self.sdd_formula.evaluate()

            after_exec = time.time()
            self.time_taken.append(after_exec - before_exec)
            # self.echo(f"Result: {result}")
            # action = "dash".upper()
            action = self.select_action_from_problog_results(result).upper()
            self.cc.command_call(action)


            self.echo(f"Action to execute: {action}")

            self.my_actions.append(self.my_character_data.action) 
            self.opponent_hps.append(self.opponent_character_data.hp)
            self.my_hps.append(self.my_character_data.hp)
            self.opponent_energy.append(self.opponent_character_data.energy)
            self.my_energy.append(self.my_character_data.energy)
            self.sent = True
            self.count_frames = 0
                    
    
    def _get_opp_facing_dir_evd(self):
        my_facing_dr = self.my_character_data.front
        opp_facing_dir = self.opponent_character_data.front
        diff_facings = my_facing_dr != opp_facing_dir
        self.echo(f"Opp facing dir: {diff_facings}")
        opp_facing_dir_evd = Term("opposite_facing_dir", Term("me"), Term("opponent"), arity=2) 
        return (opp_facing_dir_evd, diff_facings)
    

    
    def _get_opp_prev_action_type_evd(self):
        action_types = {
            "attack": False,
            "special": False,
            "defense": False,
            "non_attack": False
        }
        prev_action = self.opponent_actions_type[-1]
        action_types[prev_action] = True
        all_evd = []
        for action_type, value in action_types.items():
            all_evd.append((Term("approx_opponent_prev_action_type", Term(action_type), arity=1), value))
        return all_evd

    def _get_clause_opp_action_type(self):
        action_type = self.opponent_actions_type[-1]
        return f"opp_action_type({action_type}).\n"

    def _get_clause_eng_hp(self, player: str):
        str_hp = f"curr_hp_value({player}, {getattr(self, f'{self.name_conv.get(player)}_character_data').hp})"
        str_energy = f"curr_energy_value({player}, {getattr(self, f'{self.name_conv.get(player)}_character_data').energy})"
        return f"{str_hp}.\n", f"{str_energy}.\n"
    
    def _get_clause_count_state(self, player: str):
        character = getattr(self, f"{self.name_conv.get(player)}_character_data")
        return f"count_state({character.state.value}, {self.counters[player][character.state.value]}).\n", f"count_total_states({self.counters[player]['total']}).\n"
    
    def _get_prev_hp_energy(self, player: str):
        prev_hp = getattr(self, f"{self.name_conv.get(player)}_hps")[-1]
        prev_energy = getattr(self, f"{self.name_conv.get(player)}_energy")[-1] 
        return f"prev_hp_value({player}, {prev_hp}).\n", f"prev_energy_value({player}, {prev_energy}).\n"
    
    def _get_clause_prev_action(self, player: str):
        prev_action = getattr(self, f"{self.name_conv.get(player)}_actions_type")[-1]
        return f"prev_action_type({player}, {prev_action}).\n"
    
    def _get_clause_curr_pos(self, player: str):
        curr_pos = getattr(self, f"{self.name_conv.get(player)}_curr_pos")[-1]
        prob = 1.0 if player == "me" else 0.9
        return f"{prob}::curr_pos({player}, {curr_pos[0]}, {curr_pos[1]}).\n"
    
    def _get_clause_facing_dir(self, player: str):
        curr_facing_dir = getattr(self, f"{self.name_conv.get(player)}_character_data").front
        curr_facing_dir = self.direction.get(int(curr_facing_dir))
        return f"facing_dir({player}, {curr_facing_dir}).\n"
    
    def _get_clause_my_state(self):
        return f"my_state({self.my_character_data.state.value}).\n"
    
    def _get_hbox_clause(self, player: str):
        hbox = getattr(self, f"{self.name_conv.get(player)}_hboxes")[-1]
        return f"0.95::hbox({player}, {hbox['left']}, {hbox['right']}, {hbox['top']}, {hbox['bottom']}).\n"
    
    def _get_clause_my_prev_action(self):
        prev_action = self.my_actions[-1].value
        prev_action = prev_action.lower()
        
        return f"my_prev_action({prev_action}).\n"
    
    def _add_to_db_hp_energy_state(self):
        db = self.db_org.extend()
        
        my_str_hp, my_str_energy = self._get_clause_eng_hp("me")
        opponent_str_hp, opponent_str_energy = self._get_clause_eng_hp("opponent")
        my_state_clause = self._get_clause_my_state() 
        opponent_state_clause, opponent_total_states_clause = self._get_clause_count_state("opponent")
        my_curr_pos = self._get_clause_curr_pos("me")
        opponent_curr_pos = self._get_clause_curr_pos("opponent")
        opp_action_type = self._get_clause_opp_action_type()
        my_facing_dir = self._get_clause_facing_dir("me")
        opponent_facing_dir = self._get_clause_facing_dir("opponent")
        my_prev_action = self._get_clause_my_prev_action()
        # my_prev_action_type = self._get_clause_prev_action("me")
        # opponent_prev_action_type = self._get_clause_prev_action("opponent")
        
        # my_hbox = self._get_hbox_clause("me")
        # opponent_hbox = self._get_hbox_clause("opponent")

        
        concat_str = "\n".join([
            my_str_hp, my_str_energy, my_state_clause,
            my_curr_pos, my_facing_dir, opponent_facing_dir,
            opp_action_type, my_prev_action, #
            # my_hbox,  my_prev_hp, my_prev_energy,
            
        ])
        for statement in PrologString(concat_str):
            db += statement

        concat_str = "\n".join([
            opponent_str_hp, opponent_str_energy, opponent_state_clause, opponent_total_states_clause, 
            opponent_curr_pos,
            # opponent_hbox,  opponent_prev_hp, opponent_prev_energy,  opponent_prev_action_type,
        ])
        for statement in PrologString(concat_str):
            db += statement
    
            
        return db
        
    
   

    def _increment_counter(self, agent: str, state: str) -> None:
        self.counters[agent][state] += 1
        self.counters[agent]['total'] += 1


    def estimate_opponent_action(self):
        action_type = actions_type.get(self.opponent_character_data.action.value.upper(), "attack")

        return action_type
        

    def round_end(self, round_result: RoundResult):
        self._init_vars()
        mean_time = np.mean(self.time_taken)
        self.echo(f"Mean time taken: {mean_time}")
        # logger.info(f"round end: {round_result}")

    def get_screen_data(self, screen_data: ScreenData):
        if self.plot_scenes and hasattr(self, 'display_thread') and screen_data.display_bytes:
            try:
                if not screen_data or not screen_data.display_bytes:
                    logger.debug("No display bytes available")
                    return
                if self.display_thread.queue.full():
                    return
                self.display_thread.queue.put_nowait(screen_data.display_bytes)
                
            except queue.Full:
                pass
            except Exception as e:
                logger.error(f"Error queueing screen data: {e}")
            
        self.screen_data_raw = screen_data

    def _init_plots(self):
        if self.plot_scenes:
            self.display_thread = DisplayThread(self.width, self.height)
            self.display_thread.start()


    def game_end(self):
        pass
    def close(self):
        logger.info("Closing ProblogAgent")
        if hasattr(self, 'display_thread'):
            self.display_thread.stop()
            self.display_thread.join()
