from logging import currentframe
from turtledemo.paint import switchupdown

from pyftg.aiinterface.command_center import CommandCenter
from pyftg.models.audio_data import AudioData
from pyftg.models.frame_data import FrameData
from pyftg.models.game_data import GameData
from pyftg.models.key import Key
from pyftg.models.round_result import RoundResult
from pyftg.models.screen_data import ScreenData
from pyftg.models.enums.action import Action

from collections import deque


class Simulator:
    def __init__(self, frame_data: FrameData, motion_list: (list, list), action_list: (list, list), player_number: bool):
        self.frame_data = frame_data
        self.motion_list = motion_list
        self.action_list = action_list
        self.player_number = player_number

        self.characters = self.frame_data.character_data.copy()
        self.proj = self.frame_data.projectile_data.copy()

    def detectHit(self, oppInd: int, attack):
        pass

    def hitPlayer(self, oppInd, attInd, attack, currentFrame):
        self.proj = self.proj

    def processFight(self, currentFrame: int):
        self.processingCommands()
        self.processingHit(currentFrame)
        self.updateAttackParameters(currentFrame)
        self.updateCharacters()

    def processingCommands(self):
        self.proj = self.proj

    def processingHit(self, currentFrame: int):
        isHit = [False, False]

        for p in self.proj:
            oppInd = 1-p.player_number
            if self.detectHit(oppInd, p):
                i = 1 - oppInd
                self.hitPlayer(oppInd,i,p,currentFrame)
            else:
                self.proj.append(p)

        for i in range(0,2):
            oppInd = 1 - i
            attack = self.characters[i].attack_data
            if self.detectHit(oppInd, attack):
                isHit[oppInd] = True
                self.hitPlayer(oppInd, i, attack, currentFrame)

    def updateAttackParameters(self, currentFrame: int):
        for p in self.proj:
            p.active += 1
            if not p.active < currentFrame:
                self.proj.remove(p)
            else:
                p.current_hit_area.left += p.speed_x
                p.current_hit_area.right+= p.speed_x
                p.current_hit_area.top += p.speed_y
                p.current_hit_area.bottom += p.speed_y

        for i in range(0,2):
            if not self.updateAttack(i):
                self.characters[i].attack_data = None

    def updateCharacters(self):
        for i in range(0,2):
            self.characters[i].x += self.characters[i].speed_x
            self.characters[i].y += self.characters[i].speed_y
            if self.characters[i].bottom >= 640:
                self.characters[i].speed_x += -self.characters[i].speed_x/abs(self.characters[i].speed_x)
                self.characters[i].speed_y = 0
            else:
                if self.characters[i].top <= 0:
                    self.characters[i].speed_y = 1
                else:
                    self.characters[i].speed_y += 1

            self.characters[i].energy = max(self.characters[i].energy, 300)
            self.characters[i].remaining_frame -= 1
            if self.characters[i].remaining_frame <= 0:
                match self.characters[i].action:
                    case Action.CHANGE_DOWN:
                        break
                    case Action.DOWN:
                        break
                    case Action.AIR:
                        break
                    case Action.CROUCH:
                        break
                    case _:
                        break







