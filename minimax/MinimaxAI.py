import logging

from pyftg import AIInterface
from pyftg.aiinterface.command_center import CommandCenter
from pyftg.models.key import Key

logger = logging.getLogger(__name__)

class MinimaxAI(AIInterface):
    def __init__(self, depth=3):
        self.depth = depth  # Depth of the minimax tree
        self.cc = None
        self.key = None
        self.frame_data = None
        self.player = None

    def name(self) -> str:
        return self.__class__.__name__

    def initialize(self, game_data: GameData, player_number: bool):
        logger.info(f"Initializing for player {player_number}")
        self.cc = CommandCenter()
        self.key = Key()
        self.player = player_number
        if self.player == 0:
            self.otherplayer = 1
        else:
            self.otherplayer = 0
