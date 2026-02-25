even(0).
even(N) :- N > 0, Prev is N - 2, even(Prev).
