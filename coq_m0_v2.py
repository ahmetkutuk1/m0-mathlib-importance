# coq_m0_v2.py
import json
from collections import defaultdict
import math
from datasets import load_dataset

print("Loading Coq data (v2, name-based join)...")
proofs = load_dataset('theostos/pile-of-rocq', 'coq-ext-lib-proofs', split='train')
deps   = load_dataset('theostos/pile-of-rocq', 'coq-ext-lib-step_deps', split='train')

# uid -> name
uid_to_name = {p['proof_uid']: p['name'] for p in proofs if p['name']}
node_names = set(uid_to_name.values())
print(f"Nodes (proofs with name): {len(node_names)}")

# Build edges: (user_name, dep_name), only if both in node_names
edges = set()
for d in deps:
    user = uid_to_name.get(d['proof_uid'])
    dep  = d['name']
    if user and dep and user in node_names and dep in node_names and user != dep:
        edges.add((user, dep))
print(f"Edges (both endpoints in node set): {len(edges)}")

# In-degree: how many distinct theorems use this one
in_deg = defaultdict(set)
out_deg = defaultdict(set)
for user, dep in edges:
    in_deg[dep].add(user)
    out_deg[user].add(dep)

# M_0 = D * sqrt(1+F) * exp(-F/50)
# D = in-degree (distinct users), F = out-degree (distinct deps)
results = []
for name in node_names:
    D = len(in_deg.get(name, set()))
    F = len(out_deg.get(name, set()))
    M = D * math.sqrt(1 + F) * math.exp(-F / 50.0)
    results.append((name, M, D, F))

results.sort(key=lambda x: x[1], reverse=True)

print("\n--- Coq M_0 (name-based join, coq-ext-lib) Top 20 ---")
for i, (name, M, D, F) in enumerate(results[:20], 1):
    print(f"{i}. {name} (M: {M:.4f}, D: {D}, F: {F})")

print(f"\nTotal nodes: {len(results)}")
print(f"Nodes with D>0: {sum(1 for _,_,D,_ in results if D>0)}")
print(f"Nodes with D=0: {sum(1 for _,_,D,_ in results if D==0)}")
print(f"Nodes with F>0: {sum(1 for _,_,_,F in results if F>0)}")

with open('coq_m0_v2_scores.json', 'w', encoding='utf-8') as f:
    json.dump([{'name': n, 'M': m, 'D': D, 'F': F} for n, m, D, F in results],
              f, ensure_ascii=False, indent=2)
print("\nSaved to 'coq_m0_v2_scores.json'.")