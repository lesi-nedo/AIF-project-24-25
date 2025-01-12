:- use_module('prolog_based/problog_agent_ole/terms.py').
:- use_module(library(lists)).
:- use_module(library(aggregate)).

% Remember delay of 14/15 frames before the action is executed
% stand_fa is ineffective against stand_guard, crouch_guard, air_guard, and whe walks forward

agent(me).
agent(opponent).

possible_state(stand).
possible_state(crouch).
possible_state(air).
possible_state(down).

% Base state probabilities (sum to 1)
P::opp_state(S, C_S, N) :- 
    possible_state(S),
    count_state(S, C_S), 
    count_total_states(N),
    C_S =< N, P is C_S/N.


0.65::is_opp_stand(S) :- opp_state(S, _, _), S = stand.
0.2::is_opp_crouch(S) :- opp_state(S, _, _), S = crouch.
0.1::is_opp_air(S) :- opp_state(S, _, _), S = air.
0.05::is_opp_down(S) :- opp_state(S, _, _), S = down.


0.8::health_value(A, X) :- agent(A), A = opponent, curr_hp_value(A, X).
0.8::energy_value(A, X) :- agent(A), A = opponent, curr_energy_value(A,X).
1.0::health_value(A, X) :- agent(A), A = me, curr_hp_value(A, X).
1.0::energy_value(A, X) :- agent(A), A = me, curr_energy_value(A,X).

% High damage special moves 
0.48::s_action(stand_d_df_fc).  % Ultimate - highest priority but energy expensive
0.2::s_action(stand_f_d_dfb).  % Heavy special  one step back to avoid counter
0.1::s_action(air_d_df_fa).    % Air projectile for zoning
0.15::s_action(stand_d_db_bb).  % Counter - situational
0.05::s_action(air_d_db_ba).    % this is effective against   stand_d_df_fa

% Basic attacks
0.2::bs_action(stand_fa).
0.18::bs_action(stand_fb). 
0.11::bs_action(crouch_fb). 
0.08::bs_action(crouch_fa).
0.08::bs_action(stand_a).
 0.1::bs_action(stand_b).
0.15::bs_action(stand_f_d_dfa).

0.35::ba_action(air_fb). 
0.08::ba_action(air_f_d_dfa). 
0.3::ba_action(air_db). 
0.15::ba_action(air_b). 
0.12::ba_action(air_da). 




% Movement priorities
0.15::m_action(dash).           % Close distance quickly
0.15::m_action(back_step).      % Create space
0.15::m_action(for_jump).       % Approach from air
0.15::m_action(back_jump).      % Retreat and avoid
0.2::m_action(forward_walk).     % Default action
0.2::m_action(crouch).

forward_move(A) :- A=dash; A=for_jump; A=forward_walk.
backward_move(A) :- A=back_step;  A=back_jump.

% Defense reactions
0.4::d_action(stand_guard).    % Most common block
0.3::d_action(crouch_guard).   % Low block
0.2::d_action(air_guard).      % Air defense

defend(A) :- A=stand_guard; A=crouch_guard; A=air_guard.

% Health state probabilities
health(Agent,critical, X) :- agent(Agent), health_value(Agent, X), X < 100.
health(Agent,low, X) :- agent(Agent), health_value(Agent, X), X >= 100, X < 200.
health(Agent,medium, X) :- agent(Agent), health_value(Agent, X), X >= 200, X < 300.
health(Agent,high, X) :- agent(Agent),  health_value(Agent, X),  X > 300.

% Energy state probabilities
0.05::energy(Agent, full) :- energy_value(Agent, X), X > 149.
0.3::energy(Agent, high) :- energy_value(Agent, X), X >= 50, X =< 149.
0.25::energy(Agent, medium) :- energy_value(Agent, X), X >= 10, X < 50.
0.4::energy(Agent, low) :- energy_value(Agent, X), X < 10.

action_makes_fly_opponent(S) :- S = stand_f_d_dfb; S = stand_d_df_fc.

action_downs_opponent(S) :- S = stand_f_d_dfb; S = stand_f_d_dfa; S = stand_d_db_bb; S = crouch_fb; S = stand_d_df_fc.

    
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
0.9::damage(air_f_d_dfa, 20).
0.7::damage(stand_a, 5).
1.0::damage(stand_d_df_fc, 120).
0.6::damage(air_d_df_fa, 10).
0.9::damage(stand_f_d_dfa, 10).
0.9::damage(stand_f_d_dfb, 40).
0.8::damage(stand_d_db_bb, 25).
0.7::damage(air_d_db_ba, 10).
0.85::damage(crouch_fa, 8).
0.9::damage(air_da, 5).
0.8::damage(air_b, 10).
0.85::damage(air_db, 10).
0.8::damage(stand_b, 10).
1.0::damage(dash, 0).
1.0::damage(back_step, 0).
1.0::damage(for_jump, 0).
1.0::damage(back_jump, 0).
1.0::damage(stand_guard, 0).
1.0::damage(crouch_guard, 0).
1.0::damage(air_guard, 0).
1.0::damage(forward_walk, 0).
1.0::damage(crouch, 0).


% Energy cost facts with Agent parameter
energy_cost(stand_d_df_fc, 150).
energy_cost(stand_f_d_dfb, 55).
energy_cost(air_d_df_fa, 5).
energy_cost(stand_d_db_bb, 50).
energy_cost(air_d_db_ba, 5).
energy_cost(stand_fa, 0).
energy_cost(air_f_d_dfa, 0).
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
energy_cost(crouch_fa, 0).
energy_cost(air_db, 0).
energy_cost(air_b, 0).
energy_cost(air_da, 0).
energy_cost(forward_walk, 0).
energy_cost(crouch, 0).


