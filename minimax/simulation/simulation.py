from pyftg.models.frame_data import FrameData
from pyftg.models.enums.action import Action
import pandas as pandas

from collections import deque

motions = {}
def load_motions(char_name):
    if motions[char_name] is  None:
        motions[char_name] = pandas.read_csv(f'.DareFightingICE-7.0beta/data/characters/{char_name}/Motion.csv')
    return motions[char_name]

class Simulator:
    def __init__(self, frame_data: FrameData, action_list: (deque, deque), player_number: bool, p1:str = 'ZEN', p2:str = 'ZEN'):
        self.frame_data = frame_data
        self.motions = []
        self.motions[0] = load_motions(p1)
        self.motions[1] = load_motions(p2)
        self.action_list = action_list
        self.player_number = player_number

        self.characters = self.frame_data.character_data.copy()
        self.proj = self.frame_data.projectile_data.copy()


    def ableAction(self, ch, action: Action):
        nextMotion = self.motions[ch, action.name]
        currMotion = self.motions[ch, self.characters[ch].action.name]
        if self.characters[ch].energy < -nextMotion["attack.StartAddEnergy"]:
            return False
        elif self.characyers[ch].control:
            return True
        else:
            checkframe = currMotion["cancellableFrame"] <= currMotion["frameNumber"] - self.character[ch].remainingFrame
            checkAction = currMotion["cancellableMotionLevel"] >= nextMotion["motionLevel"]
            return checkframe & checkAction

    def runAction(self, ch, action: Action):
        motion = self.motions[ch, Action.name]
        if self.characters[ch].action is None:
            self.characters[ch].remaining_frame = motion["frameNumber"]
            self.characters[ch].energy += motion["attack.StartAddEnergy"]
        self.characters[ch].action = action
        self.characters[ch].state = motion["state"]
        if motion["speedX"] is not 0:
            self.characters[ch].speed_x = motions["speedX"] if self.characters[ch].front else -motion["speedX"]
        self.characters[ch].speed_y = motion["speedY"]
        self.characters[ch].control = motion["control"]

    def detectHit(self, oppInd: int, attack):
        pass

    def hitPlayer(self, oppInd, attInd, attack, currentFrame):
        pass

    def processFight(self, currentFrame: int = 0):
        self.processingCommands(currentFrame)
        self.processingHit(currentFrame)
        self.updateAttackParameters(currentFrame)
        self.updateCharacters(currentFrame)

    def processingCommands(self):
        for i in range(1,2):
            self.characters[i].action =

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







