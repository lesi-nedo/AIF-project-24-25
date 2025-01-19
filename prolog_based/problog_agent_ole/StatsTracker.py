import json
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, List
from collections import defaultdict
from collections import Counter
from pathlib import Path
import os
import uuid
import numpy as np

rng = np.random.default_rng()
@dataclass
class RoundStats:
    round_number: int
    duration: float
    damage_dealt: int
    damage_received: int
    actions_used: Dict[str, int]
    actions_inferred: Dict[str, int]
    avg_energy: int
    round_result: str  # "win", "loss", "draw"
    my_hps: List[int]
    opponent_hps: List[int]
    time_to_infer: List[float]
 
@dataclass
class MatchStats:
    match_id: str
    rounds: List[RoundStats]
    total_rounds_played: int
    duration: int
    wins: int
    losses: int
    draws: int
    most_effective_actions: Dict[str, float]
    avg_damage_per_round: float
    
class StatsTracker:
    """
    Class to track and save statistics of the matches played
    Attributes:
    current_match (MatchStats): The current match being played
    current_round (RoundStats): The current round being played
    match_history (List[MatchStats]): List of all matches played
    stats_file (str): Name of the stats file
    stats_folder (str): Name of the folder to save the stats
    """
    def __init__(self, ai_name1, ai_name2):
        self.current_match = None
        self.current_round = None
        self.match_history = []
        self.stats_file = "match-"
        self.stats_folder = f"{ai_name1}-vs-{ai_name2}"
        
 

    def create_from_dict(self, data_obj: dict):
        """
        Create MatchStats object from the given dictionary
        Parameters:
        data_obj (dict): Dictionary containing the match data
        Returns:
        MatchStats: MatchStats object
        """
        num_rounds = data_obj["num_rounds"]
        for_loop_round = num_rounds + 1
        new_match = MatchStats(
            match_id= "-".join(rng.choice(str(uuid.uuid4()).split("-"), size=2, replace=False)),
            rounds=[],
            total_rounds_played=num_rounds,
            duration=sum([data_obj['durations'][i] for i in range(1, for_loop_round)]) / 3600,
            wins=0,
            losses=0,
            draws=0,
            most_effective_actions=defaultdict(str),
            avg_damage_per_round=0
        )

        for round in range(1, for_loop_round):
            damage_dealt = data_obj['opponent_hps'][round][0] - data_obj['opponent_hps'][round][-1]
            damage_received = data_obj['my_hps'][round][0] - data_obj['my_hps'][round][-1]
            avg_energy = int(sum(data_obj['my_energy'][round]) / len(data_obj['my_energy'][round]))
            if data_obj['round_results'][round] == None:
                my_last_hp = data_obj['my_hps'][round][-1]
                opponent_last_hp = data_obj['opponent_hps'][round][-1]
                if my_last_hp > opponent_last_hp:
                    round_result = "win"
                elif my_last_hp < opponent_last_hp:
                    round_result = "loss"
                else:
                    round_result = "draw"
            else:
                round_result = data_obj['round_results'][round]

            if round_result == "win":
                new_match.wins += 1
            elif round_result == "loss":
                new_match.losses += 1
            else:
                new_match.draws += 1
            round = RoundStats(
                round_number=round,
                duration=data_obj['durations'][round] / 3600,
                damage_dealt=damage_dealt,
                damage_received=damage_received,
                actions_used=data_obj['my_actions_executed'][round],
                actions_inferred=data_obj['my_actions_inferred'][round],
                avg_energy=avg_energy,
                round_result=round_result,
                my_hps=data_obj['my_hps'][round],
                opponent_hps=data_obj['opponent_hps'][round],
                time_to_infer=data_obj['time_taken'][round],
            )
            new_match.rounds.append(round)
        return new_match
        

    
    def save_stats(self, attr_dict: dict):
        """
        Save the statistics to a file
        Parameters:
        attr_dict (dict): Dictionary containing the match data
        """
        try:
            match_obj = self.create_from_dict(attr_dict)
            stats_file = self.stats_file + match_obj.match_id + ".json"
            curr_dir = Path(os.path.dirname(__file__))
            path = curr_dir / "stats" 
            print(f"Saving stats to path: {path}")
            if not path.exists():
                raise FileNotFoundError("Stats directory not found: " + os.path.join(curr_dir, "stats"))
            folder_to_save = path / self.stats_folder
            os.makedirs(folder_to_save, exist_ok=True)

            file_to_save = folder_to_save / stats_file
            


            with open(file_to_save, 'w') as f:

                json.dump(asdict(match_obj), f, indent=2)
        except Exception as e:
            print(f"Error saving stats: {e}")