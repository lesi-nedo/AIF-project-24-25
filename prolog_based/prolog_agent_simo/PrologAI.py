import logging
import random
import numpy as np

from utility import Utility
from pyswip import Prolog
from pyftg import (AIInterface, AudioData, CommandCenter, FrameData, GameData,
                   Key, RoundResult, ScreenData)

from pyftg.models.attack_data import AttackData
from pyftg.models.base_model import BaseModel
from pyftg.models.character_data import CharacterData

logger = logging.getLogger(__name__)
logger.propagate = True

martial = ["STAND_B", "CROUCH_A", "CROUCH_B", "STAND_FB", "STAND_FA", "AIR _FA", "AIR _FB", "AIR _DB"]
map_names = {"stand_medium_punch" : "STAND_A", "stand_medium_kick" : "STAND_B", "fireball" : "STAND_D_DF_FA", "crouch_medium_punch": "CROUCH_A", "crouch_heavy_punch" : "CROUCH_B", "crouch_medium_kick" : "CROUCH_FA", "evade": "BACK_JUMP", "wait" : "FORWARD_WALK", "defend" : "STAND_GUARD", "ultra" : "STAND_D_DF_FC"}
class KB():
    def __init__(self):
        self.kb = Prolog()
    def query(self, q):
        return self.kb.query(q)
    def retract_frame_info(self):
        # Supporting Data Predicates
        self.kb.retractall("character_attack(_, _)")
        self.kb.retractall("character_speed(_, _, _)")
        self.kb.retractall("knocself.kback(_, _, _)")
        self.kb.retractall("character_xyd(_, _, _, _)")
        self.kb.retractall("character_box(_, _, _)")
        self.kb.retractall("hp_threshold(_, _)")
        self.kb.retractall("character_hp_energy(_, _, _)")
        self.kb.retractall("character_state(_, _)")
        self.kb.retractall("hit_area(_, _, _, _, _)")
        self.kb.retractall("knockback(_, _, _)")
        self.kb.retractall("hit_conferm(_, _)")
        self.kb.retractall("character_action(_, _)")

    def update_every_round(self, Player: CharacterData, type: str, knock_x, knock_y, h_conferm):
        [b1,b2] = Utility.get_player_width_height(Player)
        facing = -1
        hit_conferm = 0 if h_conferm == False else 1
        if Player.front:
            facing = 1
        #logger.info("character_state("+"player"+type+", "+str(Player.state._value_)+")")
        #logger.info("character_action("+"player"+type+", "+str(Player.action.value)+")")
        #logger.info("character_xyd("+"player"+type+", "+str(Player.x) +", "+ str(Player.y) +"," + str(facing) + ")")
        #logger.info("character_speed("+"player"+type+", "+str(Player.speed_x)+ ", " + str(Player.speed_y) + ")")
        #logger.info("hit_area("+"player"+type+", "+str(Player.attack_data.current_hit_area.left)+ ", " + str(Player.attack_data.current_hit_area.right) + ", " + str(Player.attack_data.current_hit_area.top) + ", " + str(Player.attack_data.current_hit_area.bottom) + ")")
        #logger.info("character_attack("+"player"+type+", "+str(Player.attack_data.start_up)+ ", " + str(Player.attack_data.is_live).lower() + ", " + str(Player.attack_data.speed_x) + ", " + str(Player.attack_data.speed_y) +", " + str(Player.attack_data.is_projectile).lower() + ")")
        #logger.info("knockback" + "(" + "player"+type+", "+ str(knock_x)+ ", " + str(knock_y) +")")
        self.kb.asserta("character_hp_energy("+"player"+type+", "+str(Player.hp)+ ", " + str(Player.energy)+ ")")
        self.kb.asserta("character_state("+"player"+type+", "+str(Player.state._value_)+")")
        self.kb.asserta("character_action("+"player"+type+", "+str(Player.action.value)+")")
        self.kb.asserta("character_xyd("+"player"+type+", "+str(Player.x) +", "+ str(Player.y) +", " + str(facing) + ")")
        self.kb.asserta("character_speed("+"player"+type+", "+str(Player.speed_x)+ ", " + str(Player.speed_y) + ")")
        self.kb.asserta("hit_area("+"player"+type+", "+str(Player.attack_data.current_hit_area.left)+ ", " + str(Player.attack_data.current_hit_area.right) + ", " + str(Player.attack_data.current_hit_area.top) + ", " + str(Player.attack_data.current_hit_area.bottom) + ")")
        self.kb.asserta("character_attack("+"player"+type+", "+str(Player.attack_data.attack_type)+ ")")
        self.kb.asserta("knockback" + "(" + "player"+type+", "+ str(knock_x)+ ", " + str(knock_y) +")")
        self.kb.asserta("character_box("+"player"+type+", "+str(b1)+ ", " + str(b2) + ")")
        self.kb.asserta("hit_conferm("+"player"+type+", "+str(hit_conferm)+")")
    
    def close(self):
        self.kb.close()


Kb = KB()
Kb.kb.consult("kb.pl")

class PrologAI(AIInterface):
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
        Kb.retract_frame_info()
        Kb.update_every_round(self.mycharacter_data,"1",self.othercharacter_data.attack_data.impact_x,self.othercharacter_data.attack_data.impact_y,self.othercharacter_data.hit_confirm)
        Kb.update_every_round(self.othercharacter_data,"2",self.mycharacter_data.attack_data.impact_x,self.mycharacter_data.attack_data.impact_y,self.mycharacter_data.hit_confirm)
        if self.cc.get_skill_flag():
            self.key = self.cc.get_skill_key()
        else:
            self.key.empty()
            self.cc.skill_cancel()
            action = map_names["wait"]
            resolve = list(Kb.query("optimal_action(player1, player2, Action)"))
            if resolve:
                #print(resolve)
                action = map_names[resolve[0]["Action"]]
                if action == "STAND_A":
                    # Chance of doing martial change
                    chance = random.randint(0,10)
                    if chance >= 3: # ~66% (non uniformed, so i don't think this is the case)
                        x = random.randint(0, len(martial)-1)
                        action = martial[x]
            self.cc.command_call(action)
            #print(action)
        #resolve = list(Kb.query("profile(optimal_action(Player1, Player2, Action))"))
        #print(resolve)        
    
    def round_end(self, round_result: RoundResult):
        logger.info(f"round end: {round_result}")

    def game_end(self):
        logger.info("game end")
        
    def close(self):
        Kb.close()
    