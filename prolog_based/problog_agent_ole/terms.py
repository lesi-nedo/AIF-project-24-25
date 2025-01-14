
from typing import Tuple
from problog.extern import problog_export
import numpy as np
import random
from problog.logic import Term
from problog.logic import term2str
from operator import add
from numpy.random import Generator as np_generator
rng = np.random.default_rng()

move_actions = [
    Term("dash"), Term("back_step"), Term("for_jump"), 
    Term("back_jump"), Term("forward_walk"), Term("crouch")]

defensive_actions = [Term("stand_guard"), Term("crouch_guard"), Term("air_guard")]
probabilities_move = [
    0.3, 0.18, 0.19, 0.15, 0.05, 0.13
]
probabilities_defensive = [
    0.4, 0.4, 0.2
]
arial_moves_actions = [Term("for_jump"), Term("back_jump")]
probabilities_air_moves = [
    0.95, 0.05
]
forward_actions = [Term("dash"), Term("for_jump"), Term("forward_walk")]
probabilities_forward = [0.2, 0.65, 0.15]

backward_actions = [Term("back_step"), Term("back_jump")]
probabilities_backward = [0.4, 0.6]

non_attack_actions = move_actions + defensive_actions
probabilities_non_attack = [0.2, 0.15, 0.15, 0.05, 0.1,0.15, 0.1, 0.05, 0.05]

attack_s_actions = [
    Term("stand_d_df_fc"), Term("stand_d_db_bb"), Term("air_d_db_ba"),  Term("stand_d_df_fa")
]


attack_bs_actions = [
    Term("stand_fa"), Term("stand_fb"), Term("crouch_fb"), Term("crouch_fa"), Term("stand_a"), Term("stand_b"), Term("stand_f_d_dfa")
]

air_attack_actions = [
    Term("air_fb"), Term("air_db"), Term("air_b"), Term("air_da")
]

total_air_damage = 10 + 10 + 10 + 5

stand_attack_actions = [
    Term("stand_b"), Term("stand_f_d_dfa"),
]

total_stand_damage = 5 + 10 + 10

long_attack_actions = [
    Term("stand_fb"), Term("crouch_fb"), Term("air_db")
]

total_long_damage = 12 + 12 + 10

total_bs_damage = 8 + 12 + 12 + 8 + 5 + 10 + 10
attack_ba_actions = [
    Term("air_fb"), Term("air_db"), Term("air_b"), Term("air_da")
]
total_ba_damage = 10  + 10 + 10 + 5
 
attack_b_actions = attack_bs_actions + attack_ba_actions
total_b_damage = total_bs_damage + total_ba_damage

most_effective_actions = {}
most_effective_actions["total"] = 1

for action in attack_b_actions:
    most_effective_actions[action] = 0.0

damage_amounts = {
    Term("stand_d_df_fc"): 120,
    # Term("stand_f_d_dfb"): 40,
    Term("stand_d_db_bb"): 25,
    Term("air_d_db_ba"): 10,
    Term("stand_fa"): 8,
    Term("air_fb"): 10,
    Term("stand_fb"): 12,
    Term("crouch_fb"): 12,
    Term("stand_a"): 5,
    Term("stand_b"): 10,
    Term("stand_f_d_dfa"): 10,
    Term("crouch_fa"): 8,
    Term("air_db"): 10,
    Term("air_b"): 10,
    Term("air_da"): 5,
    Term("stand_d_df_fa"): 5
}

total_damage_s = 120  + 25 + 10 + 5

energy_costs = {
    Term("stand_d_df_fc"): 150,
    # Term("stand_f_d_dfb"): 55,
    Term("stand_d_db_bb"): 50,
    Term("air_d_db_ba"): 5,
    Term("stand_d_df_fa"): 5
}

