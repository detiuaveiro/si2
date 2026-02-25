:- dynamic bird_y/1.
:- dynamic next_pipe_bottom_y/1.

update_state(BirdY, PipeY) :-
    retractall(bird_y(_)),
    retractall(next_pipe_bottom_y(_)),
    asserta(bird_y(BirdY)),
    asserta(next_pipe_bottom_y(PipeY)).

action(jump) :-
    bird_y(BY),
    next_pipe_bottom_y(PY),
    BY > PY + 40, !. 

action(stay).