% 1. Family Facts
parent(abraham, homer).
parent(mona, homer).
parent(homer, bart).
parent(homer, lisa).
parent(homer, maggie).
parent(marge, bart).
parent(marge, lisa).
parent(marge, maggie).
parent(bart, bart_jr). % Made up 4th generation

% 2. Basic Rules
sibling(X, Y) :- parent(Z, X), parent(Z, Y), X \= Y.
grandparent(X, Y) :- parent(X, Z), parent(Z, Y).

% 3. Recursive Rules (Ancestor)
ancestor(X, Y) :- parent(X, Y).
ancestor(X, Y) :- parent(X, Z), ancestor(Z, Y).

% 4. Arithmetic (Factorial)
factorial(0, 1).
factorial(N, Result) :- 
    N > 0, 
    N1 is N - 1, 
    factorial(N1, R1), 
    Result is N * R1.

% 5. List Length
list_length([], 0).
list_length([_|T], L) :- list_length(T, L1), L is L1 + 1.

% 6. List Membership
is_member(X, [X|_]).
is_member(X, [_|T]) :- is_member(X, T).

% 7. List Concatenation
concat_lists([], L, L).
concat_lists([H|T], L2, [H|R]) :- concat_lists(T, L2, R).

% 8. Reverse List
reverse_list([], []).
reverse_list([H|T], Reversed) :- 
    reverse_list(T, RevT), 
    concat_lists(RevT, [H], Reversed).

% 9. Maximum in a List
max_in_list([X], X).
max_in_list([H|T], Max) :- 
    max_in_list(T, TailMax), 
    (H > TailMax -> Max = H ; Max = TailMax).

% 10. Pathfinding in a Graph
edge(a, b). edge(b, c). edge(c, d). edge(b, e).
path(X, Y) :- edge(X, Y).
path(X, Y) :- edge(X, Z), path(Z, Y).