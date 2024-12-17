from mcts.base.base import BaseState, BaseAction
from Utility import Utility
from pyftg import (CommandCenter, GameData)
from pyftg.models.character_data import CharacterData
import logging
from pyftg.models.enums.action import Action as Act

from copy import deepcopy, copy

logger = logging.getLogger(__name__)
logger.propagate = True

    
class Action(BaseAction):
        def __init__(self, action_name):
            self.action_name = action_name

        def __str__(self):
            return str((self.action_name))

        def __repr__(self):
            return str(self)

        def __eq__(self, other):
            return self.__class__ == other.__class__ and self.action_name == other.action_name

        def __hash__(self):
            return hash((self.action_name))


def extract_attack_info(name: str):
            match name.upper():
                case "FORWARD_WALK":
                    return 0,0,5,0,0
                case "DASH":
                    return 0,0,10,0,0
                case "BACK_STEP":
                    return 0,0,-15,0,0
                case "CROUCH":
                    return 0,0,0,0,0
                case "JUMP":
                    return 0,0,0,-24,0
                case "FOR_JUMP":
                    return 0,0,6,-22,0
                case "BACK_JUMP":
                    return 0,0,-6,-22,0
                case "STAND_GUARD":
                    return 0,0,0,0,0
                case "CROUCH_GUARD":
                    return 0,0,0,0,0
                case "AIR_GUARD":
                    return 0,0,0,0,0
                case "THROW_A":
                    return 10, -3, 5,0,10
                case "THROW_B":
                    return 20, -5, -5,0,20
                case "STAND_A":
                    return 5, 2, 0,0,5
                case "STAND_B":
                    return 10, 5, 0,0,10
                case "CROUCH_A":
                    return 5, 3, 0, 0,5
                case "CROUCH_B":
                    return 10, 5, 0, 0,10
                case "AIR_A":
                    return 8, 5, 0, 0,10
                case "AIR_B":
                    return 10, 10, 0, 0,20
                case "AIR_DA":
                    return 8, 8, 3, 10,10
                case "AIR_DB":
                    return 10,10, 2, 8,20
                case "STAND_FA":
                    return 8,4, 0, -10,5
                case "STAND_FB":
                    return 12,10,0,0,20
                case "CROUCH_FA":
                    return 8,4,0,0,5
                case "CROUCH_FB":
                    return 12,10,0,0,10
                case "AIR_FA":
                    return 10,5,0,0,10
                case "AIR_FB":
                    return 12,10,0,0,20
                case "AIR_UA":
                    return 10,8,0,0,10
                case "AIR_UB":
                    return 20,10,5,-2,20
                case "STAND_D_DF_FA":
                    return 5,-2,0,0,5
                case "STAND_D_DF_FB":
                    return 20,-20,0,0,20
                case "STAND_F_D_DFA":
                    return 10,5,0,-4,10
                case "STAND_F_D_DFB":
                    return 40,-55+20,0,0,30
                case "STAND_D_DB_BA":
                    return 10,5,10,-18,10
                case "STAND_D_DB_BB":
                    return 25,-50+15,20,0,30
                case "AIR_D_DF_FA":
                    return 10,-5+5,-2,0,5
                case "AIR_D_DF_FB":
                    return 30,-20+15,-5,-8,30
                case "AIR_F_D_DFA":
                    return 10,-10+5,8,-10,10
                case "AIR_F_D_DFB":
                    return 20,-40+15,10,-8,30
                case "AIR_D_DB_BA":
                    return 15,-10+5,10,-10,10
                case "AIR_D_DB_BB":
                    return 40,-50+15,10,-10,30
                case "STAND_D_DF_FC":
                    return 120, -150+30,-10,0,60

