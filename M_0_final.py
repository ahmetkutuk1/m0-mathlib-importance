"""
M_0 FINAL — On altı turun özeti.
Formül: M(S) = D(S) * sqrt(1 + F(S)) * exp(-F(S)/50)
"""
import pandas as pd
from collections import defaultdict
import math, sys
sys.setrecursionlimit(100000)

def compute_M(csv_path=None):
    url = csv_path or "https://huggingface.co/datasets/MathNetwork/MathlibGraph/resolve/main/mathlib_edges.csv"
    edges = pd.read_csv(url)
    deps, users = defaultdict(set), defaultdict(set)
    for s, t in zip(edges["source"], edges["target"]):
        deps[s].add(t); users[t].add(s)
    def field_of(n):
        p = n.split(".")
        return p[0] if len(p) >= 2 else "_root_"
    def is_noise(n):
        return n.startswith(("inst", "Mathlib.Meta.", "Mathlib.Tactic.", "Lean.", "Std.")) or ".to" in n or ".inst" in n
    in_fields = {n: len({field_of(u) for u in us}) for n, us in users.items()}
    memo = {}
    def longest(n, visiting=None):
        if n in memo: return memo[n]
        if visiting is None: visiting = set()
        if n in visiting: return 0
        visiting.add(n)
        best = max((longest(t, visiting) for t in deps.get(n, ())), default=0)
        visiting.remove(n)
        memo[n] = 1 + best
        return memo[n]
    results = {}
    for n in set(deps) | set(users):
        if is_noise(n): continue
        d = longest(n); f = in_fields.get(n, 0)
        if d > 1 and f < 100:
            results[n] = d * math.sqrt(1 + f) * math.exp(-f / 50)
    return results

if __name__ == "__main__":
    print("M_0 hesaplanıyor (10-15 dk)...")
    M = compute_M()
    print(f"Toplam düğüm: {len(M)}")
    top = sorted(M.items(), key=lambda x: -x[1])[:20]
    print("\n=== Top 20 M_0 ===")
    for n, m in top:
        print(f"{m:7.2f}  {n}")
    # CSV olarak da kaydet
    df = pd.DataFrame(M.items(), columns=["name", "M"])
    df.to_csv("M_0_scores.csv", index=False)
    print("\nM_0_scores.csv kaydedildi.")