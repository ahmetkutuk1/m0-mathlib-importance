# coq_m0_mathcomp_filtered.py
import json, math
from collections import defaultdict
from datasets import load_dataset

KEEP_TYPES = {'Lemma', 'Theorem', 'Fact', 'Corollary', 'Proposition', 'Remark', 'Example'}

print("Loading Coq-MathComp (filtered to proven statements only)...")
ds = load_dataset('phanerozoic/Coq-MathComp', split='train')

# Node set: only proven statements
node_names = set()
node_types = {}
for r in ds:
    if r['type'] in KEEP_TYPES and r['symbolic_name']:
        node_names.add(r['symbolic_name'])
        node_types[r['symbolic_name']] = r['type']

print(f"Nodes (proven statements only): {len(node_names)}")
from collections import Counter
print(f"Type breakdown: {Counter(node_types.values()).most_common()}")

# Edges: (user, dep), both must be in node set
edges = set()
for r in ds:
    user = r['symbolic_name']
    if user not in node_names or not r['deps']:
        continue
    for dep in r['deps']:
        if dep in node_names and dep != user:
            edges.add((user, dep))

print(f"Edges (theorem->theorem only): {len(edges)}")

in_deg = defaultdict(set)
out_deg = defaultdict(set)
for user, dep in edges:
    in_deg[dep].add(user)
    out_deg[user].add(dep)

results = []
for name in node_names:
    D = len(in_deg.get(name, set()))
    F = len(out_deg.get(name, set()))
    M = D * math.sqrt(1 + F) * math.exp(-F / 50.0)
    results.append((name, M, D, F, node_types[name]))

results.sort(key=lambda x: x[1], reverse=True)

print("\n--- Coq MathComp M_0 (filtered) Top 25 ---")
for i, (name, M, D, F, t) in enumerate(results[:25], 1):
    print(f"{i}. {name} [{t}] (M: {M:.4f}, D: {D}, F: {F})")

print(f"\nTotal nodes: {len(results)}")
print(f"D>0: {sum(1 for _,_,D,_,_ in results if D>0)}")
print(f"D=0: {sum(1 for _,_,D,_,_ in results if D==0)}")
print(f"Max D: {max(D for _,_,D,_,_ in results)}")
print(f"Max F: {max(F for _,_,_,F,_ in results)}")

with open('coq_mathcomp_filtered_m0.json', 'w', encoding='utf-8') as f:
    json.dump([{'name': n, 'M': m, 'D': D, 'F': F, 'type': t} for n, m, D, F, t in results],
              f, ensure_ascii=False, indent=2)
print("\nSaved to 'coq_mathcomp_filtered_m0.json'.")