
from typing import Tuple
from problog.extern import problog_export
import numpy as np
import random
from problog.logic import Term
from problog.logic import term2str
from operator import add
import pandas as pd
import os
from mappings import actions_type
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
attack_ba_actions = [
    Term("air_fb"), Term("air_db"), Term("air_b"), Term("air_da")
]



stand_attack_actions = [
    Term("stand_b"), Term("stand_f_d_dfa"),
]


long_attack_actions = [
    Term("stand_fb"), Term("crouch_fb"), Term("air_db")
]
probabilities_long = [0.3, 0.6, 0.1]


anti_air_actions = [
    Term("stand_f_d_dfa"), Term("air_b"), Term("air_da")
]

probabilities_anti_air = [0.6, 0.2, 0.2]


attack_b_actions = attack_bs_actions + attack_ba_actions

probabilities_attack_b = [
    0.1, 0.04, 0.23, 0.18, 0.04, 0.05, 0.06, 0.15, 0.01, 0.1, 0.04
]

most_effective_actions = {}
most_effective_actions["total"] = 1

for action in attack_b_actions:
    most_effective_actions[action] = 0.0

for action in attack_s_actions:
    most_effective_actions[action] = 0.0




ENERGY_BEST_SPECIAL = 150
EPSILON_PROB = 0.85 # Probability of not taking a special move (epsilon-greedy)
AGGRESSIVE_PROB = 0.92 # Probability of taking an aggressive move
MIN_AGGRESSIVE_PROB = 0.89
CAN_HIT_Y = 55
STAGE_WIDTH = 960
STAGE_HEIGHT = 640
MAX_CAN_HIT_X = 200
BEST_K_ATTACKS = 3
WEIGHTS = {
    'distance': 0.25,
    'health': 0.25,
    'energy': 0.2,
    'position': 0.2,
    'height': 0.1,
    'stage_control': 0.15
}


counteractive_actions = {
    Term("stand_d_df_fa"): (Term("air_d_db_ba"), 1),
    Term("stand_f_d_dfb"): (Term("back_step"), 1),
    Term("stand_d_db_bb"): (Term("for_jump"),1),
    Term("stand_fa"):  (Term("stand_d_df_fa"), 1),
    Term("crouch_fb"): (Term("for_jump"), 1),
    Term("crouch_fa"): (Term("crouch_fb"),1),
    Term("stand_a"): (Term("crouch_fb"),1),
    Term("stand_a"): (Term("stand_d_df_fa"),1),
    Term("stand_f_d_dfa"): (Term("for_jump"),1),
}
counteractive_actions['total'] = 1

current_dir = os.path.dirname(os.path.abspath(__file__))

# Load motion data
motion_data = pd.read_csv(
    os.path.join(current_dir, "Motion.csv"),
    sep=',',              # Explicit comma separator
    quotechar='"',        # Use double quotes for field quoting
    escapechar='\\',      # Use backslash as escape character
    na_values=[''],       # Handle empty fields
    encoding='utf-8'      # Specify encoding
)
motion_data.columns = motion_data.columns.str.strip()
motion_data['motionName'] = motion_data['motionName'].apply(lambda x: x.lower())
motion_data = motion_data.set_index('motionName')
damage_amounts = motion_data['attack.HitDamage'].to_dict()
damage_amounts['stand_fb'] = damage_amounts["stand_fb"] // 2
energy_costs = motion_data['attack.StartAddEnergy'].apply(lambda x: np.abs(x)).to_dict()

# Compute total damage for each type of attack
total_damage_s = sum([damage_amounts.get(str(action), 7) for action in attack_s_actions])
total_ba_damage = sum([damage_amounts.get(str(action), 7) for action in attack_ba_actions])

