from pyftg.aiinterface.command_center import CommandCenter
from pyftg.models.audio_data import AudioData
from pyftg.models.frame_data import FrameData
from pyftg.models.game_data import GameData
from pyftg.models.key import Key
from pyftg.models.round_result import RoundResult
from pyftg.models.screen_data import ScreenData
from pyftg.models.enums.action import Action

from collections import deque


class Simulator:
    def __init__(self, frame_data: FrameData, motion_list: (list, list), action_list: (list, list), player_number: bool):
        self.frame_data = frame_data
        self.motion_list = motion_list
        self.action_list = action_list
        self.player_number = player_number

        self.characters = self.frame_data.character_data.copy()
        self.proj = self.frame_data.projectile_data.copy()

    def processFight(self, currentFrame: int):
        self.processingCommands()
        self.processingHit(currentFrame)
        self.updateAttackParameters()
        self.updateCharacters()

    def processingCommands(self):

    def processingHit(self, currentFrame: int):

    def updateAttackParameters(self):

    def updateCharacters(self):