% Energy gain facts with Agent parameter
energy_gain(crouch_fb, 10).
energy_gain(stand_fb, 10).
energy_gain(air_fb, 2).
energy_gain(stand_fa, 4).
energy_gain(air_f_d_dfa, 5).
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
energy_gain(crouch_fa, 5).
energy_gain(air_db, 5).
energy_gain(air_b, 5).
energy_gain(air_da, 5).
energy_gain(forward_walk, 0).
energy_gain(crouch, 0).


opposite_facing_dir(me, opponent) :- 
    facing_dir(me, FDir1), facing_dir(opponent, FDir2), FDir1 \= FDir2.


avg_distance_type(attack, 150).

0.8::predict_opp_next_action_type(Type) :- 
    energy(opponent, Energy),
    opp_action_type(PrevType),
    curr_pos(me, X1, Y1), curr_pos(opponent, X2, Y2),
    curr_energy_value(opponent, E),
    avg_distance_type(attack, AvgD),
    possible_state(State),
    (
        ((is_opp_air(State); is_opp_crouch(State); is_opp_stand(State)),
            ( 
                (
                    (Energy = full,
                        (State = stand,
                            (Type = special)
                        
                        );
                        (State \= stand,
                            (type = movement; Type = defense; Type = non_attack)
                        )
                    )
                    
                );

                ((Energy \= full, Energy \= low),
                    (
                        (
                            (Type = attack, abs(X1 - X2) < AvgD)
                        ); 
                        (
                            (Type = special; Type = defense; Type = movement)
                        )
                    )
                );

                ((Energy = low),
                    (
                        (Type = attack, abs(X1 - X2) < AvgD)
                    );
                    (
                        (E @> 4,
                            (Type = special; Type = defense; Type = movement)
                        );
                        (E @=< 4, 
                            (Type = defense; Type = movement)
                        )
                    )

                
                ); 
                ( \+Energy = low,
                    (abs(X1 - X2) > AvgD,
                        (Type = movement; Type = special)
                    );
                    (abs(X1 - X2) =< AvgD,
                        (Type = attack; Type = special)
                    )

                )
                
            )
        );
        (is_opp_down(State),
            Type = non_attack
        )
    ).
    

action_utility(Action, FinalUtility) :-
    health(me, Health, _),
    (
        ((bs_action(Action); s_action(Action); ba_action(Action)),
            damage(Action, Damage),
            energy_gain(Action, EGain),
            energy_cost(Action, ECost),
            (

                (action_makes_fly_opponent(Action),
                    FinalUtility is (1.8 * Damage/110 + 1.8 * EGain/30 - ECost/150)

                );
                (action_downs_opponent(Action),
                    FinalUtility is (1.55 * Damage/110 + 1.5 * EGain/30 - ECost/150)
                );
                (action_pushes_opponent(Action),
                    FinalUtility is (1.3 * Damage/110 + 1.3 * EGain/30 - ECost/150)
                );
                ((\+action_makes_fly_opponent(Action), \+action_downs_opponent(Action), \+action_pushes_opponent(Action)),
                    FinalUtility is (Damage/110 + 1.2 * EGain/30 - ECost/150)
                )
            )
        );
        ((m_action(Action); d_action(Action)),
            (
                ((d_action(Action), Health = critical),
                    FinalUtility is 0.15
                );
                ((d_action(Action), Health = low),
                    FinalUtility is 0.1
                );
                ((d_action(Action), Health = medium),
                    FinalUtility is 0.05
                );
                ((m_action(Action), Health = critical),
                    FinalUtility is 0.1
                );
                ((m_action(Action), Health = low),
                    FinalUtility is 0.05
                );
                ((m_action(Action), Health = medium),
                    FinalUtility is 0.5
                );
                ((d_action(Action), Health = high),
                    FinalUtility is 0.0
                );
                ((m_action(Action), Health = high),
                    FinalUtility is 0.5
                )
            )           
        )

    ).

find_utilities(ActionList, []).
find_utilities([Action|Rest], [Utility-Action|UtilityList]) :-
    action_utility(Action, Utility),
    find_utilities(Rest, UtilityList).

find_my_best_action(BestAction, BestUtility) :-
    curr_pos(me, X1, Y1),
    curr_pos(opponent, X2, Y2),
    energy_value(me, MyEnergy),
    energy_value(opponent, OppEnergy),
    predict_opp_next_action_type(Type),
    my_prev_action(MyPrevAction),
    (
        ((opposite_facing_dir(me, opponent), FDir is 1),
            possible_actions(X1, X2, Y1, Y2, FDir, MyEnergy, OppEnergy, Type, MyPrevAction, ActionList)
        );
        ((\+opposite_facing_dir(me, opponent), FDir is 0),
            possible_actions(X1, X2, Y1, Y2, FDir, MyEnergy, OppEnergy, Type, MyPrevAction, ActionList)
        )
    ),
    (
        find_utilities(ActionList, UtilityList),
        (
            (sort(UtilityList, SortedList),
            last(SortedList, BestUtility-BestAction))
        )
    ).

% Query
get_my_best_action(BestAction, ActionList,FDir) :- find_my_best_action(BestAction, ActionList,FDir).

% query(get_my_best_action(BestAction, ActionList,FDir)).
% query(opposite_facing_dir(me, opponent)).
% query(predict_opp_next_action_type(Type)).
query(find_my_best_action(BestAction, BestUtility)).


% query(health(opponent, _, X)).