total_ba_damage = sum([damage_amounts.get(str(action), 7) for action in attack_ba_actions])
total_stand_damage = sum([damage_amounts.get(str(action), 7) for action in stand_attack_actions])
total_long_damage = sum([damage_amounts.get(str(action), 7) for action in long_attack_actions])
total_bs_damage = sum([damage_amounts.get(str(action), 7) for action in attack_bs_actions])
total_anti_air_damage = sum([damage_amounts.get(str(action), 7) for action in anti_air_actions])
total_damage_s = sum([damage_amounts.get(action, 7) for action in attack_s_actions])

total_b_damage = total_bs_damage + total_ba_damage

def get_attack_hit_areas(action:str, positions:dict[str,int], facing_dirs:dict[str,int], player:str) -> Tuple[int, int, int, int]:
    """
    Calculate the hit areas for a given attack action
    Args:
    action (str): The attack action
    positions (dict): The current positions of the players
    facing_dirs (dict): The facing directions of the players
    player (str): The player for which to calculate the hit areas
    Returns:
    Tuple[int, int, int, int]: The hit areas for the attack action
    """
    str_action = str(action)

    hit_area_left = positions[f"{player}_x"]
    hit_area_right = positions[f"{player}_x"]
    hit_area_up = positions[f"{player}_y"]
    hit_area_down = positions[f"{player}_y"]
    half_diff_up_down = np.abs(motion_data.loc[str_action, "attack.hitAreaUp"] - motion_data.loc[str_action, "attack.hitAreaDown"]) // 2
    half_diff_left_right = np.abs(motion_data.loc[str_action, "attack.hitAreaLeft"] - motion_data.loc[str_action, "attack.hitAreaRight"]) // 2
    hit_area_up = hit_area_up + half_diff_up_down
    hit_area_down = hit_area_down + half_diff_up_down

    if facing_dirs[f"{player}_facing_dir"] == 1:
        hit_area_left = hit_area_left + half_diff_left_right
        hit_area_right = hit_area_right + half_diff_left_right
        
    
    else:
        hit_area_left = hit_area_left  - half_diff_left_right
        hit_area_right = hit_area_right - half_diff_left_right
        
    
    return hit_area_left, hit_area_right, hit_area_up, hit_area_down


def can_hit(action, facing_dirs:dict, opponent_hbox:list[int], positions:dict[str,int]) -> Tuple[int, int]:
    """
    Check if the given action can hit the opponent
    Args:
    action (str): The action to check
    facing_dirs (dict): The facing directions of the players
    opponent_hbox (list): The hit box of the opponent
    positions (dict): The current positions of the players
    Returns:
    Tuple[int, int]: A tuple indicating if the action can hit the opponent in the x and y directions
    """
    my_hit_areas = get_attack_hit_areas(action, positions, facing_dirs, "my")
    variance_x = np.random.randint(1, 10)
    variance_y = np.random.randint(2, 8)

    hit_x = (my_hit_areas[0] - variance_x <= opponent_hbox[1] and  # my left < opp right
            my_hit_areas[1] + variance_x >= opponent_hbox[0])      # my right > opp left
            
    hit_y = (my_hit_areas[2] - variance_y <= opponent_hbox[3] and  # my top < opp bottom
            my_hit_areas[3] + variance_y >= opponent_hbox[2])      # my bottom > opp top

    return hit_x and hit_y
    

def compute_helper(
    actions_to_check, acing_dirs:dict, total_damage:int, 
    positions:dict[str, int], opponent_hbox:list[int], base_weights:list[float] = None) -> Tuple[int, int]:
    """
    Estimate the actions that can hit the opponent and their weights based on the damage dealt
    Args:
    actions_to_check (list): The actions to check
    facing_dirs (dict): The facing directions of the players
    total_damage (int): The total damage dealt by the actions
    positions (dict): The current positions of the players
    opponent_hbox (list): The hit box of the opponent
    base_weights (list): The base weights for the actions
    Returns:
    Tuple[int, int]: The actions that can hit the opponent and their weights
    """

    actions = []
    weights = []

    for indx,action in enumerate(actions_to_check):
        type_action = actions_type.get(str(action).upper(), "non_attack")
        if type_action == "non_attack" or type_action == "movement":
            
            actions.append(action)
            weights.append(np.random.random()+ 0.2)
            continue
        hit = can_hit(action, acing_dirs, opponent_hbox, positions)
        if hit:
            # print(f"Action: {action} --- Hit: {hit}.", flush=True)
            actions.append(action)
            damage = damage_amounts.get(str(action), 7) / total_damage
            if base_weights:
                damage += base_weights[indx]
            weights.append(damage)
    
        
    
    return actions, weights

