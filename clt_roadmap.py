import pandas as pd
from datasets import load_dataset
import networkx as nx

print("Loading M_0 scores...")
scores_df = pd.read_csv("M_0_final_ranked.csv")
score_dict = dict(zip(scores_df['name'], scores_df['M']))
field_dict = dict(zip(scores_df['name'], scores_df['field']))

print("Loading graph...")
edges_ds = load_dataset('MathNetwork/MathlibGraph', data_files='mathlib_edges.csv', split='train')
edges_df = edges_ds.to_pandas()

print("Building DAG...")
G = nx.from_pandas_edgelist(
    edges_df[edges_df['is_explicit'] == True], 
    source='source', target='target', create_using=nx.DiGraph()
)

# CLT'nin temel yapı taşları (Mathlib'deki isimleri)
clt_keywords = ["gaussian", "normal", "char", "moment", "variance", "independence", "dist", "measure", "integral", "probability", "tendsto"]

print("\n--- CENTRAL LIMIT THEOREM ROADMAP ---")
print("Target: Prove that a sum of independent, identically distributed (i.i.d.) random variables tends to a normal distribution.\n")

# 1. Mevcut Olasılık ve Gaussian Teoremleri
prob_nodes = [n for n, f in field_dict.items() if f in ["ProbabilityTheory", "MeasureTheory"] and any(k in n.lower() for k in clt_keywords)]
top_prob = sorted([(n, score_dict.get(n,0)) for n in prob_nodes], key=lambda x: x[1], reverse=True)[:10]

print("1. Foundation Layer: Existing Probability & Measure Theory")
print("   (These are the tools you will use to build the proof)")
for n, s in top_prob:
    print(f"   - {n} (M: {s:.2f})")

# 2. Eksik Bağlantılar (Graf üzerinde birbirine bağlı olmayan ama olması gerekenler)
print("\n2. Missing Links: The Gap")
print("   (The graph shows these components are weakly connected. You need to bridge them.)")
# Örnek: En yüksek M_0'lı Gaussian teoreminin kaç tane alt komşusu var?
if prob_nodes:
    top_node = top_prob[0][0]
    print(f"   - Check if '{top_node}' has lemmas connecting to 'MeasureTheory.integral'")
    print(f"   - Look for: `ProbabilityTheory.IsGaussian.tendsto_...` (This is the missing link for CLT)")

# 3. Tavsiye Edilen İnşa Sırası
print("\n3. Recommended Construction Order:")
print("   a) Define the sum of i.i.d. random variables.")
print("   b) Prove the characteristic function of a normal distribution.")
print("   c) Prove Levy's Continuity Theorem (or equivalent weak convergence tool).")
print("   d) Combine (a), (b), and (c) to prove the CLT.")
print("\nDone.")