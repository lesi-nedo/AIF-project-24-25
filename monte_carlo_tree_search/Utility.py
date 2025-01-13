
import numpy as np

from pyftg.models.character_data import CharacterData
import logging
logger = logging.getLogger(__name__)
logger.propagate = True

frame_scale = 1 # I don't know
default_scaling_factor = 15 / frame_scale

class Utility():
    @staticmethod
    def get_actual_distance(Player1: CharacterData, Player2: CharacterData):
        [x1,y1] = [Player1.x - Player2.x, Player1.y - Player2.y]
        return np.linalg.norm([x1,y1])
    @staticmethod
    def predict_position(Player1: CharacterData, Player2: CharacterData | None = None) -> list[list[float]]:  # Matrix 2x2 in form [Player_k][x,y], [Player_j][x,y]
        p1_p2_final = [[None],[None]]
        [p1_vx, p1_vy] = [Player1.speed_x, Player1.speed_y]
        [p1_x, p1_y] = [Player1.x, Player1.y]
        [p1_f, p2_f] = [int(Player1.front), int(Player2.front) if Player2 else 0]
        p1_predicted_x_y = [p1_x + p1_vx * p1_f * default_scaling_factor, p1_y + p1_vy * p1_f * default_scaling_factor]
        p1_p2_final[0] = p1_predicted_x_y
        if Player2 != None:
            [p2_vx, p2_vy] = [Player2.speed_x, Player2.speed_y]
            [p2_x, p2_y] = [Player2.x, Player2.y]
            p2_predicted_x_y = [p2_x + p2_vx * p2_f * default_scaling_factor, p2_y + p2_vy * p2_f * default_scaling_factor]
            p1_p2_final[1] = p2_predicted_x_y
        return p1_p2_final
    @staticmethod
    def get_predicted_distance(Player1: CharacterData, Player2: CharacterData):
        pos = Utility.predict_position(Player1, Player2)
        dx = pos[0][0] - pos[1][0]
        dy = pos[0][1] - pos[1][1]
        return np.linalg.norm([dx, dy])
    @staticmethod
    def get_hp(Player1:CharacterData):
        return Player1.hp
    @staticmethod
    def get_player_width_height(Player: CharacterData):
        return [Player.right - Player.left, Player.bottom - Player.top] # Fixed box
    
    @staticmethod
    def was_attacking(Player: CharacterData):
        return Player.attack_data and not Player.attack_data.empty_flag
    
    @staticmethod    
    def predict_hitbox(Player1: CharacterData, Player2: CharacterData):
        p1_xy, p2_xy = Utility.predict_position(Player1, Player2)
        [W,H] = Utility.get_player_width_height(Player1)
        L_P1 = p1_xy[0]
        T_P1 = p1_xy[1]
        B_P1 = p1_xy[1] + H
        R_P1 = p1_xy[0] + W
        if Player2 != None:
                R_P2 = p2_xy[0] + W
                L_P2 = p2_xy[0]
                T_P2 = p2_xy[1]
                B_P2 = p2_xy[1] + H
                return [[L_P1, R_P1, T_P1, B_P1],[L_P2, R_P2, T_P2, B_P2]]
        else:
            return [[L_P1, R_P1, T_P1, B_P1], [None]]
    @staticmethod
    def hitbox_will_intersect(Player1: CharacterData, Player2: CharacterData):
        boxes = Utility.predict_hitbox(Player1, Player2)
        return boxes[0][1] > boxes[1][0] and boxes[0][0] < boxes[1][1] and boxes[0][3] > boxes[1][2] and boxes[0][2] < boxes[1][3]
    @staticmethod
    def action_was_colliding_myself_frames_ago(Opponent: CharacterData):
        return Opponent.hit_confirm