def evaluate_state(my_x: int, op_x: int, my_y: int, op_y: int, 
                  my_health: int, op_health: int, my_energy: int, 
                  distance: int) -> float:
    """
    Evaluate the current state of the game for the agent
    Args:
    my_x (int): The x position of the agent
    op_x (int): The x position of the opponent
    my_y (int): The y position of the agent
    op_y (int): The y position of the opponent
    my_health (int): The health of the agent
    op_health (int): The health of the opponent
    my_energy (int): The energy of the agent
    distance (int): The distance between the agent and the opponent
    Returns:
    float: The score of the state
    """
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

def equal_more_or_less(my_val: int, op_val: int, threshold: int) -> str:
    """
    Check if the values are equal or within a threshold
    Args:
    my_val (int): The value of the agent
    op_val (int): The value of the opponent
    threshold (int): The threshold to check
    Returns:
    str: A string indicating the result of the check
    """
    if my_val > op_val + threshold:
        return False
    if my_val < op_val - threshold:
        return False
    return True

def get_eff_actions(
        distance_x: int, distance_y: int, my_prev_action: str, score: float, 
        opponent_pred_action_type: str, opponent_prev_action:str,
        my_y:int, opp_y:int ) -> Tuple[list, list]:
    """
    Get the effective actions based on the current state, which are long-range, anti-air.
    Args:
    distance_x (int): The distance in the x direction
    distance_y (int): The distance in the y direction
    my_prev_action (str): The previous action of the agent
    score (float): The score of the current state
    opponent_pred_action_type (str): The predicted action type of the opponent
    opponent_prev_action (str): The previous action of the opponent
    my_y (int): The y position of the agent
    opp_y (int): The y position of the opponent
    Returns:
    Tuple[list, list]: The effective actions and their weights
    """
    local_actions = []
    local_weights = None
    
    if distance_y < CAN_HIT_Y + random.randint(0, 40) or "jump" in str(my_prev_action):
        local_actions = long_attack_actions 
        performance_weights = [most_effective_actions[action] / most_effective_actions["total"] for action in local_actions]
        local_weights = list(map(add, probabilities_long, performance_weights))
        
    elif distance_x > np.random.randint(30, 70):
        local_actions =  anti_air_actions
        performance_weights = [most_effective_actions.get(action, 0) / most_effective_actions["total"] for action in local_actions]
        performance_weights = list(map(add, performance_weights, probabilities_anti_air))
        local_weights = get_action_weights(
            local_actions, score, performance_weights, opponent_pred_action_type, opponent_prev_action, 
            my_prev_action, my_y, opp_y)
    
    return local_actions, local_weights

