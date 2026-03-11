from pyswip import Prolog

Prolog.consult("warmup.pl")
for s in Prolog.query("parent(homer,X)"):
    print(f"Homer is the father of {s['X']}")
