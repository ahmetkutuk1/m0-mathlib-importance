import pandas as pd
from datasets import load_dataset
import networkx as nx

print("1. Loading M_0 scores...")
scores_df = pd.read_csv("M_0_scores.csv")

# Check for 'field' column (if not present, fallback to final_ranked)
if 'field' not in scores_df.columns:
    print("Warning: 'field' not found in M_0_scores.csv. Using M_0_final_ranked.csv instead.")
    scores_df = pd.read_csv("M_0_final_ranked.csv")

score_dict = dict(zip(scores_df['name'], scores_df['M']))
field_dict = dict(zip(scores_df['name'], scores_df.get('field', ['Unknown']*len(scores_df))))

print("2. Loading graph data (edges)...")
edges_ds = load_dataset('MathNetwork/MathlibGraph', data_files='mathlib_edges.csv', split='train')
edges_df = edges_ds.to_pandas()

print("3. Building DAG...")
G = nx.from_pandas_edgelist(
    edges_df[edges_df['is_explicit'] == True], 
    source='source', target='target', create_using=nx.DiGraph()
)

# Target theorems and their specific Mathlib field/keyword mappings
targets = {
    "47 Central Limit Theorem": {
        "fields": ["ProbabilityTheory", "MeasureTheory"],
        "keywords": ["normal", "gaussian", "central_limit", "tendsto_inDistribution"]
    },
    "41 Puiseux's Theorem": {
        "fields": ["Polynomial", "Algebra", "Valuation"],
        "keywords": ["puiseux", "fractional_power", "root_series"]
    },
    "61 Ceva's Theorem": {
        "fields": ["Geometry", "EuclideanGeometry"],
        "keywords": ["ceva", "concurrent", "ratio_division"]
    },
    "84 Morley's Theorem": {
        "fields": ["Geometry", "EuclideanGeometry"],
        "keywords": ["morley", "trisect", "equilateral"]
    },
    "92 Pick's Theorem": {
        "fields": ["Geometry", "Combinatorics"],
        "keywords": ["pick", "lattice_point", "polygon_area"]
    },
    "53 pi is transcendental": {
        "fields": ["NumberTheory", "Algebra", "Analysis"],
        "keywords": ["transcendental", "pi", "algebraic_independent"]
    },
    "56 Hermite-Lindemann": {
        "fields": ["NumberTheory", "Algebra"],
        "keywords": ["hermite", "lindemann", "transcendental", "exp_algebraic"]
    }
}

print("\n--- DISCOVERY ENGINE V2 (Field and Keyword Filtered) ---")
for name, info in targets.items():
    print(f"\n[{name}] Analysis:")
    
    # 1. Filter theorems by target field
    field_nodes = [n for n in G.nodes() if field_dict.get(n, "Unknown") in info["fields"]]
    
    # 2. Filter field theorems by keyword matching
    related_nodes = [n for n in field_nodes if any(k.lower() in n.lower() for k in info["keywords"])]
    
    if not related_nodes:
        print("  -> No specific match found in this field yet (might be genuinely missing).")
        # Show the highest M_0 theorems in this field (field 'center')
        top_in_field = sorted([(n, score_dict.get(n,0)) for n in field_nodes], key=lambda x: x[1], reverse=True)[:3]
        print("  -> Top M_0 theorems in this field:")
        for n, s in top_in_field:
            print(f"     * {n} (M: {s:.2f})")
        continue

    # 3. Look at neighbors of matched nodes
    candidates = set()
    for node in related_nodes:
        # Only consider neighbors within the same field to reduce noise
        for pred in G.predecessors(node):
            if field_dict.get(pred, "") in info["fields"]:
                candidates.add(pred)
        for succ in G.successors(node):
            if field_dict.get(succ, "") in info["fields"]:
                candidates.add(succ)
                
    scored_candidates = [(c, score_dict.get(c, 0)) for c in candidates if c in score_dict]
    scored_candidates.sort(key=lambda x: x[1], reverse=True)
    
    if scored_candidates:
        print(f"  -> Matched theorems: {related_nodes[:2]}")
        print("  -> Highest M_0 scoring neighbors (new discovery candidates):")
        for cand, score in scored_candidates[:3]:
            print(f"     * {cand} (M: {score:.2f})")
    else:
        print("  -> No scored candidates found in the neighborhood.")