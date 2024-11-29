% character_state(Player, State)
% character_action(Player, Action)
% character_xyd(Player, X, Y, D)
% character_speed(Player, X_v, Y_v)
% character_hp_energy(Player, Hp, Energy)
% hit_area(PlayerNumber, Left, Right, Top, Bottom)
% hit_conferm(Player, Bool)
% character_attack(Player, AttackID)
% knockback(Player, X_m, Y_m)
% character_box(Player, W, H)

% Informazioni sul costo degli attacchi

skill_energy_cost(stand_medium_punch, 5).
skill_energy_cost(stand_medium_kick, 5).
skill_energy_cost(crouch_medium_punch, 5).
skill_energy_cost(crouch_heavy_punch, 10).
skill_energy_cost(crouch_medium_kick, 5).
skill_energy_cost(air_medium_punch, 5).
skill_energy_cost(air_medium_kick, 5).
skill_energy_cost(fireball, 15).
skill_energy_cost(energy_shield, 30).

%% Euristica aggressività giocatore in base all'energia
energy_threshold(aggressive, 50).
energy_threshold(defensive, 30).
energy_threshold(ultimate, 100).

% Delay di 15 + 1 frame, i dati sono ricevuti con ritardo
frame_duration(16.67).
frame_scaling_factor(15).
over_safe_distance(150).
bound_projectile(50).
bound_martial(30).
boud_hp_strategy(15)

:- dynamic player_is_moving/1.
:- dynamic player_next_frame/3.
:- dynamic opponent_will_hit_me/2.
:- dynamic player_can_defense/2.
:- dynamic attack_hit/2.
:- dynamic is_attacking/1.

was_hostile(Player, ID) :- character_attack(Player, AttackID), AttackID \= 0, ID = AttackID.
player_was_moving(Player) :- character_speed(Player, X_v, Y_v), (X_v \=0; Y_v \=0).
player_predict_next_position(Player, FX, FY, FD) :- frame_scaling_factor(F), knockback(Player, X_m, Y_m), character_xyd(Player, X, Y, D), character_speed(Player, X_v, Y_v), FX = X + (X_v + X_m) * D * F, FY = Y + (Y_v + Y_m) * D * F, FD = D.
player_predict_distance(Player1, Player2, D) :- player_predict_next_position(Player1, FX1, FY1, FD1), player_predict_next_position(Player2, FX2, FY2, FD2), D = sqrt((FX1 - FX2) ** 2 + (FY1 - FY2) ** 2), Player1 \= Player2.
player_predict_hitbox(Player, L, R, T, B) :- character_box(Player, W, H), player_predict_next_position(Player, FX, FY, FD), L = FX, R = FX + W, T = FY, B = FY + H.
hitbox_will_intersect(Player1, Player2) :- player_predict_hitbox(Player1, L1, R1, T1, B1), player_predict_hitbox(Player2, L2, R2, T2, B2), (R1 > L2, L1 < R2, B1 > T2, T1 < B2).
%% opponent_sure_hit_me(Player1, Player2) :- hostile(Player2), hit_area(Player2, L, R, T, B), player_next_frame(Player1, X, Y), X >= L, X =< R, Y >= T, Y =< B.
player_can_defense(Player1, Player2) :- character_state(Player1, State), (State = stand; State = crouch).
player_can_attack(Player1, Player2) :- player_can_defense(Player1, Player2).
player_is_safe(Player1, Player2, LD) :- over_safe_distance(L), player_predict_distance(Player1, Player2, D), (D >= L), LD = D.
can_shot_projectile(Player1, Player2) :- player_is_safe(Player1, Player2, LD), bound_projectile(B), (LD =< B).
can_hit_martial(Player1, Player2) :- player_is_safe(Player1, Player2, LD), bound_martial(B), (LD =< B).
strategy(Player1, defensive) :- boud_hp_strategy(B), character_hp_energy(Player1, Hp, _), Hp < B.
strategy(Player1, aggressive) :- boud_hp_strategy(B), character_hp_energy(Player1, Hp, _), Hp >= B.
should_defend(Player1, Player2) :- hitbox_will_intersect(Player1, Player2), character_hp_energy(Player1, _, Energy), Energy >= 10.
should_attack(Player1, Player2, AttackID) :- strategy(Player1, aggressive), player_can_attack(Player1, Player2), skill_energy_cost(AttackID, Cost), character_hp_energy(Player1, _, Energy), Energy >= Cost.
should_use_projectile(Player1, Player2, AttackID) :- can_shot_projectile(Player1, Player2), skill_energy_cost(AttackID, Cost), character_hp_energy(Player1, _, Energy), Energy >= Cost, AttackID = fireball.
should_use_martial(Player1, Player2, AttackID) :- can_hit_martial(Player1, Player2), skill_energy_cost(AttackID, Cost), character_hp_energy(Player1, _, Energy), Energy >= Cost, (AttackID = stand_medium_punch; AttackID = stand_medium_kick).
should_evade_or_block(Player1, Player2) :- was_hostile(Player2, ID), (ID = fireball), player_predict_distance(Player1, Player2, Distance), Distance > bound_projectile(_), player_can_defense(Player1, Player2).
optimal_action(Player1, Player2, Action) :- should_defend(Player1, Player2), Action = defend.
optimal_action(Player1, Player2, Action) :- should_use_projectile(Player1, Player2, AttackID),  Action = AttackID.
optimal_action(Player1, Player2, Action) :- should_use_martial(Player1, Player2, AttackID), Action = AttackID.
optimal_action(Player1, Player2, Action) :- should_evade_or_block(Player1, Player2), Action = evade.
optimal_action(Player1, Player2, Action) :- Action = wait.