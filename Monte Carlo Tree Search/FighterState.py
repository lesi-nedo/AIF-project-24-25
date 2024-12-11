from mcts.base.base import BaseState
from mcts.searcher.mcts import MCTS

class FighterState(BaseState):
    def get_possible_actions(self):
        pass

    def take_action(self, action: any) -> 'BaseState':
        pass

    def is_terminal(self) -> bool:
        pass

    def get_reward(self) -> float:
        pass

    def get_current_player(self) -> int:
        pass
    