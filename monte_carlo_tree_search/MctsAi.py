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
from display_thread import DisplayThread
import queue


logger = logging.getLogger(__name__)
logger.propagate = True


class MctsAi(AIInterface):
    def __init__(self,exploration_constant: float, iteration_limit: int, plot_scenes: bool = False, width: int = 960, height: int = 640):
        super().__init__()
        self.blind_flag = True
        self.plot_scenes = plot_scenes
        self.exploration_constant = exploration_constant
        self.iteration_limit = iteration_limit
        self.width = width
        self.height = height
        if self.plot_scenes is True:
            self._init_plots()

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

        self.screen_data = screen_data

    def _init_plots(self):
        if self.plot_scenes:
            self.display_thread = DisplayThread(self.width, self.height)
            self.display_thread.start()

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
            searcher = MCTS(iteration_limit=self.iteration_limit, explorationConstant=self.exploration_constant)
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
        logger.info("Closing MonteCarlo Agent")
        if hasattr(self, 'display_thread'):
            self.display_thread.stop()
            self.display_thread.join()