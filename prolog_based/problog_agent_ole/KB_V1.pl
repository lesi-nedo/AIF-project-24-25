:- use_module('prolog_based/problog_agent_ole/terms.py').
:- use_module(library(lists)).
% Remember delay of 14/15 frames before the action is executed
% stand_fa is ineffective against stand_guard, crouch_guard, air_guard, and whe walks forward

agent(me).
agent(opponent).
% add is facing


0.40::possible_state(stand).
0.25::possible_state(crouch).
0.2::possible_state(air).
0.15::possible_state(down).

0.1::random_boost(high).    % 10% chance of high boost
0.3::random_boost(medium).  % 30% chance of medium boost
0.6::random_boost(low).     % 60% chance of low boost

% Base state probabilities (sum to 1)
P::state(A, S, C_S, N) :- 
    count_state(A, S, C_S), 
    count_total_states(A, N),
    C_S =< N, P is C_S/N.

is_stand(A, S) :- state(A, S, _, _), S = stand.


0.8::health_value(A, X) :- agent(A), curr_hp_value(A, X).
0.7::energy_value(A, X) :- agent(A), curr_energy_value(A,X).

% High damage special moves (sum to 1) 
0.48::s_action(stand_d_df_fc).  % Ultimate - highest priority but energy expensive
0.29::s_action(stand_f_d_dfb).  % Heavy special  one step back to avoid counter
0.005::s_action(air_d_df_fa).    % Air projectile for zoning
0.15::s_action(stand_d_db_bb).  % Counter - situational
0.001::s_action(air_d_db_ba).    % this is effective against   stand_d_df_fa

% Basic attacks (sum to 1)
0.22::b_action(stand_fa).      % Quick high damage
0.15::b_action(air_fb).        % Air control
0.15::b_action(stand_fb).      % Ground control  
0.15::b_action(crouch_fb).     % Anti-air (no hit if stay same position)
0.01::b_action(stand_a).       % Basic attack
0.01::b_action(stand_b).       % Basic attack
0.28::b_action(stand_f_d_dfa).  % against this CROUCH_FB


% Movement priorities (sum to 1)
0.55::m_action(dash).           % Close distance quickly
0.4::m_action(back_step).      % Create space
0.001::m_action(for_jump).       % Approach from air
0.001::m_action(back_jump).      % Retreat and avoid

forward_move(A) :- A=dash, m_action(A); A=for_jump, m_action(A).
backward_move(A) :- A=back_step; A=back_jump.

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
0.05::energy(Agent, full) :- energy_value(Agent, X), X > 149.
0.3::energy(Agent, high) :- energy_value(Agent, X), X >= 50, X =< 149.
0.25::energy(Agent, medium) :- energy_value(Agent, X), X >= 10, X < 50.
0.4::energy(Agent, low) :- energy_value(Agent, X), X < 10.

action_makes_fly_opponent(S) :- S = stand_f_d_dfb; S = stand_d_df_fc.

action_downs_opponent(S) :- S = stand_f_d_dfb; S = stand_f_d_dfa; S = stand_d_db_bb; S = crouch_fb; S = stand_d_df_fc.

action_failed(Agent, S, Opponent) :- 
    curr_hp_value(Opponent, X),
    prev_hp_value(Opponent, Y),
    X = Y.
    
action_pushes_opponent(S) :- 
    S = stand_f_d_dfb; S = stand_f_d_dfa; 
    S = stand_d_db_bb; S = crouch_fb; 
    S = stand_d_df_fc; S = air_d_df_fa; S = stand_fa; S = stand_fb.

% Keep base state and action probabilities unchanged...

% Damage facts with Agent parameter
0.95::damage(crouch_fb, 12).
0.8::damage(stand_fb, 12).
0.7::damage(air_fb, 10).
0.7::damage(stand_fa, 8).
0.6::damage(stand_a, 5).
1.0::damage(stand_d_df_fc, 120).
0.6::damage(air_d_df_fa, 10).
0.9::damage(stand_f_d_dfa, 10).
0.9::damage(stand_f_d_dfb, 40).
0.8::damage(stand_d_db_bb, 25).
0.7::damage(air_d_db_ba, 10).
0.8::damage(stand_b, 10).
1.0::damage(dash, 0).
1.0::damage(back_step, 0).
1.0::damage(for_jump, 0).
1.0::damage(back_jump, 0).
1.0::damage(stand_guard, 0).
1.0::damage(crouch_guard, 0).
1.0::damage(air_guard, 0).


% Energy cost facts with Agent parameter
energy_cost(stand_d_df_fc, 150).
energy_cost(stand_f_d_dfb, 55).
energy_cost(air_d_df_fa, 5).
energy_cost(stand_d_db_bb, 50).
energy_cost(air_d_db_ba, 5).
energy_cost(stand_fa, 0).
energy_cost(crouch_fb, 0).
energy_cost(stand_fb, 0).
energy_cost(air_fb, 0).
energy_cost(stand_a, 0).
energy_cost(stand_f_d_dfa, 0).
energy_cost(stand_b, 0).
energy_cost(dash, 0).
energy_cost(back_step, 0).
energy_cost(for_jump, 0).
energy_cost(back_jump, 0).
energy_cost(stand_guard, 0).
energy_cost(crouch_guard, 0).
energy_cost(air_guard, 0).


