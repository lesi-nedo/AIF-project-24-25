:- use_module('prolog_based/problog_agent_ole/terms.py').
:- use_module(library(lists)).
:- use_module(library(aggregate)).


agent(me).
agent(opponent).

possible_state(stand).
possible_state(crouch).
possible_state(air).
possible_state(down).

0.65::is_opp_stand(S) :- opp_state(S, _, _), S = stand.
0.2::is_opp_crouch(S) :- opp_state(S, _, _), S = crouch.
0.1::is_opp_air(S) :- opp_state(S, _, _), S = air.
0.05::is_opp_down(S) :- opp_state(S, _, _), S = down.

% opponent state probabilities based on counting
% Base state probabilities (sum to 1)
P::opp_state(S, C_S, N) :- 
    possible_state(S),
    count_state(S, C_S), 
    count_total_states(N),
    P is C_S/N.

% The python class adds curr_hp_value as extra clause
0.8::health_value(A, X) :- agent(A), A = opponent, curr_hp_value(A, X).
0.8::energy_value(A, X) :- agent(A), A = opponent, curr_energy_value(A,X).
1.0::health_value(A, X) :- agent(A), A = me, curr_hp_value(A, X).
1.0::energy_value(A, X) :- agent(A), A = me, curr_energy_value(A,X).

% High damage special moves 
s_action(stand_d_df_fc).  % Ultimate - highest priority but energy expensive
s_action(stand_f_d_dfb).  % Heavy special  one step back to avoid counter
s_action(air_d_df_fa).    % Air projectile for zoning
s_action(stand_d_db_bb).  % Counter - situational
s_action(air_d_db_ba).    % this is effective against   stand_d_df_fa
s_action(stand_d_df_fa).

% Basic attacks
bs_action(stand_fa).
bs_action(stand_fb). 
bs_action(crouch_fb). 
bs_action(crouch_fa).
bs_action(stand_a).
bs_action(stand_b).
bs_action(stand_f_d_dfa).

ba_action(air_fb). 
ba_action(air_db). 
ba_action(air_b). 
ba_action(air_da). 

% Categorizes actions based on their effects
0.98::action_makes_fly_opponent(S) :- S = stand_f_d_dfb; S = stand_d_df_fc.

0.95::action_downs_opponent(S) :- S = stand_f_d_dfa; S = stand_d_db_bb; S = crouch_fb.

    
0.9::action_pushes_opponent(S) :-
    S = air_d_df_fa; S = stand_fa; S = stand_fb; S = stand_d_df_fa;
    S = air_fb; S = air_db; S = air_b; S = air_da; S = crouch_fa; S = stand_a; S = stand_b;
    S = air_d_db_ba.


% Movement priorities
m_action(dash).           % Close distance quickly
m_action(back_step).      % Create space
m_action(for_jump).       % Approach from air
m_action(back_jump).      % Retreat and avoid
m_action(forward_walk).     % Default action
m_action(crouch).

forward_move(A) :- A=dash; A=for_jump; A=forward_walk.
backward_move(A) :- A=back_step;  A=back_jump.

% Defense reactions
d_action(stand_guard).    % Most common block
d_action(crouch_guard).   % Low block
d_action(air_guard).      % Air defense

defend(A) :- A=stand_guard; A=crouch_guard; A=air_guard.

% Health state probabilities
health(Agent,critical, X) :- agent(Agent), health_value(Agent, X), X < 100.
health(Agent,low, X) :- agent(Agent), health_value(Agent, X), X >= 100, X < 200.
health(Agent,medium, X) :- agent(Agent), health_value(Agent, X), X >= 200, X < 300.
health(Agent,high, X) :- agent(Agent),  health_value(Agent, X),  X > 300.

% Energy state probabilities
energy(Agent, full) :- energy_value(Agent, X), X > 149.
energy(Agent, high) :- energy_value(Agent, X), X >= 50, X =< 149.
energy(Agent, medium) :- energy_value(Agent, X), X >= 10, X < 50.
energy(Agent, low) :- energy_value(Agent, X), X < 10.


% Keep base state and action probabilities unchanged...

% Damage facts with Agent parameter
0.95::damage(crouch_fb, 12).
0.8::damage(stand_fb, 12).
0.7::damage(air_fb, 10).
0.7::damage(stand_fa, 8).
0.7::damage(stand_a, 5).
1.0::damage(stand_d_df_fc, 120).
0.6::damage(air_d_df_fa, 10).
0.9::damage(stand_f_d_dfa, 10).
0.9::damage(stand_f_d_dfb, 40).
0.8::damage(stand_d_db_bb, 25).
0.7::damage(air_d_db_ba, 10).
0.85::damage(crouch_fa, 8).
0.8::damage(stand_d_df_fa, 5).
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
energy_cost(stand_d_df_fa, 5).
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
energy_gain(stand_a, 2).
energy_gain(stand_d_df_fc, 30).
energy_gain(air_d_df_fa, 3).
energy_gain(stand_f_d_dfa, 5).
energy_gain(stand_f_d_dfb, 40).
energy_gain(stand_d_db_bb, 20).
energy_gain(stand_b, 5).
energy_gain(air_d_db_ba, 5).
energy_gain(stand_d_df_fa, 3).
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

