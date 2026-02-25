move(1, Source, Target, _) :-
    write('Move top disk from '), write(Source), 
    write(' to '), write(Target), nl.

move(N, Source, Target, Auxiliary) :-
    N > 1,
    M is N - 1,
    move(M, Source, Auxiliary, Target), 
    move(1, Source, Target, _),         
    move(M, Auxiliary, Target, Source). 