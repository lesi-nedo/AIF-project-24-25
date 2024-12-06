:- use_module('prolog_based/problog_agent_ole/terms.py').
% Remember delay of 14/15 frames before the action is executed

agent(me).
agent(opponent).



0.40::possible_state(stand).
0.25::possible_state(crouch).
0.2::possible_state(air).
0.15::possible_state(down).



% Base state probabilities (sum to 1)
P::state(A, S, C_S, N) :- 
    count_state(A, S, C_S), 
    count_total_states(A, N),
    C_S =< N, P is C_S/N.

is_stand(A, S) :- state(A, S, _, _), S = stand.

action_makes_fly_opponent(S) :- S = stand_f_d_dfb; S = stand_d_df_fc.

action_downs_opponent(S) :- S = stand_f_d_dfb; S = stand_f_d_dfa; S = stand_d_db_bb; S = crouch_fb; S = stand_d_df_fc.

action_pushes_opponent(S) :- 
    S = stand_f_d_dfb; S = stand_f_d_dfa; 
    S = stand_d_db_bb; S = crouch_fb; 
    S = stand_d_df_fc; S = air_d_df_fa; S = stand_fa; S = stand_fb.


0.8::health_value(A, X) :- agent(A), curr_hp_value(A, X).
0.7::energy_value(A, X) :- agent(A), curr_energy_value(A,X).

% High damage special moves (sum to 1) 
0.28::s_action(stand_d_df_fc).  % Ultimate - highest priority but energy expensive
0.18::s_action(stand_f_d_dfb).  % Heavy special  one step back to avoid counter
0.15::s_action(air_d_df_fa).    % Air projectile for zoning
0.12::s_action(stand_d_db_bb).  % Counter - situational
0.11::s_action(air_d_db_ba).    % this is effective against   stand_d_df_fa
0.05::s_action(stand_f_d_dfa).  % against this CROUCH_FB

% Basic attacks (sum to 1)
0.25::b_action(stand_fa).      % Quick high damage
0.15::b_action(air_fb).        % Air control
0.20::b_action(stand_fb).      % Ground control  
0.15::b_action(crouch_fb).     % Anti-air (no hit if stay same position)
0.05::b_action(stand_a).       % Basic attack
0.05::b_action(stand_b).       % Basic attack

% Movement priorities (sum to 1)
0.3::m_action(dash).           % Close distance quickly
0.3::m_action(back_step).      % Create space
0.2::m_action(for_jump).       % Approach from air
0.2::m_action(back_jump).      % Retreat and avoid

% Defense reactions (sum to 1)
0.4::d_action(stand_guard).    % Most common block
0.3::d_action(crouch_guard).   % Low block
0.2::d_action(air_guard).      % Air defense  

% Health state probabilities
0.1::health(Agent,critical, X) :- agent(Agent), health_value(Agent, X), X < 100.
0.2::health(Agent,low, X) :- agent(Agent), health_value(Agent, X), X >= 100, X < 200.
0.55::health(Agent,medium, X) :- agent(Agent), health_value(Agent, X), X >= 200, X < 300.
0.15::health(Agent,high, X) :- agent(Agent),  health_value(Agent, X),  X > 300.

% Energy state probabilities
0.05::energy(full) :- energy_value(X), X > 149.
0.3::energy(high) :- energy_value(X), X >= 50, X =< 149.
0.25::energy(medium) :- energy_value(X), X >= 10, X < 50.
0.4::energy(low) :- energy_value(X), X < 10.

% Keep base state and action probabilities unchanged...

% Damage facts with Agent parameter
damage(Agent, crouch_fb, 12) :- agent(Agent).
damage(Agent, stand_fb, 12) :- agent(Agent).
damage(Agent, air_fb, 10) :- agent(Agent).
damage(Agent, stand_fa, 8) :- agent(Agent).
damage(Agent, stand_a, 5) :- agent(Agent).
damage(Agent, stand_d_df_fc, 120) :- agent(Agent).
damage(Agent, air_d_df_fa, 10) :- agent(Agent).
damage(Agent, stand_f_d_dfa, 10) :- agent(Agent).
damage(Agent, stand_f_d_dfb, 40) :- agent(Agent).
damage(Agent, stand_d_db_bb, 25) :- agent(Agent).
damage(Agent, unknown, _) :- agent(Agent).

