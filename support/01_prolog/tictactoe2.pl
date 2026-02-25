% Winning lines
line(0, 1, 2). line(3, 4, 5). line(6, 7, 8). 
line(0, 3, 6). line(1, 4, 7). line(2, 5, 8). 
line(0, 4, 8). line(2, 4, 6).

% Opponent definition
opponent(x, o).
opponent(o, x).

% Check if a specific player has won
win(Board, Player) :-
    line(I, J, K),
    nth0(I, Board, Player),
    nth0(J, Board, Player),
    nth0(K, Board, Player).

% Check if the game is a draw (no empty spaces left)
draw(Board) :- \+ nth0(_, Board, e).


% --- 2. State Generation (Making a Move) ---

% Replace an element in a list at a specific index
replace([_|T], 0, X, [X|T]).
replace([H|T], I, X, [H|R]) :-
    I > 0, I1 is I - 1, replace(T, I1, X, R).

% Generate a valid next board state
move(Board, Index, Player, NextBoard) :-
    nth0(Index, Board, e),
    replace(Board, Index, Player, NextBoard).


% --- 3. The Minimax (Negamax) Algorithm ---

% Base Case 1: The current player has already won (Score = 1)
minimax(Board, Player, _, 1) :- win(Board, Player), !.

% Base Case 2: The opponent has won (Score = -1)
minimax(Board, Player, _, -1) :- opponent(Player, Opp), win(Board, Opp), !.

% Base Case 3: The game is a draw (Score = 0)
minimax(Board, _, _, 0) :- draw(Board), !.

% Recursive Step: Evaluate all possible moves and pick the best one
minimax(Board, Player, BestMove, BestScore) :-
    opponent(Player, Opp),
    % 1. Find all valid moves and resulting boards
    findall(Move-NextBoard, move(Board, Move, Player, NextBoard), Moves),
    % 2. Recursively score all next states from the opponent's perspective
    evaluate_moves(Moves, Opp, ScoredMoves),
    % 3. Pick the move that maximizes our score
    best_choice(ScoredMoves, BestMove, BestScore).


% --- 4. Helper Rules for Minimax ---

% Evaluate a list of possible moves
evaluate_moves([], _, []).
evaluate_moves([Move-NextBoard | Rest], Opp, [Move-Score | RestScored]) :-
    minimax(NextBoard, Opp, _, OppScore),
    Score is -OppScore, % Negamax: My score is the negative of the opponent's score
    evaluate_moves(Rest, Opp, RestScored).

% Find the move with the highest score in a list of ScoredMoves
best_choice([Move-Score], Move, Score).
best_choice([Move-Score | Rest], BestMove, BestScore) :-
    best_choice(Rest, RestMove, RestScore),
    (Score > RestScore ->
        BestMove = Move, BestScore = Score
    ;
        BestMove = RestMove, BestScore = RestScore
    ).


% --- 5. Main Entry Point for Python/PySwip ---
best_move(Player, Board, Move) :-
    minimax(Board, Player, Move, _), !.