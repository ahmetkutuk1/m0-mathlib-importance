import pandas as pd
from datasets import load_dataset
import networkx as nx

# 1. M_0 Skorlarını Yükle
print("M_0 skorları yükleniyor...")
scores_df = pd.read_csv("M_0_scores.csv")
score_dict = dict(zip(scores_df['name'], scores_df['M']))

# 2. HuggingFace'ten Kenarları Yükle (Önbellekten hızlıca gelir)
print("Graf verisi (kenarlar) yükleniyor...")
edges_ds = load_dataset('MathNetwork/MathlibGraph', data_files='mathlib_edges.csv', split='train')
edges_df = edges_ds.to_pandas()

# 3. Yönlü Graf Oluştur (Sadece explicit olanları alalım)
print("DAG oluşturuluyor...")
G = nx.from_pandas_edgelist(
    edges_df[edges_df['is_explicit'] == True], 
    source='source', target='target', create_using=nx.DiGraph()
)

# 4. Hedef Teoremler (Eksik Wiedijk 100)
# Bu teoremlerin Mathlib'deki en yakın karşılıklarını veya "modül" (ön ek) komşularını bulacağız.
target_keywords = {
    "47 Central Limit": ["probability", "measure", "gaussian", "normal", "limit"],
    "41 Puiseux": ["puiseux", "polynomial", "root", "series", "fractional"],
    "61 Ceva": ["ceva", "triangle", "geometry", "intersect", "ratio"],
    "84 Morley": ["morley", "triangle", "angle", "trisect"],
    "92 Pick": ["pick", "polygon", "area", "lattice", "interior"],
    "53 pi_transcendental": ["pi", "transcendental", "algebraic", "e"],
    "56 Hermite-Lindemann": ["hermite", "lindemann", "transcendental", "exp", "algebraic"]
}

print("\n--- KEŞİF MOTORU SONUÇLARI ---")
for name, keywords in target_keywords.items():
    print(f"\n[{name}] için komşuluk analizi:")
    
    # Anahtar kelimeleri içeren düğümleri bul
    related_nodes = [n for n in G.nodes() if any(k.lower() in n.lower() for k in keywords)]
    
    # Bu düğümleri kullanan veya bunlardan türeyen en yüksek M_0 skorlu teoremleri bul
    candidates = set()
    for node in related_nodes:
        # Gelen komşular (bu düğümün kullandıkları)
        candidates.update(G.predecessors(node))
        # Giden komşular (bunu kullananlar)
        candidates.update(G.successors(node))
        
    # Skorlarına göre sırala
    scored_candidates = [(c, score_dict.get(c, 0)) for c in candidates if c in score_dict]
    scored_candidates.sort(key=lambda x: x[1], reverse=True)
    
    # Top 3 adayı yazdır
    for cand, score in scored_candidates[:3]:
        print(f"  -> Aday: {cand} (M: {score:.2f})")