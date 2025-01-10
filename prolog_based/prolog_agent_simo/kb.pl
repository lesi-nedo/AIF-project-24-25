% character_state(Player, State)
% character_action(Player, Action)
% character_xyd(Player, X, Y, D)
% character_speed(Player, X_v, Y_v)
% character_hp_energy(Player, Hp, Energy)
% hit_conferm(Player, Bool)
% character_attack(Player, AttackID)
% knockback(Player, X_m, Y_m)
% character_box(Player, W, H)

% Informazioni sul costo degli attacchi
skill_energy_cost(stand_medium_punch, 0).
skill_energy_cost(stand_medium_kick, 0).
skill_energy_cost(crouch_medium_punch, 0).
skill_energy_cost(crouch_heavy_punch, 0).
skill_energy_cost(crouch_medium_kick, 0).
skill_energy_cost(air_medium_punch, 0).
skill_energy_cost(air_medium_kick, 0).
skill_energy_cost(fireball, 5).
skill_energy_cost(ultra, 150).

%% Euristica aggressività giocatore in base all'hp
hp_threshold(aggressive, 50).
hp_threshold(defensive, 30).
hp_threshold(ultimate, 100).

% Delay di 15 + 1 frame, i dati sono ricevuti con ritardo
frame_duration(16.67).
frame_scaling_factor(15).
over_safe_distance(200).
bound_projectile(150).
bound_martial(150).
boud_hp_strategy(15)

% State and Action Predicates
:- dynamic was_hostile/2.
:- dynamic player_was_moving/1.
:- dynamic player_predict_next_position/4.
:- dynamic player_predict_distance/3.
:- dynamic player_predict_hitbox/5.
:- dynamic hitbox_will_intersect/2.
:- dynamic player_can_defense/2.
:- dynamic player_can_attack/2.
:- dynamic player_is_safe/3.
:- dynamic can_shot_projectile/2.
:- dynamic can_hit_martial/2.
:- dynamic strategy/2.
:- dynamic should_defend/2.
:- dynamic should_attack/3.
:- dynamic should_use_projectile/3.
:- dynamic should_use_martial/3.
:- dynamic should_evade_or_block/2.
:- dynamic optimal_action/3.

% Supporting Data Predicates
:- dynamic character_attack/2.
:- dynamic character_speed/3.
:- dynamic knockback/3.
:- dynamic character_xyd/4.
:- dynamic character_box/3.
:- dynamic hp_threshold/2.
:- dynamic character_hp_energy/3.
:- dynamic character_state/2.
:- dynamic character_action/2.
:- dynamic hit_conferm/2.


was_hostile(Player, ID) :- character_attack(Player, AttackID), AttackID \= 0, ID = AttackID.
was_hostile(Player, ID) :- character_attack(Player, AttackID), AttackID \= 0, ID = AttackID.
player_was_moving(Player) :- character_speed(Player, X_v, Y_v), (X_v \=0; Y_v \=0).
player_predict_next_position(Player, FX, FY, FD) :- frame_scaling_factor(F), knockback(Player, X_m, Y_m), character_xyd(Player, X, Y, D), character_speed(Player, X_v, Y_v), FX is X + (X_v + X_m) * D * F, FY is Y + (Y_v + Y_m) * D * F, FD is D.
player_predict_distance(Player1, Player2, D) :- player_predict_next_position(Player1, FX1, FY1, _), player_predict_next_position(Player2, FX2, FY2, _), D = sqrt((FX1 - FX2) ** 2 + (FY1 - FY2) ** 2), Player1 \= Player2.
player_predict_hitbox(Player, L, R, T, B) :- character_box(Player, W, H), player_predict_next_position(Player, FX, FY, _), L = FX, R = FX + W, T = FY, B = FY + H.
hitbox_will_intersect(Player1, Player2) :- player_predict_hitbox(Player1, L1, R1, T1, B1), player_predict_hitbox(Player2, L2, R2, T2, B2), (R1 > L2, L1 < R2, B1 > T2, T1 < B2).
player_can_defense(Player1, _) :- character_state(Player1, State), (State = stand; State = crouch).
player_can_attack(Player1, Player2) :- player_can_defense(Player1, Player2).
player_is_safe(Player1, Player2, LD) :- over_safe_distance(L), player_predict_distance(Player1, Player2, D), (D >= L), LD = D.
can_shot_projectile(Player1, Player2) :- player_is_safe(Player1, Player2, LD), bound_projectile(B), (LD >= B).
can_hit_martial(Player1, Player2) :- player_predict_distance(Player1, Player2, D), bound_martial(B), (D =< B).
strategy(Player1, defensive) :- boud_hp_strategy(B), character_hp_energy(Player1, Hp, _), Hp < B.
strategy(Player1, aggressive) :- boud_hp_strategy(B), character_hp_energy(Player1, Hp, _), Hp >= B.
should_defend(Player1, Player2) :- strategy(Player1, defensive), hitbox_will_intersect(Player1, Player2), character_hp_energy(Player1, _, Energy), Energy >= 10.
should_attack(Player1, Player2, AttackID) :- strategy(Player1, aggressive), player_can_attack(Player1, Player2), skill_energy_cost(AttackID, Cost), character_hp_energy(Player1, _, Energy), Energy >= Cost.
should_use_projectile(Player1, Player2, AttackID) :- can_shot_projectile(Player1, Player2), skill_energy_cost(AttackID, Cost), character_hp_energy(Player1, _, Energy), Energy >= Cost, AttackID = fireball.
should_use_martial(Player1, Player2, AttackID) :- can_hit_martial(Player1, Player2), skill_energy_cost(AttackID, Cost), character_hp_energy(Player1, _, Energy), Energy >= Cost, (AttackID = stand_medium_punch; AttackID = stand_medium_kick).
should_evade_or_block(Player1, Player2) :- bound_projectile(B), was_hostile(Player2, ID), (ID = fireball), player_predict_distance(Player1, Player2, Distance), Distance > B, player_can_defense(Player1, Player2).
should_ultra(Player1) :- skill_energy_cost(ultra, Cost), character_hp_energy(Player1, _, Energy), (Energy >= Cost).
optimal_action(Player1, _, Action) :- should_ultra(Player1), !, Action = ultra.
optimal_action(Player1, Player2, Action) :- should_use_martial(Player1, Player2, AttackID), !, Action = AttackID.
optimal_action(Player1, Player2, Action) :- should_use_projectile(Player1, Player2, AttackID),  !, Action = AttackID.
optimal_action(Player1, Player2, Action) :- should_defend(Player1, Player2), !, Action = defend.
optimal_action(Player1, Player2, Action) :- should_evade_or_block(Player1, Player2), !, Action = evade.
optimal_action(_, _, Action) :- !, Action = wait.