class FighterState(BaseState):
    def __init__(self, game_data: GameData, cc: CommandCenter, mycharacter_data: CharacterData, othercharacter_data: CharacterData, current_player: int):
        self.game_data = game_data
        self.cc = cc
        self.mycharacter_data = mycharacter_data
        self.othercharacter_data = othercharacter_data
        self.current_hp = [self.mycharacter_data.hp, self.othercharacter_data.hp]
        self.after_hp = [self.mycharacter_data.hp, self.othercharacter_data.hp]
        self.distance = Utility.get_actual_distance(self.mycharacter_data, self.othercharacter_data)
        self.current_energy = [self.mycharacter_data.energy, self.othercharacter_data.energy]
        self.after_energy = [self.mycharacter_data.energy, self.othercharacter_data.energy]
        self.ex = 0

        if current_player == 0:
            self.current_player = -1
        else:
            self.current_player = 1
        self.terminate = False
        
    def get_current_player(self) -> int:
        return self.current_player
        
    def get_possible_actions(self):
        possible_actions = [Action(Act.FORWARD_WALK._value_), Action(Act.DASH._value_), Action(Act.BACK_STEP._value_), Action(Act.CROUCH._value_), Action(Act.JUMP._value_),
                            Action(Act.FOR_JUMP._value_), Action(Act.BACK_JUMP._value_), Action(Act.STAND_GUARD._value_), Action(Act.CROUCH_GUARD._value_),
                            Action(Act.AIR_GUARD._value_), Action(Act.THROW_A._value_), Action(Act.THROW_B._value_), Action(Act.STAND_A._value_), Action(Act.STAND_B._value_),
                            Action(Act.CROUCH_A._value_), Action(Act.CROUCH_B._value_), Action(Act.AIR_A._value_), Action(Act.AIR_B._value_), Action(Act.AIR_DA._value_),
                            Action(Act.AIR_DB._value_), Action(Act.STAND_FA._value_), Action(Act.STAND_FB._value_), Action(Act.CROUCH_FA._value_),
                            Action(Act.CROUCH_FB._value_), Action(Act.AIR_FA._value_), Action(Act.AIR_FB._value_), Action(Act.AIR_UA._value_), Action(Act.AIR_UB._value_),
                            Action(Act.STAND_D_DF_FA._value_), Action(Act.STAND_D_DF_FB._value_), Action(Act.STAND_F_D_DFA._value_), Action(Act.STAND_F_D_DFB._value_),
                            Action(Act.STAND_D_DB_BA._value_), Action(Act.STAND_D_DB_BB._value_), Action(Act.AIR_D_DF_FA._value_), Action(Act.AIR_D_DF_FB._value_),
                            Action(Act.AIR_F_D_DFA._value_), Action(Act.AIR_F_D_DFB._value_), Action(Act.AIR_D_DB_BA._value_), Action(Act.AIR_D_DB_BB._value_),
                            Action(Act.STAND_D_DF_FC._value_)]

        return possible_actions
    

    def take_action(self, action):

        newState = deepcopy(self)
        newState.ex += 1
        attack_dmg, energy, vel_x, vel_y, given_energy = extract_attack_info(action.action_name)
        current_player = newState.current_player
        if current_player < 0:
            current_player = 0
        # aggiornare la x e la y dei due player e calcolare la distanza
        newState.mycharacter_data.speed_x = vel_x
        newState.mycharacter_data.speed_y = vel_y
        player_position = Utility.predict_position(newState.mycharacter_data, newState.othercharacter_data)[current_player]
        newState.mycharacter_data.x = player_position[0]
        newState.mycharacter_data.y = player_position[1]
        newState.distance = Utility.get_actual_distance(newState.mycharacter_data, newState.othercharacter_data)

        # se colpiti sottrarre la salute dei personaggi (dipende tutto dall'azione)

        if Utility.hitbox_will_intersect(newState.mycharacter_data, newState.othercharacter_data):
            newState.after_energy[current_player] = newState.after_energy[current_player] + energy
            newState.mycharacter_data.energy = newState.after_energy[current_player]

            newState.after_energy[1 - current_player] = newState.after_energy[1 - current_player] + given_energy
            newState.othercharacter_data.energy = newState.after_energy[1 - current_player]

            if newState.after_energy[current_player] > newState.game_data.max_energies[current_player]:
                newState.after_energy[current_player] = newState.game_data.max_energies[current_player]
                newState.mycharacter_data.energy = newState.game_data.max_energies[current_player]

            if newState.after_energy[1 - current_player] > newState.game_data.max_energies[1 - current_player]:
                newState.after_energy[1 - current_player] = newState.game_data.max_energies[1 - current_player]
                newState.othercharacter_data.energy = newState.game_data.max_energies[1 - current_player]

            newState.after_hp[1 - current_player] = newState.current_hp[1 - current_player] - attack_dmg
            newState.othercharacter_data.hp = newState.after_hp[1 - current_player]
        
        newState.mycharacter_data, newState.othercharacter_data = newState.othercharacter_data, newState.mycharacter_data
        newState.current_player = newState.current_player * -1
        logger.info(newState.after_hp)
        return newState

    def is_terminal(self):
        current_player = self.current_player
        if current_player < 0:
            current_player = 0
        if self.after_hp[1 - current_player] == 0 or self.after_hp[current_player] == 0:
            logger.info(self.ex)
            return True


    def get_reward(self) -> float:
        # effettuare il calcolo del reward
        logger.info(self.ex)
        current_player = self.current_player
        if current_player < 0:
            current_player = 0
        delta_energy = self.after_energy[current_player] - self.current_energy[current_player]
        energy_norm = delta_energy/self.game_data.max_energies[current_player]

        delta_hp_player = self.current_hp[current_player] - self.after_hp[current_player]
        hp_pl_norm = delta_hp_player/400

        delta_hp_opp = self.current_hp[1 - current_player] - self.after_hp[1 - current_player]
        hp_opp_norm = delta_hp_opp/400

        score = (1-energy_norm) * (hp_opp_norm - hp_pl_norm - self.distance) + (energy_norm) * (hp_opp_norm - hp_pl_norm + self.distance)
        logger.info("QUESTO È LO SCORE PER IL NODO CORRENTE: "+str(self.current_player))
        return score
    


    