def get_action_weights(actions: list, state_score: float, base_weights: list,
                      opponent_action_type: str, opponent_prev_action: Term, my_prev_action:Term, my_y:int, opp_y:int) -> list:
    """
    Get the weights for the actions based on different factors
    Args:
    actions (list): The actions to get the weights for
    state_score (float): The score of the current state
    base_weights (list): The base weights for the actions
    opponent_action_type (str): The action type of the opponent
    opponent_prev_action (Term): The previous action of the opponent
    my_prev_action (Term): The previous action of the agent
    my_y (int): The y position of the agent
    opp_y (int): The y position of the opponent
    Returns:
    list: The weights for the actions
    """
    base_weights = base_weights.copy()

    for indx, action in enumerate(actions):
        weight = 1.0
        # Gives a bonus to jump attacks when the opponent is in the air
        if ("jump" in str(my_prev_action) or my_y > opp_y) and action in arial_moves_actions:
            weight = 2.0
        # Gives a bonus to anti-air attacks when the opponent is in the air
        if "jump" in str(opponent_prev_action) and action in anti_air_actions:
            weight = 2.0
        # Gives a penalty to jump actions when the opponent is on the ground
        if "jump" in str(action) and (my_y > opp_y or my_y < opp_y):
            weight = 0.5
        # Gives a penalty to arial actions when the opponent is on the ground
        if my_y < opp_y and action in arial_moves_actions:
            weight = 0.5
        
        # Gives a penalty to anti-air actions when the agent is in the air
        if my_y > opp_y and action in anti_air_actions:
            weight = 0.5

        # Gives a bonus to long-range attacks when the opponent is close
        if equal_more_or_less(my_y, opp_y, 50) and action in long_attack_actions:
            weight = 2.5
        
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

        # Gives a bonus based on the effectiveness of the action
        if action in most_effective_actions:
            weight += 2.5 * most_effective_actions[action] / most_effective_actions["total"]
                
        base_weights[indx] += weight
   
    return base_weights
def check_and_update(
        my_prev_action, opponent_prev_action, my_prev_action_type, opponent_prev_action_type, my_health, my_prev_health, 
        opp_health, my_curr_energy, my_prev_energy, distance_y, distance_x, opp_prev_health):
    if my_prev_action_type == "attack" and (opponent_prev_action_type == "attack" or opponent_prev_action_type == "special"):
        """
        Check if the agent's previous action was an attack and the opponent's previous action was an attack or special move
        then update the counteractive actions if the agent's previous action was effective to counter the opponent's action based on heuristics

        args:
        my_prev_action (str): The previous action of the agent
        opponent_prev_action (str): The previous action of the opponent
        my_prev_action_type (str): The type of the agent's previous action
        opponent_prev_action_type (str): The type of the opponent's previous action
        my_health (int): The health of the agent
        my_prev_health (int): The previous health of the agent
        opp_health (int): The health of the opponent
        my_curr_energy (int): The current energy of the agent
        my_prev_energy (int): The previous energy of the agent
        distance_y (int): The distance in the y direction
        distance_x (int): The distance in the x direction
        opp_prev_health (int): The previous health of the opponent

        Note: Not used in the current implementation
        """
        if ((my_health == my_prev_health and my_curr_energy >= my_prev_energy) or 
            (opp_health < opp_prev_health)):
            if distance_y < CAN_HIT_Y and distance_x < MAX_CAN_HIT_X:
                action_key = counteractive_actions.get(opponent_prev_action, (my_prev_action, 0))
                action_key  = (action_key[0], action_key[1] + 1)
                counteractive_actions.update({opponent_prev_action: action_key})
                counteractive_actions["total"] += 1

def get_one_foreach_random_action() -> list:
    """
    Get a random action for each type of action
    Returns:
    list: The random actions
    """
    rand_b_action = rng.choice(attack_b_actions, size=1, replace=False)
    random_d_action = rng.choice(defensive_actions, size=1, replace=False)
    random_m_action = rng.choice(move_actions, size=1, replace=False)
    actions_ = np.concatenate([rand_b_action, random_d_action, random_m_action])
    
    return actions_.tolist()
@problog_export(
        '+int', '+int', '+int', '+int', '+int', '+int', '+int', '+int', '+int', '+int',
        '+int', '+int',  '+int', '+str', '+str', '+str', '+list', '-list'
    )
