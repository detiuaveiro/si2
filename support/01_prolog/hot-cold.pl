% World feedback logic (Unchanged)
perceive_hint(Secret, Guess, hot) :- Guess > Secret, !.  % "hot" means guess is too high
perceive_hint(Secret, Guess, cold) :- Guess < Secret, !. % "cold" means guess is too low
perceive_hint(Secret, Guess, found) :- Guess =:= Secret.

% Actions with limits (Min and Max)
% act(Hint, CurrentGuess, CurrentMin, CurrentMax, NextGuess, NewMin, NewMax)
act(hot, Guess, Min, _, NextGuess, Min, NewMax) :-
    NewMax is Guess - 1,                   % The secret must be lower than the guess
    NextGuess is (Min + NewMax) // 2.      % Calculate new midpoint

act(cold, Guess, _, Max, NextGuess, NewMin, Max) :-
    NewMin is Guess + 1,                   % The secret must be higher than the guess
    NextGuess is (NewMin + Max) // 2.      % Calculate new midpoint

% Starter function to define initial boundaries
smart_solve(Secret, MinLimit, MaxLimit) :-
    InitialGuess is (MinLimit + MaxLimit) // 2,
    solve(Secret, InitialGuess, MinLimit, MaxLimit).

% Base Case
solve(Secret, Guess, _, _) :-
    perceive_hint(Secret, Guess, found),
    write('Goal Reached: '), write(Guess), !.

% Recursive Step
solve(Secret, Guess, Min, Max) :-
    perceive_hint(Secret, Guess, Hint),
    write('Perception: '), write(Hint), write(' | Guessed: '), write(Guess), nl,
    act(Hint, Guess, Min, Max, NextGuess, NewMin, NewMax),
    solve(Secret, NextGuess, NewMin, NewMax).