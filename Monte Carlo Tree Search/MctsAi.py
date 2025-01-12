import logging
import numpy as np
import inspect
import sys
import traceback

from pyftg import (AIInterface, AudioData, CommandCenter, FrameData, GameData,
                   Key, RoundResult, ScreenData)

from pyftg.models.attack_data import AttackData
from pyftg.models.base_model import BaseModel
from pyftg.models.character_data import CharacterData
from Utility import Utility
from mcts.searcher.mcts import MCTS
from FighterState import FighterState
import math
from mcts.searcher.mcts import TreeNode

logger = logging.getLogger(__name__)
logger.propagate = True


class MctsAi(AIInterface):
    def __init__(self):
        super().__init__()
        self.blind_flag = True

    def name(self) -> str:
        return self.__class__.__name__

    def is_blind(self) -> bool:
        return self.blind_flag

    def initialize(self, game_data: GameData, player_number: int):
        logger.info("initialize")
        self.game_data = game_data
        self.cc = CommandCenter()
        self.key = Key()
        self.player = player_number
        if self.player == 0:
            self.otherplayer = 1
        else:
            self.otherplayer = 0

    def get_non_delay_frame_data(self, frame_data: FrameData):
        self.frame_data = frame_data

    def input(self) -> Key:
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

    def processing(self):
        if self.frame_data.empty_flag or self.frame_data.current_frame_number <= 0:

            return
        if self.cc.get_skill_flag():
            self.key = self.cc.get_skill_key()
        else:
            self.key.empty()
            self.cc.skill_cancel()
            initial_state = FighterState(self.game_data, self.cc, self.mycharacter_data, self.othercharacter_data, self.player)
            # Ora inizializzo il searcher con tutti i parametri impostati (tempo limite; iterazioni massime; valore della costante c)
            searcher = MCTS(iteration_limit=10, explorationConstant=math.sqrt(2))
            try:
                best_action = searcher.search(initialState=initial_state)
                #self.cc.command_call(best_action)
                #logger.info("AZIONE MIGLIORE: "+str(best_action))
                self.cc.command_call(str(best_action.action_name).upper())
            except Exception as e:
                tb = sys.exc_info()[-1]
                stk = traceback.extract_tb(tb, 1)
                fname = stk[0][2]
                logger.warning(e)
            #self.cc.command_call(best_action)
    
    def round_end(self, round_result: RoundResult):
        logger.info(f"round end: {round_result}")

    def game_end(self):
        logger.info("game end")
        
    def close(self):
        pass