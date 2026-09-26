"""Independent 3P3-free and P9-free matching-cut threshold oracles."""

import argparse
import json
import random
import subprocess
import sys
from collections import deque
from itertools import combinations,product
from pathlib import Path

import z3


def adjacency(instance):
    neighbors = [set() for _ in range(instance["vertices"])]
    for u,v in instance["edges"]:
        neighbors[u].add(v)
        neighbors[v].add(u)
    return neighbors


def connected_simple(instance):
    if not isinstance(instance,dict):
        return False
    n,edges,k = instance.get("vertices"),instance.get("edges"),instance.get("bound")
    if (type(n) is not int or n < 1 or type(k) is not int or k < 0
            or not isinstance(edges,list)):
        return False
    seen_edges = set()
    for edge in edges:
        if (not isinstance(edge,list) or len(edge) != 2
                or any(type(v) is not int or not 0 <= v < n for v in edge)
                or edge[0] == edge[1]):
            return False
        key = tuple(sorted(edge))
        if key in seen_edges:
            return False
        seen_edges.add(key)
    neighbors = adjacency(instance)
    seen,queue = {0},deque([0])
    while queue:
        for v in neighbors[queue.popleft()]:
            if v not in seen:
                seen.add(v)
                queue.append(v)
    return len(seen) == n


def contains_3p3(instance):
    if instance["vertices"] < 9:
        return False
    neighbors = adjacency(instance)
    paths = set()
    for center in range(instance["vertices"]):
        for u,w in combinations(neighbors[center],2):
            if w not in neighbors[u]:
                paths.add((min(u,w),center,max(u,w)))
    for three in combinations(paths,3):
        sets = [set(path) for path in three]
        if len(set.union(*sets)) != 9:
            continue
        if all(v not in neighbors[u] for i in range(3) for j in range(i+1,3)
               for u in sets[i] for v in sets[j]):
            return True
    return False


def contains_p9(instance):
    if instance["vertices"] < 9:
        return False
    neighbors = adjacency(instance)

    def extend(path):
        if len(path) == 9:
            return True
        for v in neighbors[path[-1]]:
            if v in path or any(v in neighbors[u] for u in path[:-1]):
                continue
            if extend(path+[v]):
                return True
        return False

    return any(extend([start]) for start in range(instance["vertices"]))


def legal_source(source):
    return connected_simple(source) and not contains_3p3(source)


def legal_target(target):
    return connected_simple(target) and not contains_p9(target)


def direct_cut(instance,side):
    n = instance["vertices"]
    if (not isinstance(side,list) or len(side) != n
            or any(type(value) is not bool for value in side)
            or not any(side) or all(side)):
        return False
    crossing = [(u,v) for u,v in instance["edges"] if side[u] != side[v]]
    return (1 <= len(crossing) <= instance["bound"]
            and all(sum(side[u] != side[v] for v in neighbors) <= 1
                    for u,neighbors in enumerate(adjacency(instance))))


def cut_solutions(instance,source=False,limit=3):
    if not (legal_source(instance) if source else legal_target(instance)):
        raise ValueError("Illegal matching-cut threshold instance")
    n = instance["vertices"]
    side = [z3.Bool(f"side_{v}") for v in range(n)]
    solver = z3.Solver()
    solver.add(z3.Or(*side),z3.Or(*[z3.Not(value) for value in side]))
    crossing = [z3.If(side[u] != side[v],1,0) for u,v in instance["edges"]]
    solver.add(z3.Sum(*crossing) >= 1,z3.Sum(*crossing) <= instance["bound"])
    for u,neighbors in enumerate(adjacency(instance)):
        solver.add(z3.Sum(*[z3.If(side[u] != side[v],1,0) for v in neighbors]) <= 1)
    outputs = []
    while len(outputs) < limit:
        result = solver.check()
        if result == z3.unsat:
            break
        if result != z3.sat:
            raise RuntimeError(f"Inconclusive matching-cut solver: {result}")
        model = solver.model()
        bits = [z3.is_true(model.eval(value)) for value in side]
        if not direct_cut(instance,bits):
            raise AssertionError("Z3 cut violates direct threshold")
        outputs.append({"side":bits})
        solver.add(z3.Or(*[value != bit for value,bit in zip(side,bits)]))
    return outputs or [{"status":"NO-SOLUTION"}]


