:- use_module('prolog_based/problog_agent_ole/distances.py').
% Remember delay of 14/15 frames before the action is executed

agent(me).
agent(opponent).


% Base state probabilities (sum to 1)
t(_)::state(stand).  % Most common state
t(_)::state(crouch). % Defensive position
t(_)::state(air).    % During jumps/aerials
t(_)::state(down).   % After being hit

% High damage special moves (sum to 1) 
0.28::action(stand_d_df_fc).  % Ultimate - highest priority but energy expensive
0.18::action(stand_f_d_dfb).  % Heavy special  one step back to avoid counter
0.15::action(air_d_df_fa).    % Air projectile for zoning
0.12::action(stand_d_db_bb).  % Counter - situational
0.11::action(air_d_db_ba).    % this is effective against   stand_d_df_fa
0.05::action(stand_f_d_dfa).  % against this CROUCH_FB
t(_)::action(unknown).       % Most common state

% Basic attacks (sum to 1)
0.25::action(stand_fa).      % Quick high damage
0.15::action(air_fb).        % Air control
0.20::action(stand_fb).      % Ground control  
0.15::action(crouch_fb).     % Anti-air (no hit if stay same position)
0.05::action(stand_a).       % Basic attack
0.05::action(stand_b).       % Basic attack
t(_)::action(unknown).        % Most common state

% Movement priorities (sum to 1)
0.3::action(dash).           % Close distance quickly
0.3::action(back_step).      % Create space
0.2::action(for_jump).       % Approach from air
0.2::action(back_jump).      % Retreat and avoid

% Defense reactions (sum to 1)
0.4::action(stand_guard).    % Most common block
0.3::action(crouch_guard).   % Low block
0.2::action(air_guard).      % Air defense  

% Health state probabilities
0.1::health(critical) :- health_value(X), X < 20.
0.2::health(low) :- health_value(X), X >= 20, X < 40.
0.55::health(medium) :- health_value(X), X >= 40, X < 70.
0.15::health(high) :- health_value(X), X >= 70.

% Energy state probabilities
0.05::energy(full) :- energy_value(X), X > 90.
0.3::energy(high) :- energy_value(X), X >= 70, X =< 90.
0.25::energy(medium) :- energy_value(X), X >= 40, X < 70.
0.4::energy(low) :- energy_value(X), X < 40.

damage(crouch_fb, 12).
damage(stand_fb, 12).
damage(air_fb, 10).
damage(stand_fa, 8).
damage(stand_a, 5).
damage(stand_d_df_fc, 120).
damage(air_d_df_fa, 10).
damage(stand_f_d_dfa, 10).
damage(stand_f_d_dfb, 40).
damage(stand_d_db_bb, 25).
damage(unknown, _).

energy_cost(stand_d_df_fc, 150).
energy_cost(stand_f_d_dfb, 55).
energy_cost(air_d_df_fa, 5).
energy_cost(stand_f_d_dfa, 0).
energy_cost(stand_d_db_bb, 50).
energy_cost(air_d_db_ba, 5).

energy_gain(crouch_fb, 10).
energy_gain(stand_fb, 10).
energy_gain(air_fb, 2).
energy_gain(stand_fa, 4).
energy_gain(stand_a, 2).
energy_gain(stand_d_df_fc, 30).
energy_gain(air_d_df_fa, 3).
energy_gain(stand_f_d_dfa, 5).
energy_gain(stand_f_d_dfb, 40).
energy_gain(stand_d_db_bb, 20).

max_distance_to_hit(stand_d_df_fc, _).
min_distance_to_hit(stand_d_df_fc, 0).
max_distance_to_hit(crouch_fb, 200).
% min_distance_to_hit(crouch_fb, 20) :- that the opponent does not run towards the player 
max_distance_to_hit(stand_fb, 227).
min_distance_to_hit(stand_fb, 80).
max_distance_to_hit(air_fb, 150).
min_distance_to_hit(air_fb, 0).
max_distance_to_hit(stand_fa, 150).
% min_distance_to_hit(stand_fa, 0) :- same as above
max_distance_to_hit(stand_a, 125).
min_distance_to_hit(stand_a, 0).
max_distance_to_hit(air_d_df_fa, 550).
min_distance_to_hit(air_d_df_fa, 5).
max_distance_to_hit(stand_f_d_dfa, 150).
min_distance_to_hit(stand_f_d_dfa, 0).
max_distance_to_hit(stand_f_d_dfb, 135).
min_distance_to_hit(stand_f_d_dfb, 0).
max_distance_to_hit(stand_d_db_bb, 370).
min_distance_to_hit(stand_d_db_bb, 0).



