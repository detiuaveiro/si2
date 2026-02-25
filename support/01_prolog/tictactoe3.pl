% --- 1. Game State Evaluation ---

% Winning lines (indices on a 3x3 board)
line(0, 1, 2). line(3, 4, 5). line(6, 7, 8). 
line(0, 3, 6). line(1, 4, 7). line(2, 5, 8). 
line(0, 4, 8). line(2, 4, 6).

% Define opponents
opponent(x, o).
opponent(o, x).

% Check if a specific player has won the game
win(Board, Player) :-
    line(I, J, K),
    nth0(I, Board, Player),
    nth0(J, Board, Player),
    nth0(K, Board, Player).

% Check if the game is a draw (no empty 'e' spaces left)
draw(Board) :- \+ nth0(_, Board, e).

% --- 2. State Generation ---

% Helper to replace an element at a specific index to simulate a move
replace([_|T], 0, X, [X|T]).
replace([H|T], I, X, [H|R]) :-
    I > 0, I1 is I - 1, replace(T, I1, X, R).

% Generate a valid next board state by finding an empty spot and playing in it
move(Board, Index, Player, NextBoard) :-
    nth0(Index, Board, e),
    replace(Board, Index, Player, NextBoard).

% --- 3. The Alpha-Beta Negamax Algorithm ---
% minimax(Board, Player, Alpha, Beta, BestMove, BestScore)
% Alpha: The best guaranteed score we can get so far.
% Beta: The worst score the opponent can force us into.

% Base Case 1: The current player has already won (Score = 1)
minimax(Board, Player, _, _, nil, 1) :- win(Board, Player), !.

% Base Case 2: The opponent has won (Score = -1)
minimax(Board, Player, _, _, nil, -1) :- opponent(Player, Opp), win(Board, Opp), !.

% Base Case 3: The game is a draw (Score = 0)
minimax(Board, _, _, _, nil, 0) :- draw(Board), !.

% Recursive Step: Evaluate possible moves using Alpha-Beta window
minimax(Board, Player, Alpha, Beta, BestMove, BestScore) :-
    opponent(Player, Opp),
    % Find all possible valid moves from this board state
    findall(Move, nth0(Move, Board, e), Moves),
    % Start evaluating moves. Initial BestMove is nil, Initial BestScore is incredibly low (-2)
    evaluate_moves(Moves, Board, Player, Opp, Alpha, Beta, nil, -2, BestMove, BestScore).

% --- 4. Move Evaluation & Pruning Loop ---
% evaluate_moves(MovesList, Board, Player, Opp, Alpha, Beta, CurrentBestMove, CurrentBestScore, FinalBestMove, FinalBestScore)

% Base Case: No more moves to evaluate, return the best we found.
evaluate_moves([], _, _, _, _, _, BestMove, BestScore, BestMove, BestScore).

% Recursive Step: Try a move, see how the opponent responds, and decide to prune or continue.
evaluate_moves([Move|RestMoves], Board, Player, Opp, Alpha, Beta, CurrentBestMove, CurrentBestScore, FinalBestMove, FinalBestScore) :-
    
    % 1. Simulate the move
    move(Board, Move, Player, NextBoard),
    
    % 2. Ask the opponent to evaluate this new board.
    % In Negamax, the opponent's Alpha is our -Beta, and their Beta is our -Alpha!
    NewAlpha is -Beta,
    NewBeta is -Alpha,
    minimax(NextBoard, Opp, NewAlpha, NewBeta, _, OppScore),
    
    % 3. Our score is the exact opposite of the opponent's score
    Score is -OppScore,

    % 4. ALPHA-BETA PRUNING CHECK
    ( Score >= Beta ->
        % PRUNE! This move is so good for us that the opponent will never allow 
        % this game state to happen. Stop searching immediately.
        FinalBestMove = Move,
        FinalBestScore = Score
    ;
        % NO PRUNE: Check if this move is better than our current best
        ( Score > CurrentBestScore ->
            NextBestMove = Move,
            NextBestScore = Score,
            % Update our Alpha (our guaranteed safety net)
            NextAlpha is max(Alpha, Score)
        ;
            % Keep the old best move/score/alpha
            NextBestMove = CurrentBestMove,
            NextBestScore = CurrentBestScore,
            NextAlpha = Alpha
        ),
        % 5. Continue evaluating the rest of the available moves
        evaluate_moves(RestMoves, Board, Player, Opp, NextAlpha, Beta, NextBestMove, NextBestScore, FinalBestMove, FinalBestScore)
    ).

% --- 5. Main Entry Point for Python/PySwip ---

% Start the search with Alpha = -2 and Beta = 2 (since Tic-Tac-Toe scores only go from -1 to 1)
best_move(Player, Board, Move) :-
    minimax(Board, Player, -2, 2, Move, _), !.