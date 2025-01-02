from pyftg.models.enums.state import State
from pyftg.models.frame_data import FrameData
from pyftg.models.enums.action import Action
import pandas as pandas

def load_motions(char_name):
    motions = pandas.read_csv(f'DareFightingICE-7.0beta/data/characters/{char_name}/Motion.csv')
    motions = motions.set_index("motionName")
    return motions

class Simulator:
    def __init__(self, p1:str = 'ZEN', p2:str = 'ZEN'):
        self.current_frame = None
        self.playing_action = None
        self.playing_character = None
        self.frame_data = None
        self.motions = [None, None]
        self.motions[0] = load_motions(p1)
        self.motions[1] = load_motions(p2)
        self.characters = None


    def able_action(self, frame_data: FrameData, action: Action, ch: int):
        self.frame_data = frame_data
        self.characters = self.frame_data.character_data.copy()
        self.current_frame = self.frame_data.current_frame_number
        self.playing_character = ch
        self.playing_action = action

        if self.characters[ch].energy < -self.motions[ch].loc[action.name, "attack.StartAddEnergy"]:
            return False
        elif self.characters[ch].control:
            return True
        else:
            if self.characters[ch].action is None:
                return True
            check_frame = self.motions[ch].loc[self.characters[ch].action.name, "cancelAbleFrame"] <= self.motions[ch].loc[self.characters[ch].action.name, "frameNumber"] - self.characters[ch].remaining_frame
            check_action = self.motions[ch].loc[self.characters[ch].action.name, "cancelAbleMotionLevel"] >= self.motions[ch].loc[action.name, "motionLevel"]
            return check_frame and check_action

    def run_action(self, ch, action: Action):
        if self.characters[ch].action is not action:
            self.characters[ch].remaining_frame = self.motions[ch].loc[action.name, "frameNumber"]
            self.characters[ch].energy += self.motions[ch].loc[action.name, "attack.StartAddEnergy"]
        self.characters[ch].action = action
        self.characters[ch].state = self.motions[ch].loc[action.name, "state"]
        if self.motions[ch].loc[action.name, "speedX"] != 0:
            self.characters[ch].speed_x = self.motions[ch].loc[action.name, "speedX"] if self.characters[ch].front else -self.motions[ch].loc[action.name, "speedX"]
        self.characters[ch].speed_y = self.motions[ch].loc[action.name, "speedY"]
        self.characters[ch].control = self.motions[ch].loc[action.name, "control"]

    def detect_hit(self, oppInd: int, attack):
        if attack is None or self.characters[oppInd].state == 0:
            return False
        opp_hit_area_left = self.characters[oppInd].x + self.motions[oppInd].loc[attack.name, "hitAreaLeft"] if self.characters[oppInd].front else -self.motions[oppInd].loc[attack.name, "hitAreaLeft"]
        opp_hit_area_right = self.characters[oppInd].x + self.motions[oppInd].loc[attack.name, "hitAreaRight"] if self.characters[oppInd].front else -self.motions[oppInd].loc[attack.name, "hitAreaRight"]
        opp_hit_area_up = self.characters[oppInd].y + self.motions[oppInd].loc[attack.name, "hitAreaUp"]
        opp_hit_area_down = self.characters[oppInd].y + self.motions[oppInd].loc[attack.name, "hitAreaDown"]

        att_hit_area_left = self.characters[oppInd].graphic_size_x + self.motions[oppInd].loc[attack.name, "attack.hitAreaLeft"]
        att_hit_area_right = self.characters[oppInd].graphic_size_x + self.motions[oppInd].loc[attack.name, "attack.hitAreaRight"]
        att_hit_area_up = self.characters[oppInd].graphic_size_y + self.motions[oppInd].loc[attack.name, "attack.hitAreaUp"]
        att_hit_area_down = self.characters[oppInd].graphic_size_y + self.motions[oppInd].loc[attack.name, "attack.hitAreaDown"]

        hit_left = opp_hit_area_left <= att_hit_area_right
        hit_right = opp_hit_area_right >= att_hit_area_left
        hit_up = opp_hit_area_up <= att_hit_area_down
        hit_down = opp_hit_area_down >= att_hit_area_up

        return hit_left and hit_right and hit_down and hit_up

    def is_guard(self, oppInd, attack):
        is_guard = False
        match self.characters[1-oppInd].action:
            case Action.STAND_GUARD:
                if self.motions[1-oppInd].loc[attack.name, "attack.AttackType"] == 1 or self.motions[1-oppInd].loc[attack.name, "attack.AttackType"] == 2:
                    self.run_action(1 - oppInd, Action.STAND_GUARD_RECOV)
                    is_guard = True
            case Action.CROUCH_GUARD:
                if self.motions[1-oppInd].loc[attack.name, "attack.AttackType"] == 1 or self.motions[1-oppInd].loc[attack.name, "attack.AttackType"] == 3:
                    self.run_action(1 - oppInd, Action.CROUCH_GUARD_RECOV)
                    is_guard = True
            case Action.AIR_GUARD:
                if self.motions[1-oppInd].loc[attack.name, "attack.AttackType"] == 1 or self.motions[1-oppInd].loc[attack.name, "attack.AttackType"] == 2:
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
            self.characters[1-oppInd].hp -= self.motions[1-oppInd].loc[attack.name, "attack.GuardDamage"]
            self.characters[1-oppInd].energy += self.motions[1-oppInd].loc[attack.name, "attack.GiveEnergy"]
            self.characters[1-oppInd].speed_x = direction * self.motions[1-oppInd].loc[attack.name, "attack.ImpactX"] / 2
            self.characters[1-oppInd].remaining_frame = self.motions[1-oppInd].loc[attack.name, "attack.GiveGuardRecov"]
            self.characters[oppInd] += self.motions[1-oppInd].loc[attack.name, "attack.guardAddEnergy"]
        else:
            if self.motions[1-oppInd].loc[attack.name, "attack.AttackType"] == 4:
                st = self.characters[1-oppInd].state
                if st != State.AIR and st != State.DOWN:
                    self.run_action(1 - oppInd, Action.THROW_SUFFER)
                    if self.characters[oppInd].action != Action.THROW_SUFFER:
                        self.run_action(oppInd, Action.THROW_HIT)
                    self.characters[1-oppInd].hp -= self.motions[1-oppInd].loc[attack.name, "attack.HitDamage"]
                    self.characters[1-oppInd].energy =+ self.motions[1-oppInd].loc[attack.name, "attack.GiveEnergy"]
                    self.characters[oppInd].energy += self.motions[1-oppInd].loc[attack.name, "attack.HitAddEnergy"]
                else:
                    self.characters[1 - oppInd].hp -= self.motions[1-oppInd].loc[attack.name, "attack.HitDamage"]
                    self.characters[1 - oppInd].energy = + self.motions[1-oppInd].loc[attack.name, "attack.GiveEnergy"]
                    self.characters[1 - oppInd].speed_x = direction * self.motions[1-oppInd].loc[attack.name, "attack.ImpactX"]
                    self.characters[1 - oppInd].speed_y = self.motions[1-oppInd].loc[attack.name, "attack.ImpactY"]
                    self.characters[oppInd].energy += self.motions[1-oppInd].loc[attack.name, "attack.HitAddEnergy"]

                    if not self.motions[1-oppInd].loc[attack.name, "attack.DownProp"]:
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


    def process_fight(self, frame_data: FrameData, action: Action, ch: int):
        self.frame_data = frame_data
        self.characters = self.frame_data.character_data.copy()
        self.current_frame = self.frame_data.current_frame_number
        self.playing_character = ch
        self.playing_action = action
        self.processing_commands()
        self.processing_hit()
        self.update_attack_parameters()
        self.update_characters()
        
        return FrameData(
            character_data=self.characters,
            current_frame_number=self.frame_data.current_frame_number + 1,
            current_round=self.frame_data.current_round,
            projectile_data=self.frame_data.projectile_data.copy(),
            empty_flag=self.frame_data.empty_flag,
            front=self.frame_data.front.copy(),
        )

    def processing_commands(self):
            self.run_action(self.playing_character, self.playing_action)

    def processing_hit(self):
        is_hit = [False, False]
        for i in range(0,2):
            opp_ind = 1 - i
            attack = self.characters[i].action
            if self.detect_hit(opp_ind, attack):
                is_hit[opp_ind] = True
                self.hit_player(opp_ind, self.characters[i].action, self.current_frame)

    def update_attack_parameters(self):
        for i in range(0,2):
            self.current_frame += 1
            if self.characters[i].action is not None:
                if self.current_frame <= self.motions[i].loc[self.characters[i].action.name, "attack.Active"]:
                    self.characters[i].action = None

    def update_characters(self):
        for i in range(0,2):
            self.characters[i].x += self.characters[i].speed_x
            self.characters[i].y += self.characters[i].speed_y
            if (self.characters[i].bottom >= 640) & (self.characters[i].speed_x != 0):
                self.characters[i].speed_x += -self.characters[i].speed_x/abs(self.characters[i].speed_x)
                self.characters[i].speed_y = 0
            else:
                if self.characters[i].top <= 0:
                    self.characters[i].speed_y = 1
                else:
                    self.characters[i].speed_y += 1

            self.characters[i].energy = max(self.characters[i].energy, 300)
            self.characters[i].remaining_frame -= 1