% Energy cost facts with Agent parameter
energy_cost(Agent, stand_d_df_fc, 150) :- agent(Agent).
energy_cost(Agent, stand_f_d_dfb, 55) :- agent(Agent).
energy_cost(Agent, air_d_df_fa, 5) :- agent(Agent).
energy_cost(Agent, stand_f_d_dfa, 0) :- agent(Agent).
energy_cost(Agent, stand_d_db_bb, 50) :- agent(Agent).
energy_cost(Agent, air_d_db_ba, 5) :- agent(Agent).

% Energy gain facts with Agent parameter
energy_gain(Agent, crouch_fb, 10) :- agent(Agent).
energy_gain(Agent, stand_fb, 10) :- agent(Agent).
energy_gain(Agent, air_fb, 2) :- agent(Agent).
energy_gain(Agent, stand_fa, 4) :- agent(Agent).
energy_gain(Agent, stand_a, 2) :- agent(Agent).
energy_gain(Agent, stand_d_df_fc, 30) :- agent(Agent).
energy_gain(Agent, air_d_df_fa, 3) :- agent(Agent).
energy_gain(Agent, stand_f_d_dfa, 5) :- agent(Agent).
energy_gain(Agent, stand_f_d_dfb, 40) :- agent(Agent).
energy_gain(Agent, stand_d_db_bb, 20) :- agent(Agent).

% Distance facts with Agent parameter
max_distance_to_hit(Agent, stand_d_df_fc, _) :- agent(Agent).
min_distance_to_hit(Agent, stand_d_df_fc, 0) :- agent(Agent).
max_distance_to_hit(Agent, crouch_fb, 200) :- agent(Agent).
max_distance_to_hit(Agent, stand_fb, 227) :- agent(Agent).
min_distance_to_hit(Agent, stand_fb, 80) :- agent(Agent).
max_distance_to_hit(Agent, air_fb, 150) :- agent(Agent).
min_distance_to_hit(Agent, air_fb, 0) :- agent(Agent).
max_distance_to_hit(Agent, stand_fa, 150) :- agent(Agent).
max_distance_to_hit(Agent, stand_a, 125) :- agent(Agent).
min_distance_to_hit(Agent, stand_a, 0) :- agent(Agent).
max_distance_to_hit(Agent, air_d_df_fa, 550) :- agent(Agent).
min_distance_to_hit(Agent, air_d_df_fa, 5) :- agent(Agent).
max_distance_to_hit(Agent, stand_f_d_dfa, 150) :- agent(Agent).
min_distance_to_hit(Agent, stand_f_d_dfa, 0) :- agent(Agent).
max_distance_to_hit(Agent, stand_f_d_dfb, 135) :- agent(Agent).
min_distance_to_hit(Agent, stand_f_d_dfb, 0) :- agent(Agent).
max_distance_to_hit(Agent, stand_d_db_bb, 370) :- agent(Agent).
min_distance_to_hit(Agent, stand_d_db_bb, 0) :- agent(Agent).

% Updated can_perform_action predicate
can_perform_s_action(Agent, A) :- 
    agent(Agent),
    s_action(A),
    energy_value(Agent, E), 
    energy_cost(Agent, A, EC), 
    E >= EC.
    % max_distance_to_hit(Agent, A, MD),
    % min_distance_to_hit(Agent, A, MiD), 
    % distance(D), 
    % D =< MD, 
    % D >= MiD.

action(back_jump, Agent1) :- agent(Agent1), agent(Agent2), Agent1 \= Agent2, can_perform_action(Agent2, stand_d_df_fc).

action(air_d_db_ba, Agent2) :- agent(Agent1), agent(Agent2), Agent1 \= Agent2, can_perform_action(Agent2, stand_d_df_fa).


% First, add a predicate to handle valid actions only
valid_actions(Agent, Actions) :-
    findall(A, (
        s_action(A),
        energy_value(Agent, E),
        energy_cost(Agent, A, EC),
        E >= EC
    ), Actions),
    Actions \= [].  % Ensure non-empty list


% Then modify the query to use it
1.0::all_actions(Agent, Actions) :- 
    valid_actions(Agent, Actions).


% query(health(me, _, X)).


query(all_actions(me, X)).