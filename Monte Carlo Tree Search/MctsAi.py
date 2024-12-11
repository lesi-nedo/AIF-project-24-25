import logging
import numpy as np

from pyftg import (AIInterface, AudioData, CommandCenter, FrameData, GameData,
                   Key, RoundResult, ScreenData)

from pyftg.models.attack_data import AttackData
from pyftg.models.base_model import BaseModel
from pyftg.models.character_data import CharacterData

logger = logging.getLogger(__name__)
logger.propagate = True

class Utility():
    @classmethod
    def get_distance(Player1: CharacterData, Player2: CharacterData): # norm_2(pos1-pos2)
        [x1,y1] = [Player1.x - Player2.x, Player1.y - Player2.y]
        return np.linalg.norm([x1,y1])
    @classmethod
    def get_hp(Player1):
        return Player1.get_hp()
    @classmethod
    def get_player_width_height(Player: CharacterData):
        return [Player.right - Player.left, Player.bottom - Player.top]
    @classmethod
    def attack_in_range(Player1: CharacterData, Player2: CharacterData, Attack: AttackData):
        pass
    @classmethod
    def is_attacking(Player: CharacterData):
        return Player.attack_data and not Player.attack_data.empty_flag
    @classmethod
    def attack_will_collide(Attack: AttackData, Player: CharacterData):
        [w,h] = Utility.get_player_width_height(Player)
        [x,y] = [Player.x,Player.y]
        if Player.speed_x:
            x = x * Player.speed_x
        if Player.speed_y:
            y = y * Player.speed_y
        hit_area = Attack.current_hit_area
        if hit_area.right > x and hit_area.left < x + w and hit_area.bottom > y and hit_area.top < y + h:
            return True
        return False
    @classmethod
    def action_is_colliding_myself(Opponent: CharacterData):
        return Opponent.hit_confirm


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
            self.cc.command_call("B")
    
    def round_end(self, round_result: RoundResult):
        logger.info(f"round end: {round_result}")

    def game_end(self):
        logger.info("game end")
        
    def close(self):
        pass