% Opposite facing direction clause
opposite_facing_dir(me, opponent) :- 
    facing_dir(me, FDir1), facing_dir(opponent, FDir2), FDir1 \= FDir2.


% They serve to estimate opponent's' next action type 
is_close_range(X1, X2) :-
    max_distance_type(attack, AvgD),
    abs(X1 - X2) =< AvgD.

is_long_range(X1, X2) :-
    max_distance_type(attack, AvgD),
    abs(X1 - X2) > AvgD.

0.9::state_action_pref(stand, special, _, _).

0.8::state_action_pref(stand, attack, X1, X2) :- 
    is_close_range(X1, X2).

0.7::state_action_pref(stand, movement, X1, X2); 0.3::state_action_pref(stand, non_attack, X1, X2) :-
    is_long_range(X1, X2).
    
0.6::state_action_pref(air, movement, X1, X2); 0.4::state_action_pref(air, non_attack, X1, X2) :-
    is_long_range(X1, X2).

0.1::state_action_pref(air, defense, X1, X2); 0.9::state_action_pref(air, attack, X1, X2) :-
    is_close_range(X1, X2).

0.15::state_action_pref(crouch, defense, X1, X2); 0.85::state_action_pref(crouch, attack, X1, X2) :-
    is_close_range(X1, X2).

0.7::state_action_pref(crouch, movement, X1, X2); 0.3::state_action_pref(crouch, non_attack, X1, X2) :-
    is_long_range(X1, X2).


0.8::state_action_pref(down, non_attack, _, _).

1.0::state_action_pref(_, movement, _, _) :-
    facing_dir(me, MyFDir), facing_dir(opponent, OppFDir), MyFDir = OppFDir.

1.0::energy_action_pref(full, special) :- true.
0.5::energy_action_pref(high, special).
0.38::energy_action_pref(high, attack).
0.09::energy_action_pref(high, movement).
0.02::energy_action_pref(high, defense).
0.01::energy_action_pref(high, non_attack).
0.6::energy_action_pref(medium, special).
0.3::energy_action_pref(medium, attack).
0.05::energy_action_pref(medium, movement).
0.03::energy_action_pref(medium, defense).
0.02::energy_action_pref(medium, non_attack).
0.3::energy_action_pref(low, special) :- curr_energy_value(opponent, E), E > 4.
0.52::energy_action_pref(low, attack).
1.0::energy_action_pref(low, attack) :- curr_energy_value(opponent, E), E =< 4.
0.08::energy_action_pref(low, movement).
0.05::energy_action_pref(low, defense).
0.05::energy_action_pref(low, non_attack).


% Predicts the opponent's' next action type based on the current state
0.8::predict_opp_next_action_type(Type) :- 
    energy(opponent, Energy),
    curr_pos(me, X1, Y1), 
    curr_pos(opponent, X2, Y2),
    curr_energy_value(opponent, E),
    opp_state(State, _, _),
    (
        ((is_opp_air(State); is_opp_crouch(State); is_opp_stand(State)),
            state_action_pref(State, Type, X1, X2),
            energy_action_pref(Energy, Type)
        );
        (is_opp_down(State),
            Type = non_attack
        )
    ).
    
% Helpers for calculating utility
calculate_damage_ratio(Damage, DamageRatio) :-
    number(Damage),
    DamageRatio is Damage / 110.

calculate_energy_ratio(EGain, ECost, EnergyRatio) :-
    number(EGain),
    number(ECost),
    GainRatio is (1.2 * EGain) / 30,
    CostRatio is ECost / 150,
    EnergyRatio is GainRatio - CostRatio.


