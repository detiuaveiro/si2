% Winning lines
line(0, 1, 2). line(3, 4, 5). line(6, 7, 8). 
line(0, 3, 6). line(1, 4, 7). line(2, 5, 8). 
line(0, 4, 8). line(2, 4, 6).                

% Find a winning move
win_move(Player, Board, Index) :-
    line(I, J, Index),
    nth0(I, Board, Player), nth0(J, Board, Player), nth0(Index, Board, e).

% Fallback to first empty
first_empty(Board, Index) :- nth0(Index, Board, e).

% Best move logic
best_move(Player, Board, Move) :- win_move(Player, Board, Move), !.
best_move(_, Board, Move) :- first_empty(Board, Move), !.