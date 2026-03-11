% Declare state as dynamic so we can retract and assert it on the fly
:- dynamic state/4.

% 1. Entry Point: Updates the world and decides the action
step(PY, PV, PC, PX, Action) :-
    update_world(PY, PV, PC, PX),
    decide(Action).

% 2. Update World State: Clear the old state and save the new one
update_world(PY, PV, PC, PX) :-
    retractall(state(_, _, _, _)),
    assertz(state(PY, PV, PC, PX)).

% 3. Action Logic: Decide whether to 'jump' or 'stay'
% In typical game canvas logic, Y=0 is the top of the screen and Y increases downwards.
% If the birds Y (PY) is greater than the pipe center (PC), it is too low and needs to jump.
decide(jump) :-
    state(PY, _, PC, _),
    PY > PC.

% Otherwise, do nothing (stay).
decide(stay) :-
    state(PY, _, PC, _),
    PY =< PC.
