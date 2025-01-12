
from typing import Tuple
from problog.extern import problog_export
import numpy as np
import random
from problog.logic import Term



move_actions = [
    Term("dash"), Term("back_step"), Term("for_jump"), 
    Term("back_jump"), Term("forward_walk"), Term("crouch")]

defensive_actions = [Term("stand_guard"), Term("crouch_guard"), Term("air_guard")]
probabilities_move = [
    0.25, 0.15, 0.25, 0.15, 0.05, 0.15
]
probabilities_defensive = [
    0.4, 0.4, 0.2
]
arial_moves_actions = [Term("for_jump"), Term("back_jump")]
probabilities_air_moves = [
    0.95, 0.05
]
forward_actions = [Term("dash"), Term("for_jump"), Term("forward_walk")]
probabilities_forward = [0.35, 0.35, 0.3]

backward_actions = [Term("back_step"), Term("back_jump")]
probabilities_backward = [0.4, 0.6]

non_attack_actions = move_actions + defensive_actions
probabilities_non_attack = [0.2, 0.15, 0.15, 0.05, 0.1,0.15, 0.1, 0.05, 0.05]

attack_s_actions = [
    Term("stand_d_df_fc"), Term("stand_f_d_dfb"), Term("stand_d_db_bb"), Term("air_d_db_ba")
]


attack_bs_actions = [
    Term("stand_fa"), Term("stand_fb"), Term("crouch_fb"), Term("crouch_fa"), Term("stand_a"), Term("stand_b"), Term("stand_f_d_dfa")
]

total_bs_damage = 8 + 10 + 12 + 12 + 8 + 5 + 10 + 10
attack_ba_actions = [
    Term("air_fb"), Term("air_db"), Term("air_b"), Term("air_da")
]
total_ba_damage = 10  + 10 + 10 + 5
 
attack_b_actions = attack_bs_actions + attack_ba_actions
total_b_damage = total_bs_damage + total_ba_damage

damage_amounts = {
    Term("stand_d_df_fc"): 120,
    Term("stand_f_d_dfb"): 40,
    Term("stand_d_db_bb"): 25,
    Term("air_d_db_ba"): 10,
    Term("stand_fa"): 8,
    Term("air_fb"): 10,
    Term("stand_fb"): 12,
    Term("crouch_fb"): 12,
    Term("stand_a"): 5,
    Term("stand_b"): 10,
    Term("stand_f_d_dfa"): 10,
    Term("air_f_d_dfa"): 10,
    Term("crouch_fa"): 8,
    Term("air_db"): 10,
    Term("air_b"): 10,
    Term("air_da"): 5
}

total_damage_s = 120 + 40 + 10 + 25 + 10
total_damage_b = 8 + 10 + 12 + 12 + 5 + 10 + 10 + 10 + 8

energy_costs = {
    Term("stand_d_df_fc"): 150,
    Term("stand_f_d_dfb"): 55,
    Term("stand_d_db_bb"): 50,
    Term("air_d_db_ba"): 5
}

move_ranges = {
    Term("stand_d_df_fc"): {'max': 1000, 'min': 0},
    Term("crouch_fb"): {'max': 200, 'min': 0},
    Term("stand_fb"): {'max': 237, 'min': 75},
    Term("air_fb"): {'max': 150, 'min': 0},
    Term("stand_fa"): {'max': 150, 'min': 0},
    Term("crouch_fa"): {'max': 150, 'min': 0},
    Term("stand_a"): {'max': 100, 'min': 0},
    Term("air_d_df_fa"): {'max': 550, 'min': 10},
    Term("stand_f_d_dfa"): {'max': 150, 'min': 0},
    Term("stand_f_d_dfb"): {'max': 135, 'min': 0},
    Term("stand_d_db_bb"): {'max': 370, 'min': 0},
    Term("air_d_db_ba"): {'max': 100, 'min': 0},
    Term("stand_b"): {'max': 150, 'min': 10},
    Term("air_f_d_dfa"): {'max': 150, 'min': 0},
    Term("air_db"): {'max': 150, 'min': 10},
    Term("air_b"): {'max': 150, 'min': 10},
    Term("air_da"): {'max': 100, 'min': 0}
}

