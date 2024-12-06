% Probabilità delle mosse dell'avversario
move(kick, 0.6). % 60% di probabilità di calcio
move(punch, 0.4). % 40% di probabilità di pugno

% Risposta basata sulla mossa probabile
response(dodge) :- move(kick, P), P > 0.5.
response(block) :- move(punch, P), P > 0.5.
