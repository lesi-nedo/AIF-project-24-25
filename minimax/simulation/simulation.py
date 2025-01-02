from os import MFD_ALLOW_SEALING

from pyftg.models.enums.state import State
from pyftg.models.frame_data import FrameData
from pyftg.models.enums.action import Action
import pandas as pandas

from collections import deque

motions = []
def load_motions(char_name, i):
    if motions[i] is None:
        motions[i].set_index("motionName", inplace = True)
        motions[i] = pandas.read_csv(f'.DareFightingICE-7.0beta/data/characters/{char_name}/Motion.csv')
    return motions[i]

class Simulator:
    def __init__(self, frame_data: FrameData, action_list: (deque, deque), player_number: bool, p1:str = 'ZEN', p2:str = 'ZEN'):
        self.frame_data = frame_data
        self.motions = []
        self.motions[0] = load_motions(p1, 0)
        self.motions[1] = load_motions(p2, 1)
        self.action_list = action_list
        self.player_number = player_number

        self.characters = self.frame_data.character_data.copy()
        self.proj = self.frame_data.projectile_data.copy()


    # def ableAction(self, ch, action: Action):
    #     nextMotion = self.motions[ch][ action.name]
    #     currMotion = self.motions[ch][ self.characters[ch].action.name]
    #     if self.characters[ch].energy < -nextMotion["attack.StartAddEnergy"]:
    #         return False
    #     elif self.characters[ch].control:
    #         return True
    #     else:
    #         checkframe = currMotion["cancellableFrame"] <= currMotion["frameNumber"] - self.character[ch].remainingFrame
    #         checkAction = currMotion["cancellableMotionLevel"] >= nextMotion["motionLevel"]
    #         return checkframe & checkAction

    def runAction(self, ch, action: Action):
        motion = self.motions[ch][action.name]
        if self.characters[ch].action is None:
            self.characters[ch].remaining_frame = motion["frameNumber"]
            self.characters[ch].energy += motion["attack.StartAddEnergy"]
        self.characters[ch].action = action
        self.characters[ch].state = motion["state"]
        if motion["speedX"] is not 0:
            self.characters[ch].speed_x = motion["speedX"] if self.characters[ch].front else -motion["speedX"]
        self.characters[ch].speed_y = motion["speedY"]
        self.characters[ch].control = motion["control"]

    def detectHit(self, oppInd: int, attack):
        if attack is None or self.characters[oppInd].state == 0:
            return False
        oppHitAreaLeft = self.characters[oppInd].x + self.motions[oppInd]["hitAreaLeft"] if self.characters[oppInd].front else -self.motions[oppInd]["hitAreaLeft"]
        oppHitAreaRight = self.characters[oppInd].x + self.motions[oppInd]["hitAreaRight"] if self.characters[oppInd].front else -self.motions[oppInd]["hitAreaRight"]
        oppHitAreaTop = self.characters[oppInd].y + self.motions[oppInd]["hitAreaTop"]
        oppHitAreaBottom = self.characters[oppInd].y + self.motions[oppInd]["hitAreaBottom"]

        attHitAreaLeft = self.characters[oppInd].graphic_size_x + self.motions[oppInd]["attack.hitAreaLeft"]
        attHitAreaRight = self.characters[oppInd].graphic_size_x + self.motions[oppInd]["attack.hitAreaRight"]
        attHitAreaTop = self.characters[oppInd].graphic_size_y + self.motions[oppInd]["attack.hitAreaTop"]
        attHitAreaBottom = self.characters[oppInd].graphic_size_y + self.motions[oppInd]["attack.hitAreaLeft"]

        hitLeft = oppHitAreaLeft <= attHitAreaRight
        hitRight = oppHitAreaRight >= attHitAreaLeft
        hitTop = oppHitAreaTop <= attHitAreaBottom
        hitBottom = oppHitAreaBottom >= attHitAreaTop

        return hitLeft and hitRight and hitBottom and hitTop

    def isGuard(self, oppInd, attack):
        isGuard = False
        match self.characters[1-oppInd].action:
            case Action.STAND_GUARD:
                if self.motions[1-oppInd][attack.name]["attackType"] == 1 or self.motions[1-oppInd][attack.name]["attackType"] == 2:
                    self.runAction(1-oppInd, Action.STAND_GUARD_RECOV)
                    isGuard = True
            case Action.CROUCH_GUARD:
                if self.motions[1-oppInd][attack.name]["attackType"] == 1 or self.motions[1-oppInd][attack.name]["attackType"] == 3:
                    self.runAction(1-oppInd, Action.CROUCH_GUARD_RECOV)
                    isGuard = True
            case Action.AIR_GUARD:
                if self.motions[1-oppInd][attack.name]["attackType"] == 1 or self.motions[1-oppInd][attack.name]["attackType"] == 2:
                    self.runAction(1-oppInd, Action.AIR_GUARD_RECOV)
                    isGuard = True
            case Action.STAND_GUARD_RECOV:
                self.runAction(1 - oppInd, Action.STAND_GUARD_RECOV)
                isGuard = True
            case Action.CROUCH_GUARD_RECOV:
                self.runAction(1 - oppInd, Action.CROUCH_GUARD_RECOV)
                isGuard = True
            case Action.AIR_GUARD_RECOV:
                self.runAction(1 - oppInd, Action.AIR_GUARD_RECOV)
                isGuard = True
                pass
            case _:
                isGuard = False
        return isGuard

    def hitPlayer(self, oppInd, attInd, attack, currentFrame):
        self.characters[oppInd].hit_count += 1
        self.characters[oppInd].last_hit_frame = currentFrame

        direction = 1 if self.characters[oppInd].x <= self.characters[1-oppInd].x else -1

        if self.isGuard(oppInd, attack):
            self.characters[1-oppInd].hp -= self.motions[1-oppInd][attack.name]["guardDamage"]
            self.characters[1-oppInd].energy += self.motions[1-oppInd][attack.name]["giveEnergy"]
            self.characters[1-oppInd].speed_x = direction * self.motions[1-oppInd][attack.name]["impactX"] / 2
            self.characters[1-oppInd].remaining_frame = self.motions[1-oppInd][attack.name]["giveGuardRecov"]
            self.characters[oppInd] += self.motions[1-oppInd][attack.name]["guardGiveEnergy"]
        else:
            if self.motions[1-oppInd][attack.name]["attackType"] == 4:
                st = self.characters[1-oppInd].state
                if st != State.AIR and st != State.DOWN:
                    self.runAction(1-oppInd, Action.THROW_SUFFER)
                    if self.characters[oppInd].action != Action.THROW_SUFFER:
                        self.runAction(oppInd, Action.THROW_HIT)
                    self.characters[1-oppInd].hp -= self.motions[1-oppInd][attack.name]["hitDamage"]
                    self.characters[1-oppInd].energy =+ self.motions[1-oppInd][attack.name]["giveEnergy"]
                    self.characters[oppInd].energy += self.motions[1-oppInd][attack.name]["hitAddEnergy"]
                else:
                    self.characters[1 - oppInd].hp -= self.motions[1 - oppInd][attack.name]["hitDamage"]
                    self.characters[1 - oppInd].energy = + self.motions[1 - oppInd][attack.name]["giveEnergy"]
                    self.characters[1 - oppInd].speed_x = direction * self.motions[1 - oppInd][attack.name]["impactX"]
                    self.characters[1 - oppInd].speed_y = self.motions[1 - oppInd][attack.name]["impactY"]
                    self.characters[oppInd].energy += self.motions[1 - oppInd][attack.name]["hitAddEnergy"]

                    if not self.motions[1-oppInd][attack.name]["dropProp"]:
                        match st:
                            case State.STAND:
                                self.runAction(1 - oppInd, Action.STAND_RECOV)
                                pass
                            case State.CROUCH:
                                self.runAction(1 - oppInd, Action.CROUCH_RECOV)
                                pass
                            case State.AIR:
                                self.runAction(1-oppInd, Action.AIR_RECOV)
                                pass
                    else:
                        self.runAction(1-oppInd, Action.CHANGE_DOWN)
                        self.characters[1-oppInd].remaining_frame = self.motions[1-oppInd][Action.CHANGE_DOWN.name]["frameNumber"]


    def processFight(self, currentFrame: int = 0):
        self.processingCommands()
        self.processingHit(currentFrame)
        self.updateAttackParameters(currentFrame)
        self.updateCharacters()

    def processingCommands(self):
        for i in range(0,2):
            self.runAction(i, self.action_list.deque())

    def processingHit(self, currentFrame: int):
        isHit = [False, False]

        # for p in self.proj:
        #     oppInd = 1-p.player_number
        #     if self.detectHit(oppInd, p):
        #         i = 1 - oppInd
        #         self.hitPlayer(oppInd, i, p, currentFrame)
        #     else:
        #         self.proj.append(p)

        for i in range(0,2):
            oppInd = 1 - i
            attack = self.characters[i].attack_data
            if self.detectHit(oppInd, attack):
                isHit[oppInd] = True
                self.hitPlayer(oppInd, i, self.characters[i].action, currentFrame)

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
            currentFrame += 1
            if currentFrame <= self.motions[i][self.characters[i].action.name]["attack.Active"]:
                self.characters[i].action = None

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






