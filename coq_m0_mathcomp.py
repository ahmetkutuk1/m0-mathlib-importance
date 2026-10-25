# coq_m0_mathcomp.py
import json, math
from collections import defaultdict
from datasets import load_dataset

print("Loading Coq-MathComp (phanerozoic)...")
ds = load_dataset('phanerozoic/Coq-MathComp', split='train')

# Nodes = all symbolic_name
node_names = set(n for n in ds['symbolic_name'] if n)
print(f"Nodes: {len(node_names)}")

# Edges: (user, dep), only if dep in node_names (ratio was 1.0, so all should pass)
edges = set()
for row in ds:
    user = row['symbolic_name']
    if not user or not row['deps']:
        continue
    for dep in row['deps']:
        if dep and dep in node_names and dep != user:
            edges.add((user, dep))
print(f"Edges: {len(edges)}")

# In-degree (D) and out-degree (F)
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
    results.append((name, M, D, F))

results.sort(key=lambda x: x[1], reverse=True)

print("\n--- Coq MathComp M_0 Top 20 ---")
for i, (name, M, D, F) in enumerate(results[:20], 1):
    print(f"{i}. {name} (M: {M:.4f}, D: {D}, F: {F})")

print(f"\nTotal nodes: {len(results)}")
print(f"D>0: {sum(1 for _,_,D,_ in results if D>0)}")
print(f"D=0: {sum(1 for _,_,D,_ in results if D==0)}")
print(f"F>0: {sum(1 for _,_,_,F in results if F>0)}")
print(f"Max D: {max(D for _,_,D,_ in results)}")
print(f"Max F: {max(F for _,_,_,F in results)}")

with open('coq_mathcomp_m0_scores.json', 'w', encoding='utf-8') as f:
    json.dump([{'name': n, 'M': m, 'D': D, 'F': F} for n, m, D, F in results],
              f, ensure_ascii=False, indent=2)
print("\nSaved to 'coq_mathcomp_m0_scores.json'.")