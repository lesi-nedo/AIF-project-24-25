import json
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, List
from collections import defaultdict
from collections import Counter
from pathlib import Path
import os
@dataclass
class RoundStats:
    round_number: int
    duration: float
    damage_dealt: int
    damage_received: int
    actions_used: Dict[str, int]
    avg_energy: int
    round_result: str  # "win", "loss", "draw"
    remaining_hp: int
    opponent_remaining_hp: int
    mean_time_to_infer: float
    number_of_elapsed_frames: int

@dataclass
class MatchStats:
    match_id: str
    start_time: str
    rounds: List[RoundStats]
    total_rounds_played: int
    wins: int
    losses: int
    draws: int
    most_effective_actions: Dict[str, float]
    avg_damage_per_round: float
    
class StatsTracker:
    def __init__(self, ai_name1, ai_name2):
        self.current_match = None
        self.current_round = None
        self.match_history = []
        self.stats_file = "match-"
        self.stats_folder = f"{ai_name1}-vs-{ai_name2}"
        
    def start_new_match(self):
        self.current_match = MatchStats(
            match_id=datetime.now().strftime("%Y%m%d_%H%M%S"),
            start_time=datetime.now().isoformat(),
            rounds=[],
            total_rounds_played=0,
            wins=0,
            losses=0,
            draws=0,
            most_effective_actions={},
            avg_damage_per_round=0.0
        )
    
    def start_new_round(self, round_number: int):
        self.current_round = RoundStats(
            round_number=round_number,
            duration=0.0,
            damage_dealt=0,
            damage_received=0,
            actions_used=defaultdict(int),
            avg_energy=0,
            round_result="",
            remaining_hp=0,
            opponent_remaining_hp=0,
            mean_time_to_infer=0.0,
            number_of_elapsed_frames=0
        )
    
    def update_round_stats(self, actions: list[str], my_hps: list[int], opp_hps:list[int], 
                          my_energies: list[int]):
        if self.current_round:
            damage_dealt = opp_hps[0] - opp_hps[-1]
            damage_received = my_hps[0] - my_hps[-1]
            avg_energy = int(sum(my_energies) / len(my_energies))
            self.current_round.actions_used = actions
            self.current_round.damage_dealt = damage_dealt 
            self.current_round.damage_received = damage_received
            self.current_round.avg_energy = avg_energy
            self.current_round.remaining_hp = my_hps[-1]
            self.current_round.opponent_remaining_hp = opp_hps[-1]
    
    def end_round(self, result: str, duration: float, mean_time_to_infer: float, number_of_elapsed_frames: int):
        if self.current_round and self.current_match:
            self.current_round.round_result = result
            self.current_round.duration = duration
            self.current_round.mean_time_to_infer = mean_time_to_infer
            self.current_match.rounds.append(self.current_round)
            self.number_of_elapsed_frames = number_of_elapsed_frames
            
            self._update_match_stats(result)
            self.save_stats()
    
    def _update_match_stats(self, round_result: str):
        self.current_match.total_rounds_played += 1
        if round_result == "win":
            self.current_match.wins += 1
        elif round_result == "loss":
            self.current_match.losses += 1
        else:
            self.current_match.draws += 1
            
        # Calculate average damage
        total_damage = sum(r.damage_dealt for r in self.current_match.rounds)
        self.current_match.avg_damage_per_round = total_damage / len(self.current_match.rounds)
        
        # Update most effective actions
        all_actions = defaultdict(lambda: {"uses": 0, "damage": 0})
        for round_ in self.current_match.rounds:
            actions_used = Counter(round_.actions_used)
            for action, count in actions_used.items():
                all_actions[action]["uses"] += count
                all_actions[action]["damage"] += round_.damage_dealt / len(round_.actions_used)
                
        self.current_match.most_effective_actions = {
            action: stats["damage"]/stats["uses"] 
            for action, stats in all_actions.items() if stats["uses"] > 0
        }
    
    def save_stats(self):
        try:
            stats_file = self.stats_file + self.current_match.match_id + ".json"
            curr_dir = Path(os.path.dirname(__file__))
            path = curr_dir / "stats" 
            print(f"Saving stats to path: {path}")
            if not path.exists():
                raise FileNotFoundError("Stats directory not found: " + os.path.join(curr_dir, "stats"))
            folder_to_save = path / self.stats_folder
            os.makedirs(folder_to_save, exist_ok=True)

            file_to_save = folder_to_save / stats_file
            with open(file_to_save, 'w') as f:
                json.dump(asdict(self.current_match), f, indent=2)
        except Exception as e:
            print(f"Error saving stats: {e}")