ENERGY_BEST_SPECIAL = 150
EPSILON_PROB = 0.85 # Probability of not taking a special move (epsilon-greedy)
AGGRESSIVE_PROB = 0.76 # Probability of taking an aggressive move




def can_hit(action, my_x:int, op_x:int, my_y:int, op_y:int, max_dist:int, min_dist:int) -> Tuple[int, int]:
    
    distance = np.abs(my_x - op_x)
    if distance > max_dist or distance < min_dist:
        return 0
    return 1


def compute_helper(actions_to_check, my_x:int, op_x:int, my_y:int, op_y:int, total_damage:int, move_ranges: dict) -> Tuple[int, int]:
    actions = []
    probabilities = []

    for action in actions_to_check:
    
        hit = can_hit(action, my_x, op_x, my_y, op_y, move_ranges[action]['max'], move_ranges[action]['min'])
        if hit:
            if action == Term("stand_d_df_fc"):
                return [action], [1]
            actions.append(action)
            damage = damage_amounts[action]/total_damage
            probabilities.append(damage)
    
    return actions, probabilities

@problog_export(
        '+int', '+int', '+int', 
        '+int', '+int', '+int', '+int', '+str', '+str', '-list'
    )
def possible_actions(
        my_x:int, op_x:int, my_y:int, op_y:int, 
        facing_opposite:int, my_curr_energy: int,
        opponent_curr_energy: int,
        opponent_action_type: str, my_prev_action: str
    ) -> list[Term]:
    """Get the possible actions for the current state
    Args:
        my_x: x-coordinate of the player
        op_x: x-coordinate of the opponent
        my_y: y-coordinate of the player
        op_y: y-coordinate of the opponent
        facing_opposite: 1 if the player is facing the opponent, 0 otherwise
        my_curr_energy: current energy of the player
        opponent_curr_energy: current energy of the opponent
        opponent_action_type: the type of action the opponent is taking
        my_prev_action: the previous action taken by the player
    Returns:
        list[Term]: the possible actions for the current state
    """
    actions = []
    if opponent_action_type == "special":
        actions.extend(arial_moves_actions)
        probabilities = probabilities_air_moves
    else:
        if opponent_curr_energy >= ENERGY_BEST_SPECIAL:
            return [Term("for_jump")], [1]
        if (my_curr_energy > 4 and 
                (random.random() > EPSILON_PROB or my_curr_energy >= ENERGY_BEST_SPECIAL) and 
                facing_opposite == 1
            ):
            for s_action in attack_s_actions:
                if energy_costs.get(s_action) <= my_curr_energy:
                   actions.append(s_action)
                        
            actions, probabilities = compute_helper(actions, my_x, op_x, my_y, op_y, total_damage_s, move_ranges)
        elif (not opponent_action_type == "attack" or random.random() > AGGRESSIVE_PROB):
            if my_y > 0:
                actions, probabilities = compute_helper(attack_ba_actions, my_x, op_x, my_y, op_y, total_ba_damage, move_ranges)
            else:
                actions, probabilities = compute_helper(attack_b_actions, my_x, op_x, my_y, op_y, total_b_damage, move_ranges)
            
        else:
            actions.extend(defensive_actions)
            probabilities = probabilities_defensive
        
        
        if len(actions) == 0:
            prob = np.random.random()
            if opponent_action_type != "special" and prob >  AGGRESSIVE_PROB:
                actions.extend(forward_actions)
                probabilities = probabilities_forward
            elif opponent_action_type != "special" and prob < AGGRESSIVE_PROB:
                actions.extend(defensive_actions)
                probabilities = probabilities_defensive
            elif opponent_action_type == "special":
                actions.extend(arial_moves_actions)
                probabilities = probabilities_air_moves

        else:
            sum = np.sum(probabilities)
            len_actions = len(actions)
            adder = (1 - sum) / len_actions
            probabilities = [p + adder for p in probabilities]
    actions = np.array(actions)
    probabilities = np.array(probabilities)
    index = np.where(actions == Term(my_prev_action))[0]
    np.delete(actions, index)
    np.delete(probabilities, index)

    return np.random.choice(actions, p=probabilities, size=2)
    