move_ranges = {
    Term("stand_d_df_fc"): {'max': 1000, 'min': 0},
    Term("crouch_fb"): {'max': 200, 'min': 10},
    Term("stand_fb"): {'max': 210, 'min': 70},
    Term("air_fb"): {'max': 130, 'min': 20},
    Term("stand_fa"): {'max': 130, 'min': 0},
    Term("crouch_fa"): {'max': 130, 'min': 0},
    Term("stand_a"): {'max': 90, 'min': 0},
    Term("air_d_df_fa"): {'max': 500, 'min': 10},
    Term("stand_f_d_dfa"): {'max': 90, 'min': 0},
    # Term("stand_f_d_dfb"): {'max': 65, 'min': 0},
    Term("stand_d_db_bb"): {'max': 300, 'min': 0},
    Term("air_d_db_ba"): {'max': 100, 'min': 0},
    Term("stand_b"): {'max': 120, 'min': 10},
    Term("air_db"): {'max': 120, 'min': 10},
    Term("air_b"): {'max': 120, 'min': 10},
    Term("air_da"): {'max': 100, 'min': 0},
    Term("stand_d_df_fa"): {'max': 500, 'min': 10}
}

ENERGY_BEST_SPECIAL = 150
EPSILON_PROB = 0.85 # Probability of not taking a special move (epsilon-greedy)
AGGRESSIVE_PROB = 0.92 # Probability of taking an aggressive move
CAN_HIT_Y = 50
STAGE_WIDTH = 960
STAGE_HEIGHT = 640
WEIGHTS = {
    'distance': 0.25,
    'health': 0.25,
    'energy': 0.2,
    'position': 0.2,
    'height': 0.1,
    'stage_control': 0.15
}


counteractive_actions = {
    "stand_d_df_fa": ("air_d_db_ba", 1),
    "stand_f_d_dfb": ("back_step", 1),
    "stand_d_db_bb": ("for_jump",1),
    "stand_fa":  ("stand_d_df_fa", 1),
    "crouch_fb": ("for_jump", 1),
    "crouch_fa": ("crouch_fb",1),
    "stand_a": ("crouch_fb",1),
    "stand_a": ("stand_d_df_fa",1),
    "stand_f_d_dfa": ("for_jump",1),
}
counteractive_actions['total'] = 1



def can_hit(action, my_x:int, op_x:int, my_y:int, op_y:int, max_dist:int, min_dist:int) -> Tuple[int, int]:
    
    distance_x = np.abs(my_x - op_x)
    distance_y = np.abs(my_y - op_y)
    if action == 'air_d_db_ba' and distance_y > CAN_HIT_Y:
        return 0
    if distance_x > max_dist or distance_x < min_dist:
        return 0
    if distance_y > CAN_HIT_Y:
        return 0
    return 1


def compute_helper(actions_to_check, my_x:int, op_x:int, my_y:int, op_y:int, total_damage:int, move_ranges: dict) -> Tuple[int, int]:
    actions = []
    probabilities = []

    for action in actions_to_check:
    
        hit = can_hit(action, my_x, op_x, my_y, op_y, move_ranges[action]['max'], move_ranges[action]['min'])
        if hit:
            actions.append(action)
            damage = damage_amounts[action]/total_damage
            probabilities.append(damage)
    
        
    
    return actions, probabilities