% Energy gain facts with Agent parameter
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
energy_gain(stand_b, 5).
energy_gain(air_d_db_ba, 5).
energy_gain(dash, 0).
energy_gain(back_step, 0).
energy_gain(for_jump, 0).
energy_gain(back_jump, 0).
energy_gain(stand_guard, 0).
energy_gain(crouch_guard, 0).
energy_gain(air_guard, 0).


% Distance facts with Agent parameter
max_distance_to_hit(stand_d_df_fc, 1000).
min_distance_to_hit(stand_d_df_fc, 0).
max_distance_to_hit(crouch_fb, 200).
min_distance_to_hit(crouch_fb, 0).
max_distance_to_hit(stand_fb, 237).
min_distance_to_hit(stand_fb, 75).
max_distance_to_hit(air_fb, 150).
min_distance_to_hit(air_fb, 0).
max_distance_to_hit(stand_fa, 150).
min_distance_to_hit(stand_fa, 0).
max_distance_to_hit(stand_a, 100).
min_distance_to_hit(stand_a, 0).
max_distance_to_hit(air_d_df_fa, 550).
min_distance_to_hit(air_d_df_fa, 10).
max_distance_to_hit(stand_f_d_dfa, 150).
min_distance_to_hit(stand_f_d_dfa, 0).
max_distance_to_hit(stand_f_d_dfb, 135).
min_distance_to_hit(stand_f_d_dfb, 0).
max_distance_to_hit(stand_d_db_bb, 370).
min_distance_to_hit(stand_d_db_bb, 0).
max_distance_to_hit(air_d_db_ba, 100).
min_distance_to_hit(air_d_db_ba, 0).
max_distance_to_hit(stand_b, 150).
min_distance_to_hit(stand_b, 20).
max_distance_to_hit(dash, 1000).
min_distance_to_hit(dash, 0).
max_distance_to_hit(back_step, 1000).
min_distance_to_hit(back_step, 0).
max_distance_to_hit(for_jump, 1000).
min_distance_to_hit(for_jump, 0).
max_distance_to_hit(back_jump, 1000).
min_distance_to_hit(back_jump, 0).
max_distance_to_hit(stand_guard, 1000).
min_distance_to_hit(stand_guard, 0).
max_distance_to_hit(crouch_guard, 1000).
min_distance_to_hit(crouch_guard, 0).
max_distance_to_hit(air_guard, 1000).
min_distance_to_hit(air_guard, 0).

max_distance_b_action(260).




action(back_jump, Agent1) :- agent(Agent1), agent(Agent2), Agent1 \= Agent2, can_perform_action(Agent2, stand_d_df_fc).

action(air_d_db_ba, Agent2) :- agent(Agent1), agent(Agent2), Agent1 \= Agent2, can_perform_action(Agent2, stand_d_df_fa).


action_utility(Action, FinalUtility) :-
    damage(Action, Damage),
    energy_gain(Action, EGain),
    % Base utility calculation
    (
         FinalUtility is (0.7 * Damage/120 + 0.3 * EGain/40)
    ).

% Sort actions by utility
find_my_best_action(BestAction, ActionList, MaxDistBAction) :-
    findall(Utility-Action-MaxDistBAction, (
        % Distance check
        curr_pos(me, X1, _),
        curr_pos(opponent, X2, _),
        distance_x(X1, X2, D),
        energy_value(me, E),
        max_distance_to_hit(Action, MaxD),
        min_distance_to_hit(Action, MinD),
        energy_cost(Action, EC),
        max_distance_b_action(MaxDistBAction),
        (
            (D > MaxDistBAction,
                ((health(me, critical, _),
                    backward_move(Action),
                    Utility is 0.0
                );
                (\+health(me, critical, _),
                    forward_move(Action),
                    Utility is 0.0
                ))
            );
            (D =< MaxDistBAction,
                ((EC =< E, 
                    D >= MinD,
                    (s_action(Action),
                    action_utility(Action, Utility))
                );
                (D =< MaxD, D >= MinD,
                    (b_action(Action),
                    action_utility(Action, Utility))  
                ); 
                (D < MinD,
                    (Action = crouch_fb,
                    Utility is 0.2)
                ); 
                (D >= MaxD,
                    (Action = dash, Utility is 0.0)
                )
                )
            
            )

        )
    ), ActionList),
    (
            (sort(ActionList, SortedList),
            last(SortedList, _-BestAction-MaxDistBAction))
    ).


% Query
get_my_best_action(BestAction, ActionList, D) :- find_my_best_action(BestAction, ActionList,D).

query(get_my_best_action(BestAction, ActionList, D)).



% query(health(me, _, X)).


