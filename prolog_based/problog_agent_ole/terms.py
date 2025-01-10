
from typing import Tuple
from problog.extern import problog_export
import typer

non_attack_actions = set(["dash", "back_step", "for_jump", "back_jump", "stand_guard", "crouch_guard", "air_guard"])

attack_s_actions = set([
    "stand_d_df_fc", "stand_f_d_dfb", "air_d_df_fa", "stand_d_db_bb", "air_d_db_ba"
])

attack_b_actions = set([
    "stand_fa", "air_fb", "stand_fb", "crouch_fb", "stand_a", "stand_b", "stand_f_d_dfa"
])

energy_costs = {
    'stand_d_df_fc': 150,
    'stand_f_d_dfb': 55,
    'air_d_df_fa': 5,
    'stand_d_db_bb': 50,
    'air_d_db_ba': 5
}

move_ranges = {
    'stand_d_df_fc': {'max': 1000, 'min': 0},
    'crouch_fb': {'max': 200, 'min': 0},
    'stand_fb': {'max': 237, 'min': 75},
    'air_fb': {'max': 150, 'min': 0},
    'stand_fa': {'max': 150, 'min': 0},
    'stand_a': {'max': 100, 'min': 0},
    'air_d_df_fa': {'max': 550, 'min': 10},
    'stand_f_d_dfa': {'max': 150, 'min': 0},
    'stand_f_d_dfb': {'max': 135, 'min': 0},
    'stand_d_db_bb': {'max': 370, 'min': 0},
    'air_d_db_ba': {'max': 100, 'min': 0},
    'stand_b': {'max': 150, 'min': 20}
}

@problog_export('+int', '+int', '-int')
def distance_x(player_x: int,  opponent_x: int) -> int:
    """Calculate the euclidean distance between two points"""
    return int(abs(player_x - opponent_x))

def compute_distance(action, my_front:int,my_hbleft:int,  my_hbright:int,  my_hbtop:int, my_hbbottom:int, 
        opp_hbleft:int, opp_hbright:int,  opp_hbtop:int, opp_hbbottom:int, max_dist, min_dist) -> Tuple[int, int]:
    # Calculate horizontal distance between hit boxes
    if my_front == 1:  # Facing right
        hit_start = my_hbright
        hit_end = hit_start + max_dist
        target = opp_hbleft
        horizontal_hit = (hit_start + min_dist <= target <= hit_end)
    else:  # Facing left 
        hit_start = my_hbleft
        hit_end = hit_start - max_dist
        target = opp_hbright
        horizontal_hit = (hit_end <= target <= hit_start - min_dist)
    if "air" in action:
        vertical_hit = (my_hbbottom >= opp_hbtop and my_hbtop <= opp_hbbottom)
        return int(horizontal_hit and vertical_hit)
    return int(horizontal_hit)

@problog_export(
        '+int', '+int', '+int', '+int', '+int', '+int', '+int',
        '+int', '+int', '+int', '-int'
    )
def can_hit(
        my_front:int, my_hbleft:int,  my_hbright:int,  my_hbtop:int, my_hbbottom:int, 
        opp_hbleft:int, opp_hbright:int,  opp_hbtop:int, opp_hbbottom:int, curr_energy: int
    ) -> int:
    """Calculate if an action's hit box will overlap with opponent's position"""

    if curr_energy > 4:
        for s_action in attack_s_actions:
            if energy_costs.get(s_action) <= curr_energy:
                hit = compute_distance(s_action, my_front, my_hbleft, my_hbright, my_hbtop, my_hbbottom, opp_hbleft, opp_hbright, opp_hbtop, opp_hbbottom, move_ranges[s_action]['max'], move_ranges[s_action]['min'])
                if hit:
                    return hit
        
    for b_action in attack_b_actions:
        hit = compute_distance(b_action, my_front, my_hbleft, my_hbright, my_hbtop, my_hbbottom, opp_hbleft, opp_hbright, opp_hbtop, opp_hbbottom, move_ranges[b_action]['max'], move_ranges[b_action]['min'])
        if hit:
            return hit
   

                       
    return 0
    

   

# def get_range_type(distance: int) -> str:
#     """Get the range category based on distance"""
#     if distance <= 100:
#         return "close"
#     elif distance <= 250:
#         return "mid" 
#     else:
#         return "far"

# def calculate_positions(player_data, opponent_data) -> Tuple[int, int]:
#     """Extract center positions from character data"""
#     player_center = player_data.getHitAreaCenterX()
#     opponent_center = opponent_data.getHitAreaCenterX()
#     return player_center, opponent_center