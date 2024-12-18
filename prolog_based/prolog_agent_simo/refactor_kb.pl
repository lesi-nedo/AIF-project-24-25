% =====================================
% Dynamic Predicate Declarations
% =====================================

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
:- dymanic hit_area/5.
:- dymanic hit_conferm/2.
:- dymanic character_action/2.

% Supporting Data Predicates
:- dynamic character_attack/2.
:- dynamic character_speed/3.
:- dynamic knockback/3.
:- dynamic character_xyd/4.
:- dynamic character_box/3.
:- dynamic hp_threshold/2.
:- dynamic character_hp_energy/3.
:- dynamic character_state/2.

% =====================================
% Game Parameters and Constants
% =====================================

% Skill energy costs
skill_energy_cost(stand_medium_punch, 0).
skill_energy_cost(stand_medium_kick, 0).
skill_energy_cost(crouch_medium_punch, 0).
skill_energy_cost(crouch_heavy_punch, 0).
skill_energy_cost(crouch_medium_kick, 0).
skill_energy_cost(air_medium_punch, 0).
skill_energy_cost(air_medium_kick, 0).
skill_energy_cost(fireball, 5).

% HP thresholds for strategies
hp_threshold(aggressive, 50).
hp_threshold(defensive, 30).
hp_threshold(ultimate, 100).

% Frame-related constants
frame_duration(16.67).             % in milliseconds
frame_scaling_factor(15).          % scaling factor for frames

% Distance boundaries
over_safe_distance(200).           % units
bound_projectile(150).             % units
bound_martial(100).                % units

% HP strategy boundary
bound_hp_strategy(15).

% =====================================
% Rule Definitions
% =====================================

% Determines if a player is hostile based on their attack.
was_hostile(Player, AttackID) :-
    character_attack(Player, CurrentAttackID),
    CurrentAttackID \= 0,
    AttackID = CurrentAttackID.

% Checks if a player is moving based on their speed.
player_was_moving(Player) :-
    character_speed(Player, X_v, Y_v),
    (X_v \= 0 ; Y_v \= 0).

% Predicts the next position of a player.
player_predict_next_position(Player, FutureX, FutureY, Direction) :-
    frame_scaling_factor(Factor),
    knockback(Player, KnockbackX, KnockbackY),
    character_xyd(Player, CurrentX, CurrentY, Direction),
    character_speed(Player, SpeedX, SpeedY),
    FutureX is CurrentX + (SpeedX + KnockbackX) * Direction * Factor,
    FutureY is CurrentY + (SpeedY + KnockbackY) * Direction * Factor.

% Predicts the distance between two players.
player_predict_distance(Player1, Player2, Distance) :-
    player_predict_next_position(Player1, FX1, FY1, _),
    player_predict_next_position(Player2, FX2, FY2, _),
    Distance is sqrt((FX1 - FX2) ** 2 + (FY1 - FY2) ** 2),
    Player1 \= Player2.

% Predicts the hitbox boundaries of a player.
player_predict_hitbox(Player, Left, Right, Top, Bottom) :-
    character_box(Player, Width, Height),
    player_predict_next_position(Player, FutureX, FutureY, _),
    Left is FutureX,
    Right is FutureX + Width,
    Top is FutureY,
    Bottom is FutureY + Height.

% Checks if two players' hitboxes will intersect.
hitbox_will_intersect(Player1, Player2) :-
    player_predict_hitbox(Player1, L1, R1, T1, B1),
    player_predict_hitbox(Player2, L2, R2, T2, B2),
    R1 > L2,
    L1 < R2,
    B1 > T2,
    T1 < B2.

% Determines if a player can defend based on their state.
player_can_defense(Player1, Player2) :-
    character_state(Player1, State),
    (State = stand ; State = crouch).

% Determines if a player can attack (currently same as can_defense).
player_can_attack(Player1, Player2) :-
    player_can_defense(Player1, Player2).

% Checks if a player is at a safe distance.
player_is_safe(Player1, Player2, SafeDistance) :-
    over_safe_distance(L),
    player_predict_distance(Player1, Player2, D),
    D >= L,
    SafeDistance = D.

% Determines if a player can shoot a projectile.
can_shot_projectile(Player1, Player2) :-
    player_is_safe(Player1, Player2, SafeDistance),
    bound_projectile(Bound),
    SafeDistance >= Bound.

% Determines if a player can hit another with a martial attack.
can_hit_martial(Player1, Player2) :-
    player_predict_distance(Player1, Player2, Distance),
    bound_martial(Bound),
    Distance =< Bound.

% Determines the strategy based on HP thresholds.
strategy(Player1, Strategy) :-
    hp_threshold(aggressive, AggB),
    hp_threshold(defensive, DefB),
    character_hp_energy(Player1, Hp, _),
    (Hp >= AggB -> Strategy = aggressive
    ; Hp < DefB  -> Strategy = defensive
    ; Strategy = neutral).

% Determines if a player should defend.
should_defend(Player1, Player2) :-
    hitbox_will_intersect(Player1, Player2),
    character_hp_energy(Player1, _, Energy),
    Energy >= 10.

% Determines if a player should attack.
should_attack(Player1, Player2, AttackID) :-
    strategy(Player1, aggressive),
    player_can_attack(Player1, Player2),
    skill_energy_cost(AttackID, Cost),
    character_hp_energy(Player1, _, Energy),
    Energy >= Cost.

% Determines if a player should use a projectile attack.
should_use_projectile(Player1, Player2, AttackID) :-
    can_shot_projectile(Player1, Player2),
    skill_energy_cost(AttackID, Cost),
    character_hp_energy(Player1, _, Energy),
    Energy >= Cost,
    AttackID = fireball.

% Determines if a player should use a martial attack.
should_use_martial(Player1, Player2, AttackID) :-
    can_hit_martial(Player1, Player2),
    skill_energy_cost(AttackID, Cost),
    character_hp_energy(Player1, _, Energy),
    Energy >= Cost,
    (AttackID = stand_medium_punch ; AttackID = stand_medium_kick).

% Determines if a player should evade or block.
should_evade_or_block(Player1, Player2) :-
    bound_projectile(Bound),
    was_hostile(Player2, ID),
    ID = fireball,
    player_predict_distance(Player1, Player2, Distance),
    Distance > Bound,
    player_can_defense(Player1, Player2).

% Determines the optimal action for a player.
optimal_action(Player1, Player2, Action) :-
    should_use_martial(Player1, Player2, AttackID),
    !,
    Action = AttackID.

optimal_action(Player1, Player2, Action) :-
    should_use_projectile(Player1, Player2, AttackID),
    !,
    Action = AttackID.

optimal_action(Player1, Player2, Action) :-
    should_defend(Player1, Player2),
    !,
    Action = defend.

optimal_action(Player1, Player2, Action) :-
    should_evade_or_block(Player1, Player2),
    !,
    Action = evade.

optimal_action(_, _, wait).  % Default action

:- compile(player_predict_distance/3).
:- compile(player_predict_next_position/4).