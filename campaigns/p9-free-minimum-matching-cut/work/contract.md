# Prepared input and output contract

Source and target inputs are `{"vertices": n, "edges": [[u,v], ...], "bound": k}`: a connected simple undirected graph on `0..n-1`, with `n >= 1` and integer `k >= 0`. The source is induced-`3P3`-free; the target is induced-`P9`-free. These are threshold instances. A positive output is `{"side": [bool, ...]}` for a nontrivial vertex bipartition with between 1 and `k` crossing edges and at most one crossing edge at each vertex. `{"status": "NO-SOLUTION"}` is valid exactly when no such cut exists.

A candidate `algorithm.py` reads source JSON from stdin and writes legal target JSON to stdout. With `--extract`, it reads `{"source": source, "target_solution": output}` and writes a valid source output. The commands share no memory, exit nonzero on errors and send diagnostics to stderr. They must be deterministic and polynomial time; recovery must work for every valid target cut or negative answer.

`check.py --candidate PATH` independently solves each constructed target on the fixed source corpus and directly validates recovered source cuts. It checks up to three target outputs per instance, including the negative output when the target has no cut.
