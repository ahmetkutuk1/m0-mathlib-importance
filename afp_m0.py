import json
import networkx as nx
from collections import defaultdict
import math

print("Loading AFP metadata...")
with open('afp_metadata.json', 'r', encoding='utf-8') as f:
    entries = json.load(f)

print(f"Total AFP entries: {len(entries)}")

# Extract entry names and their dependencies
sessions = {}
topics_map = {}
for entry in entries:
    name = entry['session']
    deps = entry.get('dependencies', [])
    topics = entry.get('topics', [])
    sessions[name] = deps
    topics_map[name] = set(topics)

# Create directed graph (A -> B means A depends on B)
G = nx.DiGraph()
for name, deps in sessions.items():
    G.add_node(name)
    for dep in deps:
        if dep in sessions:  # Only internal AFP dependencies
            G.add_edge(name, dep)

print(f"Graph has {len(G.nodes())} entries and {len(G.edges())} dependencies.")

# D: Longest path for each entry
try:
    longest_paths = {}
    for node in G.nodes():
        try:
            # Longest path starting from this node in the DAG
            longest_paths[node] = nx.dag_longest_path_length(G, node)
        except:
            longest_paths[node] = 0
except Exception as e:
    print(f"Longest path calculation error: {e}")
    longest_paths = {node: 0 for node in G.nodes()}

# F: Number of distinct topics (this entry + its transitive dependencies)
def get_diversity(node, visited=None):
    if visited is None:
        visited = set()
    if node in visited:
        return set()
    visited.add(node)
    result = set(topics_map.get(node, set()))
    for dep in G.successors(node):  # Entries this node depends on
        result |= get_diversity(dep, visited)
    return result

print("Calculating diversity (this may take a moment)...")
diversity = {}
for i, node in enumerate(G.nodes()):
    if i % 50 == 0:
        print(f"  {i}/{len(G.nodes())}...")
    diversity[node] = len(get_diversity(node))

# M_0-like score (entry level)
# M = D * sqrt(1+F) * exp(-F/50)
scores = {}
for node in G.nodes():
    D = longest_paths.get(node, 0)
    F = diversity.get(node, 0)
    scores[node] = D * math.sqrt(1 + F) * math.exp(-F / 50)

# Sort and print
sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
print("\n--- AFP M_0 (Entry Level) Top 20 ---")
for i, (name, score) in enumerate(sorted_scores[:20], 1):
    print(f"{i}. {name} (M: {score:.2f}, D: {longest_paths[name]}, F: {diversity[name]})")

# Save results
with open('afp_m0_scores.json', 'w', encoding='utf-8') as f:
    json.dump({name: {'M': scores[name], 'D': longest_paths[name], 'F': diversity[name]} for name in scores}, f, indent=2)
print("\nResults saved to 'afp_m0_scores.json'.")