def evaluate_state(my_x: int, op_x: int, my_y: int, op_y: int, 
                  my_health: int, op_health: int, my_energy: int, 
                  distance: int) -> float:
    """Evaluate current battle state with improved metrics"""
    score = 0.0
    
    optimal_range = 200
    distance_score = 1.0 / (1.0 + abs(distance - optimal_range) / 200)
    score += distance_score * WEIGHTS['distance']
    
    # Health advantage with non-linear scaling
    health_diff = my_health - op_health
    health_score = 2.0 / (1.0 + np.exp(-health_diff / 50)) - 1.0
    score += health_score * WEIGHTS['health']
    
    # Energy evaluation
    energy_ratio = my_energy / ENERGY_BEST_SPECIAL
    energy_score = np.sqrt(min(energy_ratio, 1.0))
    score += energy_score * WEIGHTS['energy']
    
    # Advanced position evaluation considering both players
    corner_distance = min(op_x, STAGE_WIDTH - op_x)
    position_score = 1.0 - (corner_distance / (STAGE_WIDTH / 2))
    if corner_distance < 100:
        position_score *= 1.5  # Corner trap bonus
    score += position_score * WEIGHTS['position']
    
    # Height advantage
    height_diff = op_y - my_y
    height_score = min(max(height_diff / 100, -1), 1)
    score += height_score * WEIGHTS['height']
    
    # Stage control evaluation
    center_x = STAGE_WIDTH / 2
    my_center_distance = abs(my_x - center_x)
    stage_control_score = 1.0 - (my_center_distance / (STAGE_WIDTH / 2))
    
    # Space behind evaluation
    space_behind = my_x if op_x > my_x else STAGE_WIDTH - my_x
    space_factor = min(space_behind / 200, 1.0)
    stage_control_score *= (1.0 + space_factor)
    
    score += stage_control_score * WEIGHTS['stage_control']
    
    return max(min(score, 1.0), 0.0)


def get_action_weights(actions: list, state_score: float, base_weights: list,
                      opponent_action_type: str) -> list:
    """Calculate action weights based on state evaluation"""
    base_weights = base_weights.copy()

    for indx, action in enumerate(actions):
        weight = 1.0
        
        # Defensive adjustments
        if opponent_action_type == "attack":
            if action in defensive_actions:
                weight *= (2.0 - state_score)  # Defend more when disadvantaged
                
        # Offensive adjustments
        if action in attack_s_actions:
            weight *= state_score * 1.5  # More aggressive when advantaged
            
        # Movement adjustments
        if action in move_actions:
            if state_score < 0.4:  # Defensive movement when disadvantaged
                weight *= 1.5
                
        base_weights[indx] += weight
   
    return base_weights

def get_one_foreach_random_action() -> list:
    rand_b_action = rng.choice(attack_b_actions, size=1, replace=False)
    random_d_action = rng.choice(defensive_actions, size=1, replace=False)
    random_m_action = rng.choice(move_actions, size=1, replace=False)
    actions_ = np.concatenate([rand_b_action, random_d_action, random_m_action])
    
    return actions_.tolist()
@problog_export(
        '+int', '+int', '+int', '+int', '+int', '+int', '+int', '+int', '+int',
        '+int', '+int',  '+int', '+str', '+str', '+str', '+str', '+list',  '-list'
    )
