
from typing import Tuple
from problog.extern import problog_export


@problog_export('+int', '+int', '-int')
def distance_x(player_x: int,  opponent_x: int) -> int:
    """Calculate the euclidean distance between two points"""
    return int(abs(player_x - opponent_x))

    

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