def possible_actions(
        my_x:int, op_x:int, my_y:int, op_y:int, my_facing_dir:int, my_health: int, my_prev_health:int, opp_health:int, opp_prev_health:int,
        my_curr_energy: int, my_prev_energy:int, opponent_curr_energy: int, opponent_prev_energy: int, 
        opponent_pred_action_type: str, my_prev_action: str, opponent_prev_action,
        opponent_hbox: list[int]
    ) -> list[str]:
    """
    Get k best possible actions for the agent based on different factors. This is used as clause in the Problog Knowledge Base.
    Args:
    my_x (int): The x position of the agent
    op_x (int): The x position of the opponent
    my_y (int): The y position of the agent
    op_y (int): The y position of the opponent
    my_facing_dir (int): The facing direction of the agent
    my_health (int): The health of the agent
    my_prev_health (int): The previous health of the agent
    opp_health (int): The health of the opponent
    opp_prev_health (int): The previous health of the opponent
    my_curr_energy (int): The current energy of the agent
    my_prev_energy (int): The previous energy of the agent
    opponent_curr_energy (int): The current energy of the opponent
    opponent_prev_energy (int): The previous energy of the opponent
    opponent_pred_action_type (str): The predicted action type of the opponent
    my_prev_action (str): The previous action of the agent
    opponent_prev_action (str): The previous action of the opponent
    opponent_hbox (list): The hit box of the opponent
    Returns:
    list[str]: The k best possible actions for the agent, chosen randomly based on the weights
    """
    distance_x = np.abs(my_x - op_x)
    distance_y = np.abs(my_y - op_y)
    positions = {
        "my_x": my_x, "op_x": op_x, "my_y": my_y, "op_y": op_y
    }
    # evaluate the state of the game
    score = evaluate_state(my_x, op_x, my_y, op_y, my_health, opp_health, my_curr_energy, distance_x)
    facing_dirs = {"my_facing_dir": my_facing_dir, "op_facing_dir": my_facing_dir * -1}
    # Holds the probability to be aggressive
    global AGGRESSIVE_PROB
    opponent_prev_action = Term(opponent_prev_action)
    my_prev_action = Term(my_prev_action)
    
    actions = []
    weights = []
    
    my_prev_action_type = actions_type.get(str(my_prev_action).upper(), "non_attack")
    
    
    if my_prev_action_type == "special" or my_prev_action_type == "attack":
        # Given a bonus to the most effective actions, again.
        bonus = 0
        if my_curr_energy > my_prev_energy:
            bonus += 1
        if my_health == my_prev_health:
            bonus += 1
        if opp_health < opp_prev_health:
            bonus += 2
        term_action = my_prev_action
        bonus += most_effective_actions.get(term_action, 0)
        most_effective_actions.update({term_action: bonus})
        most_effective_actions["total"] += bonus
    prob = np.random.random()

    if my_health < 150:
        # If health is low, the agent becomes more aggressive
        AGGRESSIVE_PROB=1.0
        
        
    if (opponent_curr_energy >= ENERGY_BEST_SPECIAL - 2):
        # If the opponent has enough energy to use a special move, the agent jumps
        return [Term("for_jump")]
    
    if opponent_curr_energy > 9 and distance_y < CAN_HIT_Y-np.random.randint(10, 30) and distance_x > MAX_CAN_HIT_X + np.random.randint(0, 40):
        if ((opponent_pred_action_type == "special" and prob > AGGRESSIVE_PROB) or 
            opponent_curr_energy < opponent_prev_energy):
            # If the opponent is likely to use a special move, the agent jumps
            return [Term("for_jump")]
    
    random_energy = np.random.randint(0, 10)
    if my_curr_energy >= ENERGY_BEST_SPECIAL + random_energy and distance_y <= CAN_HIT_Y:
        # If the agent has enough energy to use a special move, it uses it 
        if distance_x > np.random.randint(40, 70):
            return [Term("stand_d_df_fc")]
        else:
            return [Term("back_jump"), Term("for_jump")]
    
    if distance_x > MAX_CAN_HIT_X+np.random.randint(0, 40):
        # If the opponent is far away, the agent moves forward
        actions.extend(forward_actions)
        weights.extend(get_action_weights(
            forward_actions, score, probabilities_forward, 
            opponent_pred_action_type, opponent_prev_action, my_prev_action, my_y, op_y))
        sum_weights = sum(weights)
        probabilities = [w/sum_weights for w in weights]
        # Three is the maximum number of actions to return
        return rng.choice(actions, p=probabilities, size=min(BEST_K_ATTACKS, 3), replace=False).tolist()
    
    else:
    
        if (my_curr_energy > 4 and 
                random.random() > EPSILON_PROB and distance_y < CAN_HIT_Y
            ):
            # If the agent has enough energy and the opponent is close, it uses a special move with 1-EPSILON_PROB probability. 
            # Higher probability of EPSILON_PROB the more energy the agent will have
            for s_action in attack_s_actions:
                if energy_costs.get(str(s_action)) < my_curr_energy:
                    local_actions, local_weights = compute_helper([s_action], facing_dirs, total_damage_s, opponent_hbox=opponent_hbox, positions=positions)
                    local_weights = get_action_weights(
                        local_actions, score, local_weights, opponent_pred_action_type,
                        opponent_prev_action, my_prev_action, my_y, op_y)
                    actions.extend(local_actions)
                    weights.extend(local_weights)
        
        if distance_y > CAN_HIT_Y + np.random.randint(10, 20) and my_y < op_y - np.random.randint(10, 20):
            # If the opponent is in the air. The agent can move back.
            actions.extend(backward_actions)
            weights.extend(probabilities_backward)
        
        if (not opponent_pred_action_type == "attack" or random.random() < AGGRESSIVE_PROB):
            # If the opponent's predicted action type is not an attack or the probability of being aggressive is true
            actions_local, base_weights = compute_helper(attack_b_actions, facing_dirs, total_b_damage,opponent_hbox=opponent_hbox, positions=positions)
            base_weights = list(map(add, base_weights, probabilities_attack_b))
            weights.extend(get_action_weights(
                actions_local, score, base_weights, opponent_pred_action_type,
                opponent_prev_action, my_prev_action, my_y, op_y))
            actions.extend(actions_local)
            AGGRESSIVE_PROB = min(MIN_AGGRESSIVE_PROB, AGGRESSIVE_PROB - 0.0001*my_prev_health/my_health)
        else:
            # If the opponent's predicted action type is an attack or the probability of being aggressive is false
            # The agent uses non-attack actions
  
            actions.extend(non_attack_actions)
            weights.extend(get_action_weights(non_attack_actions, score, probabilities_non_attack, opponent_pred_action_type,
                                              opponent_prev_action, my_prev_action, my_y, op_y))
        
        # Check if are there any actions
        # Also if score is low, the agent becomes more defensive or uses long-range attacks or anti-air attacks (which might down the opponent)
        if len(actions) == 0 or score < 0.5:
            local_actions = []
            local_weights = None
            if score < 0.1:
                local_actions = defensive_actions
                local_weights = np.random.dirichlet(np.ones(len(defensive_actions)))
            elif distance_x < 100 and score < 0.25:
                local_actions = backward_actions + defensive_actions
                local_weights = probabilities_backward + probabilities_defensive
            else:
                local_actions,local_weights = get_eff_actions(
                    distance_x, distance_y, my_prev_action, score, opponent_pred_action_type,
                    opponent_prev_action, my_y, op_y)
            
            actions = local_actions
            weights = local_weights
    total_actions = len(actions)
    if total_actions > 0:
        if total_actions < BEST_K_ATTACKS + 1:
            return actions

        weights_sum = sum(weights)
        probabilities = [w/weights_sum for w in weights]
        # Choose two actions based on the probabilities
        return rng.choice(a=actions, p=probabilities, size=BEST_K_ATTACKS, replace=False).tolist()
    return actions