% Calculates the utility of an action based on the current state
action_utility(Action, FinalUtility) :-
    curr_pos(me, X1, Y1),
    curr_pos(opponent, X2, Y2),
    DistanceX is abs(X1 - X2),
    DistanceY is abs(Y1 - Y2),
    curr_hp_value(me, MyHPTemp),
    MyHP is (MyHPTemp / 400),
    my_state(MyState),
    ((MyState \= down,
        ((is_combat_action(Action),
            damage(Action, Damage),
            energy_gain(Action, EGain),
            energy_cost(Action, ECost),
            calculate_damage_ratio(Damage, DamageRatio),
            calculate_energy_ratio(EGain, ECost, EnergyRatio),
            opp_state(OppState, _, _), 
            (
                (is_opp_stand(OppState),
                    HeightMult is 1.5
                );
                (is_opp_crouch(OppState),
                    HeightMult is 1.5
                );
                (is_opp_air(OppState),
                    HeightMult is 1.2
                );
                (is_opp_down(OppState),
                    HeightMult is 0.6
                )
            ),

            (
                (DistanceX > 100,
                    DistMultTemp = 1.5

                );
                (DistanceX =< 100,
                    DistMultTemp = 0.8
                )
            ),
            DistMult is (HeightMult + MyHP),
            (
                (action_makes_fly_opponent(Action),
                    FinalUtility is 1.8 * (DamageRatio + EnergyRatio) * DistMult
                );
                (action_downs_opponent(Action),
                    FinalUtility is 1.55 *(DamageRatio + EnergyRatio) * DistMult
                );
                (action_pushes_opponent(Action),
                    FinalUtility is 1.3 * (DamageRatio + EnergyRatio) * DistMult
                )
            )
        );
        (is_non_combat(Action),
            
            ((
                (DistanceX > 500,
                    DistMult = 1.2
                );
                (DistanceX =< 500,
                    DistMult = 0.8
                ) 
            ),
            (
                (forward_move(Action),
                    FinalUtility is (0.8  * DistMult + MyHP) 
                );
                (backward_move(Action),
                    curr_energy_value(me, MyEnergy),
                    (
                        (MyEnergy >= 150,
                            FinalUtility is (2.5  * DistMult + MyHP)
                        );
                        (MyEnergy < 150,
                            FinalUtility is (0.6  * DistMult + MyHP)
                        )
                    )
                );
                (defend(Action),
                    FinalUtility is (0.5  * DistMult + MyHP) 
                );
                (Action = crouch,
                    FinalUtility is (0.7 * DistMult + MyHP) 
                )
            ))           
        ))
    );
    (MyState = down,
        FinalUtility is 0.0
    )).


% Facts about attack distances
max_distance_type(attack, 110).
max_distance_type(special, 1000).
max_dist_y(55).

is_combat_action(Action) :-
    bs_action(Action); ba_action(Action); s_action(Action).

is_non_combat(Action) :-
    m_action(Action); d_action(Action).

% Finds the possible actions based on the current state, energy, health, and previous actions
% Then calculates the utility of each action and returns the best action and its utility
find_my_best_action(BestAction, BestUtility) :-
    curr_pos(me, X1, Y1),
    curr_pos(opponent, X2, Y2),
    curr_energy_value(me, MyEnergy),
    prev_energy_value(me, MyPrevEnergy),
    curr_energy_value(opponent, OppEnergy),
    prev_energy_value(opponent, OppPrevEnergy),
    predict_opp_next_action_type(PredOppActionType),
    curr_hp_value(me, MyHP),
    prev_hp_value(me, MyPrevHP),
    curr_hp_value(opponent, OppHP),
    prev_hp_value(opponent, OppPrevHP),
    prev_action(me, MyPrevAction),
    prev_action(opponent, OppPrevAction),
    facing_dir(me, MyFDir),
    hbox(opponent, OppHBox),
    possible_actions(
        X1, X2, Y1, Y2, MyFDir, MyHP, MyPrevHP, OppHP, OppPrevHP, MyEnergy, MyPrevEnergy, 
        OppEnergy, OppPrevEnergy, PredOppActionType, MyPrevAction, OppPrevAction,OppHBox, ActionList),
    length(ActionList, L),
    (
        (L =:= 1,
            ActionList = [SingleAction],
            BestAction = SingleAction,
            BestUtility = 0.5
        );
        (L > 1,
            find_utilities(ActionList, UtilityList),
            sort(UtilityList, SortedList),
            last(SortedList, BestUtility-BestAction)
        );
        (L =:= 0,
            BestAction = crouch_fb,
            BestUtility = 0.5
        )
    ).
      
get_action_utility(Action, Utility-Action) :-
    action_utility(Action, Utility).

find_utilities(ActionList, UtilityList) :-
    maplist(get_action_utility, ActionList, UtilityList).


% Computes the probability of each action based on the number of times it has been used
P::actions_prob(A, P) :- 
    count_action(A, C_A), 
    count_total_actions(N),
    P is C_A/N.

% Finds the K actions with the highest probabilities
% This clause was used to find counter moves, but the mechanism did not improve the agent's' performance
find_best_k_prob_actions(K, BestActions) :-
    
    findall(Prob-Action, actions_prob(Action, Prob), ActionList),
    (
        ActionList = []; ActionList \= []
    ),
    sort(ActionList, SortedList),
    length(SortedList, L),
    Klocal is min(K, L),
    last(Klocal, SortedList, BestActions).

last(0, _, []).
last(K, [H|T], [H|Rest]) :- K > 0, K1 is K-1, last(K1, T, Rest).


% Main Query
query(find_my_best_action(BestAction, BestUtility)).
% Debugging Queries
% query(is_combat_action(stand_fa)).
% query(opposite_facing_dir(me, opponent)).
% query(predict_opp_next_action_type(Type)).
% query(action_utility(stand_fa, FinalUtility)).
% query(find_utilities([air_d_db_ba, stand_d_df_fa, stand_fb, stand_fa, crouch_fa, stand_a, air_b, air_da], UtilityList)).
% query(find_best_k_prob_actions(3, BestActions)).