def solve_source(source):
    return cut_solutions(source,source=True,limit=1)[0]


def solve_target(target):
    return cut_solutions(target,source=False,limit=1)[0]


def valid_source(source,output):
    if not legal_source(source) or not isinstance(output,dict):
        return False
    if output == {"status":"NO-SOLUTION"}:
        return solve_source(source) == output
    return set(output) == {"side"} and direct_cut(source,output["side"])


def valid_target(target,output):
    if not legal_target(target) or not isinstance(output,dict):
        return False
    if output == {"status":"NO-SOLUTION"}:
        return solve_target(target) == output
    return set(output) == {"side"} and direct_cut(target,output["side"])


def exhaustive_cut(instance):
    for bits in product((False,True),repeat=instance["vertices"]):
        if direct_cut(instance,list(bits)):
            return {"side":list(bits)}
    return {"status":"NO-SOLUTION"}


def self_test():
    from generate_cases import EDGE_CASES,random_source
    from test_oracle import test_hand_cases

    root = Path(__file__).resolve().parents[3]
    path = Path(__file__).with_name("cases.json")
    subprocess.run([sys.executable,str(root/"research/validate_preparation.py"),str(path)],check=True,cwd=root)
    cases = json.loads(path.read_text())
    for source,expected in EDGE_CASES:
        assert ("side" in solve_source(source)) == expected
    for case in cases:
        source = case["source"]
        if case["kind"] == "random":
            assert random_source(case["seed"]) == source
        current = solve_source(source)
        assert ("side" in current) == ("side" in case["expected"]) == ("side" in exhaustive_cut(source))
        assert valid_source(source,current) and valid_source(source,case["expected"])
    test_hand_cases()
    checked,seen = 0,set()
    for seed in range(160):
        rng = random.Random(seed)
        n = rng.randint(2,8)
        edges = [[0,v] for v in range(1,n)]
        edges += [[u,v] for u in range(1,n) for v in range(u+1,n) if rng.randrange(2)]
        k = rng.randint(0,n)
        target = {"vertices":n,"edges":edges,"bound":k}
        key = json.dumps(target,sort_keys=True)
        if key not in seen and legal_target(target):
            seen.add(key)
            assert ("side" in solve_target(target)) == ("side" in exhaustive_cut(target))
            checked += 1
    print(f"Self-test passed: {len(cases)} independently labelled source cases and {checked} exhaustive P9-free target thresholds")


def candidate_check(path):
    self_test()
    cases = json.loads(Path(__file__).with_name("cases.json").read_text())
    recovered = 0
    for case in cases:
        source = case["source"]
        forward = subprocess.run([sys.executable,str(path)],input=json.dumps(source),text=True,capture_output=True,check=True)
        target = json.loads(forward.stdout)
        if not legal_target(target):
            raise AssertionError(f"Illegal P9-free target: {target}")
        for output in cut_solutions(target):
            if not valid_target(target,output):
                raise AssertionError(f"Invalid target oracle output: {output}")
            payload = {"source":source,"target_solution":output}
            extraction = subprocess.run([sys.executable,str(path),"--extract"],input=json.dumps(payload),text=True,capture_output=True,check=True)
            recovered_output = json.loads(extraction.stdout)
            if not valid_source(source,recovered_output):
                raise AssertionError(f"Invalid recovery from {output}: {recovered_output}")
            recovered += 1
    print(f"Candidate check passed: {len(cases)} source cases, {recovered} target outputs")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--self-test",action="store_true")
    group.add_argument("--candidate",type=Path)
    args = parser.parse_args()
    if args.self_test:
        self_test()
    else:
        candidate_check(args.candidate)
