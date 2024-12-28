import logging
import math
from pyftg import AIInterface
from pyftg.aiinterface.command_center import CommandCenter
from pyftg.models.audio_data import AudioData
from pyftg.models.frame_data import FrameData
from pyftg.models.game_data import GameData
from pyftg.models.key import Key
from pyftg.models.round_result import RoundResult
from pyftg.models.screen_data import ScreenData
from pyftg.models.enums.action import Action

logger = logging.getLogger(__name__)
logger.propagate = True

class MinimaxAI(AIInterface):
    def __init__(self, depth=3):
        self.action = None
        self.otherplayer = None
        self.audio_data = None
        self.screen_data = None
        self.game_data = None
        self.blind_flag = True
        self.depth = depth
        self.cc = None
        self.key = None
        self.frame_data = None
        self.player = None

    def name(self) -> str:
        return self.__class__.__name__

    def initialize(self, game_data: GameData, player_number: bool):
        logger.info(f"Initializing for player {player_number}")
        self.game_data = game_data
        self.cc = CommandCenter()
        self.key = Key()
        self.frame_data = FrameData()
        self.player = player_number
        if self.player == 0:
            self.otherplayer = 1
        else:
            self.otherplayer = 0

    def get_non_delay_frame_data(self, frame_data: FrameData):
        self.frame_data = frame_data

    def input(self):
        return self.key

    def get_information(self, frame_data: FrameData, is_control: bool):
        self.frame_data = frame_data
        self.cc.set_frame_data(self.frame_data, self.player)

    def get_screen_data(self, screen_data: ScreenData):
        self.screen_data = screen_data

    def get_audio_data(self, audio_data: AudioData):
        self.audio_data = audio_data

    def close(self):
        logger.info("Closing MinimaxAI.")

    def game_end(self):
        logger.info("Game over")

    def is_blind(self):
        return self.blind_flag

    def round_end(self, round_result: RoundResult):
        logger.info(f"round end: {round_result}")

    def processing(self):
        if self.frame_data.empty_flag or self.frame_data.current_frame_number <= 0:
            return
        if self.cc.get_skill_flag():
            self.key = self.cc.get_skill_key()
            return
        else:
            best_move = self.minimax_decision(self.frame_data, self.depth, -math.inf, math.inf, True)
            if best_move:
                logger.info(f"Executing move: {best_move}")
                self.key.empty()
                self.cc.skill_cancel()
                self.cc.command_call(best_move)

    def minimax_decision(self, state, depth, alpha, beta, maximizing_player):
        if depth == 0 or self.is_terminal(state):
            return self.evaluate(state)

        if maximizing_player:
            max_eval = -math.inf
            best_action = None
            for action in Action:
                new_state = self.simulate_action(state, action)
                eval = self.minimax_decision(new_state, depth - 1, alpha, beta, False)
                if eval > max_eval:
                    max_eval = eval
                    best_action = action.name
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return best_action if depth == self.depth else max_eval
        else:
            min_eval = math.inf
            for action in Action:
                new_state = self.simulate_action(state, action)
                eval = self.minimax_decision(new_state, depth - 1, alpha, beta, True)
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval

    def simulate_action(self, state: FrameData, action) -> FrameData:
        # Creare una copia simulata di FrameData
        new_state = FrameData(
            character_data=state.character_data.copy(),
            current_frame_number=state.current_frame_number,
            current_round=state.current_round,
            projectile_data=state.projectile_data.copy(),
            empty_flag=state.empty_flag,
            front=state.front.copy(),
        )
        if action == Action.FORWARD_WALK:
             new_state.character_data[0].hp -= 5
        else:
             return state

        return new_state

    def evaluate(self, state: FrameData) -> float:
        my_character = state.get_character(self.player)
        opponent_character = state.get_character(self.otherplayer)
        if not my_character or not opponent_character:
            logger.warning("Dati dei personaggi non validi.")
            return -math.inf

        my_hp = my_character.hp
        opponent_hp = opponent_character.hp
        return my_hp - opponent_hp

    def is_terminal(self, state):
        my_character = state.get_character(self.player)
        opponent_character = state.get_character(self.otherplayer)
        return my_character.hp <= 0 or opponent_character.hp <= 0
