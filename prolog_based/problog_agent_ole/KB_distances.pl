
% Distance definitions based on game mechanics
close_range(D) :- D =< 100.    % For throws and quick attacks
mid_range(D) :- D > 100, D =< 250.  % For normal moves
far_range(D) :- D > 250.       % For projectiles

% Base distance probabilities
0.8::attack_close :- distance(D), close_range(D).
0.6::attack_mid :- distance(D), mid_range(D).
0.7::attack_far :- distance(D), far_range(D).

% Close range actions
0.4::action(throw_a) :- attack_close.
0.4::action(throw_b) :- attack_close.
0.6::action(stand_a) :- attack_close.
0.6::action(stand_b) :- attack_close.

% Mid range actions  
0.5::action(stand_fa) :- attack_mid.
0.5::action(stand_fb) :- attack_mid.
0.4::action(air_fa) :- attack_mid.
0.4::action(air_fb) :- attack_mid.

% Far range actions (projectiles)
0.7::action(stand_d_df_fa) :- attack_far.  % Projectile
0.7::action(stand_d_df_fb) :- attack_far.  % Projectile
0.6::action(stand_d_df_fc) :- attack_far.  % Ultimate projectile

% Distance is calculated from game state
distance(D) :- 
    player_x(X1),
    opponent_x(X2),
    D is abs(X1 - X2).

% Helper predicates to get positions
player_x(X) :- character(player, Char), hit_area_center_x(Char, X).
opponent_x(X) :- character(opponent, Char), hit_area_center_x(Char, X).