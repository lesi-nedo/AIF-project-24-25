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
    #         check-frame = currMotion["cancellableFrame"] <= currMotion["frameNumber"] - self.character[ch].remainingFrame
    #         checkAction = currMotion["cancellableMotionLevel"] >= nextMotion["motionLevel"]
    #         return check-frame & checkAction

    def run_action(self, ch, action: Action):
        if self.characters[ch].action is not action:
            self.characters[ch].remaining_frame = self.motions[ch].loc[action.name, "frameNumber"]
            self.characters[ch].energy += self.motions[ch].loc[action.name, "attack.StartAddEnergy"]
        self.characters[ch].action = action
        self.characters[ch].state = self.motions[ch].loc[action.name, "state"]
        if self.motions[ch].loc[action.name, "speedX"] is not 0:
            self.characters[ch].speed_x = self.motions[ch].loc[action.name, "speedX"] if self.characters[ch].front else -self.motions[ch].loc[action.name, "speedX"]
        self.characters[ch].speed_y = self.motions[ch].loc[action.name, "speedY"]
        self.characters[ch].control = self.motions[ch].loc[action.name, "control"]

    def detect_hit(self, oppInd: int, attack):
        if attack is None or self.characters[oppInd].state == 0:
            return False
        opp_hit_area_left = self.characters[oppInd].x + self.motions[oppInd].loc[attack.name, "hitAreaLeft"] if self.characters[oppInd].front else -self.motions[oppInd].loc[attack.name, "hitAreaLeft"]
        opp_hit_area_right = self.characters[oppInd].x + self.motions[oppInd].loc[attack.name, "hitAreaRight"] if self.characters[oppInd].front else -self.motions[oppInd].loc[attack.name, "hitAreaRight"]
        opp_hit_area_top = self.characters[oppInd].y + self.motions[oppInd].loc[attack.name, "hitAreaTop"]
        opp_hit_area_bottom = self.characters[oppInd].y + self.motions[oppInd].loc[attack.name, "hitAreaBottom"]

        att_hit_area_left = self.characters[oppInd].graphic_size_x + self.motions[oppInd].loc[attack.name, "attack.hitAreaLeft"]
        att_hit_area_right = self.characters[oppInd].graphic_size_x + self.motions[oppInd].loc[attack.name, "attack.hitAreaRight"]
        att_hit_area_top = self.characters[oppInd].graphic_size_y + self.motions[oppInd].loc[attack.name, "attack.hitAreaTop"]
        att_hit_area_bottom = self.characters[oppInd].graphic_size_y + self.motions[oppInd].loc[attack.name, "attack.hitAreaLeft"]

        hit_left = opp_hit_area_left <= att_hit_area_right
        hit_right = opp_hit_area_right >= att_hit_area_left
        hit_top = opp_hit_area_top <= att_hit_area_bottom
        hit_bottom = opp_hit_area_bottom >= att_hit_area_top

        return hit_left and hit_right and hit_bottom and hit_top

    def is_guard(self, oppInd, attack):
        is_guard = False
        match self.characters[1-oppInd].action:
            case Action.STAND_GUARD:
                if self.motions[1-oppInd].loc[attack.name, "attackType"] == 1 or self.motions[1-oppInd].loc[attack.name, "attackType"] == 2:
                    self.run_action(1 - oppInd, Action.STAND_GUARD_RECOV)
                    is_guard = True
            case Action.CROUCH_GUARD:
                if self.motions[1-oppInd].loc[attack.name, "attackType"] == 1 or self.motions[1-oppInd].loc[attack.name, "attackType"] == 3:
                    self.run_action(1 - oppInd, Action.CROUCH_GUARD_RECOV)
                    is_guard = True
            case Action.AIR_GUARD:
                if self.motions[1-oppInd].loc[attack.name, "attackType"] == 1 or self.motions[1-oppInd].loc[attack.name, "attackType"] == 2:
                    self.run_action(1 - oppInd, Action.AIR_GUARD_RECOV)
                    is_guard = True
            case Action.STAND_GUARD_RECOV:
                self.run_action(1 - oppInd, Action.STAND_GUARD_RECOV)
                is_guard = True
            case Action.CROUCH_GUARD_RECOV:
                self.run_action(1 - oppInd, Action.CROUCH_GUARD_RECOV)
                is_guard = True
            case Action.AIR_GUARD_RECOV:
                self.run_action(1 - oppInd, Action.AIR_GUARD_RECOV)
                is_guard = True
                pass
            case _:
                is_guard = False
        return is_guard

    def hit_player(self, oppInd, attack, currentFrame):
        self.characters[oppInd].hit_count += 1
        self.characters[oppInd].last_hit_frame = currentFrame

        direction = 1 if self.characters[oppInd].x <= self.characters[1-oppInd].x else -1

        if self.is_guard(oppInd, attack):
            self.characters[1-oppInd].hp -= self.motions[1-oppInd].loc[attack.name, "guardDamage"]
            self.characters[1-oppInd].energy += self.motions[1-oppInd].loc[attack.name, "giveEnergy"]
            self.characters[1-oppInd].speed_x = direction * self.motions[1-oppInd].loc[attack.name, "impactX"] / 2
            self.characters[1-oppInd].remaining_frame = self.motions[1-oppInd].loc[attack.name, "giveGuardRecov"]
            self.characters[oppInd] += self.motions[1-oppInd].loc[attack.name, "guardGiveEnergy"]
        else:
            if self.motions[1-oppInd].loc[attack.name, "attackType"] == 4:
                st = self.characters[1-oppInd].state
                if st != State.AIR and st != State.DOWN:
                    self.run_action(1 - oppInd, Action.THROW_SUFFER)
                    if self.characters[oppInd].action != Action.THROW_SUFFER:
                        self.run_action(oppInd, Action.THROW_HIT)
                    self.characters[1-oppInd].hp -= self.motions[1-oppInd].loc[attack.name, "hitDamage"]
                    self.characters[1-oppInd].energy =+ self.motions[1-oppInd].loc[attack.name, "giveEnergy"]
                    self.characters[oppInd].energy += self.motions[1-oppInd].loc[attack.name, "hitAddEnergy"]
                else:
                    self.characters[1 - oppInd].hp -= self.motions[1-oppInd].loc[attack.name, "hitDamage"]
                    self.characters[1 - oppInd].energy = + self.motions[1-oppInd].loc[attack.name, "giveEnergy"]
                    self.characters[1 - oppInd].speed_x = direction * self.motions[1-oppInd].loc[attack.name, "impactX"]
                    self.characters[1 - oppInd].speed_y = self.motions[1-oppInd].loc[attack.name, "impactY"]
                    self.characters[oppInd].energy += self.motions[1-oppInd].loc[attack.name, "hitAddEnergy"]

                    if not self.motions[1-oppInd].loc[attack.name, "dropProp"]:
                        match st:
                            case State.STAND:
                                self.run_action(1 - oppInd, Action.STAND_RECOV)
                                pass
                            case State.CROUCH:
                                self.run_action(1 - oppInd, Action.CROUCH_RECOV)
                                pass
                            case State.AIR:
                                self.run_action(1 - oppInd, Action.AIR_RECOV)
                                pass
                    else:
                        self.run_action(1 - oppInd, Action.CHANGE_DOWN)
                        self.characters[1-oppInd].remaining_frame = self.motions[1-oppInd].loc[Action.CHANGE_DOWN.name, "frameNumber"]


    def process_fight(self, currentFrame: int = 0):
        self.processing_commands()
        self.processing_hit(currentFrame)
        self.update_attack_parameters(currentFrame)
        self.update_characters()

    def processing_commands(self):
        for i in range(0,2):
            self.run_action(i, self.action_list.deque())

    def processing_hit(self, currentFrame: int):
        is_hit = [False, False]

        # for p in self.proj:
        #     opp_ind = 1-p.player_number
        #     if self.detectHit(opp_ind, p):
        #         i = 1 - opp_ind
        #         self.hitPlayer(opp_ind, i, p, currentFrame)
        #     else:
        #         self.proj.append(p)

        for i in range(0,2):
            opp_ind = 1 - i
            attack = self.characters[i].attack_data
            if self.detect_hit(opp_ind, attack):
                is_hit[opp_ind] = True
                self.hit_player(opp_ind, self.characters[i].action, currentFrame)

    def update_attack_parameters(self, currentFrame: int):
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
            if currentFrame <= self.motions[i].loc [self.characters[i].action.name, "attack.Active"]:
                self.characters[i].action = None

    def update_characters(self):
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






