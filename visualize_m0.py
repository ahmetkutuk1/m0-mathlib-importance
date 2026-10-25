import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from datasets import load_dataset

print("Loading M_0 scores...")
df = pd.read_csv("M_0_final_ranked.csv")
top_300 = df.nlargest(300, 'M')
top_names = set(top_300['name'])

score_dict = dict(zip(top_300['name'], top_300['M']))
field_dict = dict(zip(top_300['name'], top_300['field']))

print("Loading graph edges from HuggingFace...")
ds = load_dataset('MathNetwork/MathlibGraph', data_files='mathlib_edges.csv', split='train')
edges_df = ds.to_pandas()

# Filter edges where both endpoints are in our top 300 list
filtered_edges = edges_df[edges_df['source'].isin(top_names) & edges_df['target'].isin(top_names)]

print(f"Found {len(filtered_edges)} connections among the Top 300.")

# Create graph
G = nx.from_pandas_edgelist(filtered_edges, 'source', 'target', create_using=nx.DiGraph())

if len(G.nodes()) == 0:
    print("ERROR: No direct connections found among these 300 theorems.")
else:
    print(f"Graph has {len(G.nodes())} nodes and {len(G.edges())} edges. Plotting...")
    
    plt.figure(figsize=(20, 15))
    plt.title("M_0 Significance Map: Top 300 Theorems", fontsize=24, fontweight='bold')

    fields = list(set(field_dict.get(node, 'Unknown') for node in G.nodes()))
    colors = plt.cm.tab20(range(len(fields)))
    color_map = dict(zip(fields, colors))
    node_colors = [color_map[field_dict.get(node, 'Unknown')] for node in G.nodes()]

    node_sizes = [score_dict.get(node, 10) * 15 for node in G.nodes()]

    pos = nx.spring_layout(G, k=0.5, iterations=50)
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=node_sizes, alpha=0.8)
    nx.draw_networkx_edges(G, pos, alpha=0.3, arrows=True, arrowsize=10)

    top_10_names = top_300.nlargest(10, 'M')['name']
    labels = {node: node.split('.')[-1] for node in G.nodes() if node in top_10_names.values}
    nx.draw_networkx_labels(G, pos, labels, font_size=10, font_weight='bold')

    handles = [plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=color_map[f], markersize=10, label=f) for f in fields[:10]]
    plt.legend(handles=handles, title="Fields", loc="upper right")

    plt.axis('off')
    plt.tight_layout()
    plt.savefig("M_0_Significance_Map.png", dpi=300)
    print("Saved image as 'M_0_Significance_Map.png'.")