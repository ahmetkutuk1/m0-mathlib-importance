# mathlib_m0_independent.py
import json, math
from collections import Counter
from datasets import load_dataset

print("Loading MathNetwork/MathlibGraph metrics...")
ds = load_dataset('MathNetwork/MathlibGraph', data_files='v2/declaration/metrics.csv', split='train')
print(f"Total nodes: {len(ds)}")
print(f"Kind distribution: {Counter(ds['kind']).most_common()}")

# Compute M_0 for ALL nodes (we'll filter later if needed)
results = []
for r in ds:
    if not r['name']:
        continue
    D = r['in_degree'] or 0
    F = r['out_degree'] or 0
    M = D * math.sqrt(1 + F) * math.exp(-F / 50.0)
    results.append({
        'name': r['name'],
        'kind': r['kind'],
        'M': M,
        'D': D,
        'F': F,
        'pagerank': r['pagerank'],
        'betweenness': r['betweenness'],
        'module': r['module'],
    })

print(f"\nComputed M_0 for {len(results)} nodes")

# Top 25 (all kinds)
results.sort(key=lambda x: x['M'], reverse=True)
print("\n--- Mathlib M_0 (independent, ALL kinds) Top 25 ---")
for i, r in enumerate(results[:25], 1):
    print(f"{i}. {r['name']} [{r['kind']}] (M: {r['M']:.2f}, D: {r['D']}, F: {r['F']})")

# Now filter to proven statements only (lemma/theorem)
KEEP_KINDS = {'lemma', 'theorem'}
filtered = [r for r in results if r['kind'] in KEEP_KINDS]
print(f"\nProven statements only (lemma+theorem): {len(filtered)}")
print("\n--- Mathlib M_0 (independent, lemma+theorem) Top 25 ---")
for i, r in enumerate(filtered[:25], 1):
    print(f"{i}. {r['name']} [{r['kind']}] (M: {r['M']:.2f}, D: {r['D']}, F: {r['F']})")

print(f"\nFiltered stats: D>0: {sum(1 for r in filtered if r['D']>0)}, Max D: {max(r['D'] for r in filtered)}, Max F: {max(r['F'] for r in filtered)}")

with open('mathlib_m0_independent.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print("\nSaved to 'mathlib_m0_independent.json'.")