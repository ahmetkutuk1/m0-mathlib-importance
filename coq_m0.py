from datasets import load_dataset
import networkx as nx
import math
import json

print("Loading Coq data from HuggingFace...")
ds = load_dataset('theostos/pile-of-rocq', 'coq-ext-lib-proofs', split='train')
df = ds.to_pandas()

print(f"Total proofs/lemmas: {len(df)}")

# Build directed graph: name -> axioms (dependencies)
G = nx.DiGraph()
all_names = set(df['name'].dropna().unique())

for _, row in df.iterrows():
    name = row.get('name')
    axioms = row.get('axioms', [])
    if name:
        G.add_node(name)
        if isinstance(axioms, list):
            for ax in axioms:
                # Axioms are strings; check if they are internal names
                if ax in all_names:
                    G.add_edge(name, ax)

print(f"Graph: {len(G.nodes())} nodes, {len(G.edges())} edges")

# D: Longest path (dependency depth)
longest_paths = {}
for node in G.nodes():
    try:
        longest_paths[node] = nx.dag_longest_path_length(G, node)
    except:
        longest_paths[node] = 0

# F: Diversity (out-degree = number of axioms used)
diversity = {node: G.out_degree(node) for node in G.nodes()}

# M_0 score
scores = {}
for node in G.nodes():
    D = longest_paths.get(node, 0)
    F = diversity.get(node, 0)
    scores[node] = D * math.sqrt(1 + F) * math.exp(-F / 50)

# Sort and print
sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
print("\n--- Coq M_0 (Theorem Level, coq-ext-lib) Top 20 ---")
for i, (name, score) in enumerate(sorted_scores[:20], 1):
    print(f"{i}. {name} (M: {score:.2f}, D: {longest_paths[name]}, F: {diversity[name]})")

# Save results
with open('coq_m0_scores.json', 'w', encoding='utf-8') as f:
    json.dump({name: {'M': scores[name], 'D': longest_paths[name], 'F': diversity[name]} for name in scores}, f, indent=2)
print("\nResults saved to 'coq_m0_scores.json'.")