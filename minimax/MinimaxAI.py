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

logger = logging.getLogger(__name__)

class MinimaxAI(AIInterface):
    def __init__(self, depth=3):
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
        self.cc = CommandCenter()
        self.key = Key()
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
        self.mycharacter_data = self.frame_data.get_character(self.player)
        self.othercharacter_data = self.frame_data.get_character(self.otherplayer)

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
        """
        Funzione principale di elaborazione dell'agente. Viene chiamata ogni frame.
        """
        if self.frame_data is not None and self.frame_data.current_frame > 0:
            if self.cc.getskill_flag():
                self.key = self.cc.command_call()
                return

            # Calcolo della mossa ottimale tramite Minimax
            logger.info("Calculating optimal move using Minimax with alpha-beta pruning...")
            best_move = self.minimax_decision(self.frame_data, self.depth, -math.inf, math.inf, True)
            if best_move:
                logger.info(f"Executing move: {best_move}")
                self.cc.command_call(best_move)

    def minimax_decision(self, state, depth, alpha, beta, maximizing_player):
        """
        Implementazione del Minimax con potatura Alpha-Beta.
        """
        if depth == 0 or self.is_terminal(state):
            return self.evaluate(state)

        if maximizing_player:
            max_eval = -math.inf
            best_action = None
            for action in self.get_possible_actions(state):
                new_state = self.simulate_action(state, action)
                eval = self.minimax_decision(new_state, depth - 1, alpha, beta, False)
                if eval > max_eval:
                    max_eval = eval
                    best_action = action
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return best_action if depth == self.depth else max_eval
        else:
            min_eval = math.inf
            for action in self.get_possible_actions(state):
                new_state = self.simulate_action(state, action)
                eval = self.minimax_decision(new_state, depth - 1, alpha, beta, True)
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval

    def get_possible_actions(self, state):
        """
        Restituisce una lista delle mosse possibili a partire dallo stato attuale.
        """
        return ["STAND", "FOR_JUMP", "DASH", "CROUCH", "STAND_D_DB_BA", "THROW_A", "THROW_B", "BACK_STEP"]

    def simulate_action(self, state, action):
        """
        Simula lo stato risultante dopo aver eseguito un'azione.
        """
        new_state = state.copy()  # Simula una copia dello stato
        new_state.player[self.player].execute_action(action)
        return new_state

    def evaluate(self, state):
        """
        Funzione di valutazione che assegna un punteggio allo stato in base al vantaggio.
        """
        my_hp = state.player[self.player].hp
        opponent_hp = state.player[self.otherplayer].hp
        my_position = state.player[self.player].position.x
        opponent_position = state.player[self.otherplayer].position.x

        # Peso derivato dalla salute e dalla distanza dall'avversario
        return (my_hp - opponent_hp) + (abs(my_position - opponent_position) * -0.1)

    def is_terminal(self, state):
        """
        Verifica se lo stato è terminale (partita finita).
        """
        return state.player[self.player].hp <= 0 or state.player[self.otherplayer].hp <= 0
