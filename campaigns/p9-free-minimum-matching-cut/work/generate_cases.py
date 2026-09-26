"""Reproducible connected 3P3-free matching-cut threshold instances."""

import json
import random
from pathlib import Path


def graph(n,edges,bound):
    return {"vertices":n,"edges":sorted(edges),"bound":bound}


def clique(n):
    return [[u,v] for u in range(n) for v in range(u+1,n)]


EDGE_CASES = [
    (graph(1,[],0),False),
    (graph(2,[[0,1]],0),False),
    (graph(2,[[0,1]],1),True),
    (graph(3,[[0,1],[1,2]],1),True),
    (graph(3,clique(3),1),False),
    (graph(4,clique(4),2),False),
    (graph(4,[[0,1],[1,2],[2,3],[0,3]],1),False),
    (graph(4,[[0,1],[1,2],[2,3],[0,3]],2),True),
    (graph(4,[[0,1],[1,2],[2,3]],1),True),
    (graph(5,clique(4)+[[0,4]],1),True),
    (graph(6,clique(3)+[[3,4],[3,5],[4,5],[2,3]],1),True),
    (graph(8,[[i,i+1] for i in range(7)],1),True),
    (graph(8,[[0,i] for i in range(1,8)],1),True),
    (graph(9,[[i,i+1] for i in range(8)],1),True),
]


def random_source(seed):
    rng = random.Random(seed)
    if seed % 2 == 0:
        a,b = rng.randint(2,4),rng.randint(2,4)
        edges = [[i,i+1] for i in range(a-1)]
        edges += [[i,i+1] for i in range(a,a+b-1)]
        edges += [[a-1,a]]
        edges += [[u,v] for u in range(a) for v in range(u+2,a) if rng.randrange(2)]
        edges += [[u,v] for u in range(a,a+b) for v in range(u+2,a+b) if rng.randrange(2)]
        bound = rng.randint(1,3)
        return graph(a+b,edges,bound)
    n = rng.randint(5,8)
    edges = clique(n)
    removed = rng.sample(edges,rng.randint(0,2))
    return graph(n,[edge for edge in edges if edge not in removed],rng.randint(0,2))


def build_cases():
    from check import solve_source
    cases,seen = [],set()

    def add(source,kind,seed=None,hand_answer=None):
        key = json.dumps(source,sort_keys=True,separators=(",", ":"))
        if key in seen:
            return False
        answer = solve_source(source)
        if hand_answer is not None and ("side" in answer) != hand_answer:
            raise AssertionError(f"Hand label disagrees with oracle: {source}")
        seen.add(key)
        case = {"source":source,"kind":kind,"expected":answer}
        if seed is not None:
            case["seed"] = seed
        cases.append(case)
        return True

    for source,expected in EDGE_CASES:
        add(source,"edge",hand_answer=expected)
    seed = 0
    while sum(case["kind"] == "random" for case in cases) < 100:
        add(random_source(seed),"random",seed=seed)
        seed += 1
    return cases


if __name__ == "__main__":
    path = Path(__file__).with_name("cases.json")
    cases = build_cases()
    path.write_text(json.dumps(cases,indent=2)+"\n")
    print(f"Wrote {len(cases)} cases to {path}")
