import logging
from pyftg import AIInterface, CommandCenter, Key, FrameData, GameData, RoundResult, ScreenData
from problog.program import PrologString
from problog import get_evaluatable

logger = logging.getLogger(__name__)

class ProblogAgent(AIInterface):
    def __init__(self, knowledge_base_path="knowledge_base.pl"):
        super().__init__()
        self.blind_flag = False
        self.knowledge_base_path = knowledge_base_path
        self.problog_model = self.load_knowledge_base()

    def name(self) -> str:
        return self.__class__.__name__

    def is_blind(self) -> bool:
        return self.blind_flag

    def initialize(self, game_data: GameData, player_number: int):
        logger.info("initialize")
        self.cc = CommandCenter()
        self.key = Key()
        self.player = player_number

    def get_non_delay_frame_data(self, frame_data: FrameData):
        pass

    def input(self):
        return self.key

    def get_information(self, frame_data: FrameData, is_control: bool):
        self.frame_data = frame_data
        self.cc.set_frame_data(frame_data, self.player)

    def get_screen_data(self, screen_data: ScreenData):
        # Metodo richiesto ma non utilizzato
        self.screen_data = screen_data

    def get_audio_data(self, audio_data):
        # Metodo richiesto ma non utilizzato
        pass

    def processing(self):
        if self.frame_data.empty_flag or self.frame_data.current_frame_number <= 0:
            return

        if self.cc.get_skill_flag():
            self.key = self.cc.get_skill_key()
            return

        self.key.empty()
        self.cc.skill_cancel()

        # Decidere l'azione usando Problog
        problog_result = self.decide_action()
        if problog_result == "dodge":
            self.cc.command_call("CROUCH_B")
        elif problog_result == "block":
            self.cc.command_call("STAND_GUARD")
        else:
            self.cc.command_call("STAND_A")  # Azione predefinita

    def load_knowledge_base(self):
        try:
            with open(self.knowledge_base_path, "r") as file:
                return file.read()
        except FileNotFoundError:
            logger.error(f"Knowledge base file '{self.knowledge_base_path}' not found.")
            return ""

    def decide_action(self):
        # Interroga il modello Problog
        problog_model = PrologString(self.problog_model)
        result = get_evaluatable().create_from(problog_model).evaluate()

        # Determina l'azione con la probabilità più alta
        actions = {k: v for k, v in result.items() if "response" in k}
        best_action = max(actions, key=actions.get, default="STAND_A")
        return best_action.split("(")[1].strip(").")

    def round_end(self, round_result: RoundResult):
        logger.info(f"round end: {round_result}")

    def game_end(self):
        logger.info("game end")

    def close(self):
        pass