def possible_actions(
        my_x:int, op_x:int, my_y:int, op_y:int, my_health: int, my_prev_health:int, opp_health:int, opp_prev_health:int,
        my_curr_energy: int, my_prev_energy:int,
        opponent_curr_energy: int, opponent_prev_energy: int, 
        opponent_action_type: str, opponent_prev_action: str, my_prev_action: str, my_prev_action_type: str,  most_opponent_actions: list
    ) -> list[Term]:
    
    distance_x = np.abs(my_x - op_x)
    distance_y = np.abs(my_y - op_y)
    # print(f"Most opponent actions: {most_opponent_actions}", flush=True)
    score = evaluate_state(my_x, op_x, my_y, op_y, my_health, opp_health, my_curr_energy, distance_x)
    actions = []
    weights = []
    if (opponent_curr_energy >= ENERGY_BEST_SPECIAL - 2):
            return [Term("for_jump")]
    
    if my_curr_energy >= ENERGY_BEST_SPECIAL and distance_y < CAN_HIT_Y:
            return [Term("stand_d_df_fc")]
    
    if opponent_action_type == "attack" or opponent_action_type == "special":
        if ((my_health == my_prev_health and my_curr_energy == my_prev_energy) or 
            (opp_health <= opp_prev_health and opponent_curr_energy < opponent_prev_energy)):
            action_key = counteractive_actions.get(opponent_prev_action, (my_prev_action, 0))
            action_key  = (action_key[0], action_key[1] + 1)
            counteractive_actions.update({opponent_prev_action: action_key})
            counteractive_actions["total"] += 1
            
    
    if my_prev_action_type == "special" or my_prev_action_type == "attack":
        bonus = 0
        if my_curr_energy > my_prev_energy:
            bonus += 1
        if my_health == my_prev_health:
            bonus += 1
        if opp_health < opp_prev_health:
            bonus += 2
        most_effective_actions[Term(my_prev_action)] += bonus
        most_effective_actions["total"] += bonus
    
    if ((opponent_action_type == "special" and opponent_curr_energy > 10) or opponent_curr_energy < opponent_prev_energy):
        actions.extend(arial_moves_actions)
        weights.extend(get_action_weights(arial_moves_actions, score, probabilities_air_moves, opponent_action_type))
    else:

        for most_prob_opp_action in most_opponent_actions:
            if isinstance(most_prob_opp_action, Term):
                most_prob_opp_action = term2str(most_prob_opp_action)
                action,prob = most_prob_opp_action.split("-")
                action = action.strip()
                prob = float(prob)
                if action in counteractive_actions:
                    action_key = counteractive_actions[action]
                    if action_key[1] > 0:
                        actions.append(Term(action))
                        weights.append(counteractive_actions[action][1] / counteractive_actions["total"])
                        continue
                    
        if len(actions) > 0 and (score < 0.5 or opponent_action_type == "attack"):
            probabilities = [w/sum(weights) for w in weights]
            action =  rng.choice(actions, p=probabilities, size=1, replace=False)
            return action
       
        if (my_curr_energy > 4 and 
                random.random() > EPSILON_PROB and distance_y < CAN_HIT_Y
            ):
            
            for s_action in attack_s_actions:
                if energy_costs.get(s_action) <= my_curr_energy:
                    local_actions, local_weights = compute_helper([s_action], my_x, op_x, my_y, op_y, total_damage_s, move_ranges)
                    local_weights = get_action_weights(local_actions, score, local_weights, opponent_action_type)
                    actions.extend(local_actions)
                    weights.extend(local_weights)

        
        if (not opponent_action_type == "attack" or random.random() > AGGRESSIVE_PROB):
            actions_local, base_weights = compute_helper(attack_b_actions, my_x, op_x, my_y, op_y, total_b_damage, move_ranges)
            performance_weights = [most_effective_actions[action] / most_effective_actions["total"] for action in attack_b_actions]
            base_weights = list(map(add, base_weights, performance_weights))
            weights.extend(get_action_weights(actions_local, score, base_weights, opponent_action_type))
            actions.extend(actions_local)
        else:
            
            actions.extend(non_attack_actions)
            weights.extend(get_action_weights(non_attack_actions, score, probabilities_non_attack, opponent_action_type))
        
        
        if len(actions) == 0 or score < 0.4:
            actions_ = None
            local_weights = None
            if score < 0.1:
                actions_ = defensive_actions
                local_weights = np.random.dirichlet(np.ones(len(defensive_actions)))
            elif distance_x > 140:
                
                actions_ = forward_actions + defensive_actions
                if my_y > CAN_HIT_Y:
                    probabilities_defensive[2] = 0.6
                else:
                    probabilities_defensive[1] = 0.6
                local_weights = probabilities_forward + probabilities_defensive
                if opponent_prev_action == "special" or opponent_prev_energy > opponent_curr_energy:
                    actions_ = defensive_actions
                    local_weights = [0.15, 0.8, 0.05]
                
            elif distance_x < 100 and score < 0.05:
                actions_ = backward_actions
                local_weights = probabilities_backward
            else:
                actions_ = long_attack_actions
                local_weights = []
                for action in long_attack_actions:
                    local_weights.append(most_effective_actions[action] / most_effective_actions["total"])

            actions.extend(actions_)
            weights.extend(get_action_weights(actions_, score, local_weights, opponent_action_type))
    weights_sum = sum(weights)
    probabilities = [w/weights_sum for w in weights]
    if len(actions) == 1:
        return actions
    return rng.choice(a=actions, p=probabilities, size=2, replace=False).tolist()
    