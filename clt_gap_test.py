import pandas as pd
from datasets import load_dataset
import networkx as nx

print("Loading graph...")
edges_ds = load_dataset('MathNetwork/MathlibGraph', data_files='mathlib_edges.csv', split='train')
edges_df = edges_ds.to_pandas()

print("Building DAG...")
G = nx.from_pandas_edgelist(
    edges_df[edges_df['is_explicit'] == True], 
    source='source', target='target', create_using=nx.DiGraph()
)

# Test: IsGaussian ile MeasureTheory.integral arasındaki en kısa yol
source_node = "ProbabilityTheory.IsGaussian.memLp_id"
target_node = "MeasureTheory.integral"

print(f"\nSearching for path from '{source_node}' to '{target_node}'...")

try:
    # En kısa yolu bul (yönlü graf olduğu için sadece ileri yönlü)
    path = nx.shortest_path(G, source=source_node, target=target_node)
    print(f"Path found! Length: {len(path)} steps")
    for i, node in enumerate(path):
        print(f"  {i+1}. {node}")
except nx.NetworkXNoPath:
    print("No direct path found (the components are disconnected).")
except nx.NodeNotFound as e:
    print(f"Node not found: {e}")