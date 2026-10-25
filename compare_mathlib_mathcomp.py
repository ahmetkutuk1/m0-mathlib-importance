# compare_mathlib_mathcomp.py
import json

with open('mathlib_m0_independent.json', encoding='utf-8') as f:
    ml = json.load(f)
with open('coq_mathcomp_filtered_m0.json', encoding='utf-8') as f:
    mc = json.load(f)

# Filter Mathlib to lemma+theorem only
ml_filtered = {r['name']: r for r in ml if r['kind'] in ('theorem', 'lemma')}
mc_map = {r['name']: r for r in mc}

print(f"Mathlib (lemma+theorem): {len(ml_filtered)}")
print(f"MathComp: {len(mc_map)}")

common = sorted(set(ml_filtered) & set(mc_map))
print(f"Common names: {len(common)}")

def rankdata(xs):
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    ranks = [0.0]*len(xs); i = 0
    while i < len(order):
        j = i
        while j+1 < len(order) and xs[order[j+1]] == xs[order[i]]: j += 1
        avg = (i+j)/2.0 + 1
        for k in range(i, j+1): ranks[order[k]] = avg
        i = j+1
    return ranks
def pearson(xs, ys):
    n = len(xs); mx = sum(xs)/n; my = sum(ys)/n
    num = sum((x-mx)*(y-my) for x,y in zip(xs,ys))
    dx = sum((x-mx)**2 for x in xs)**0.5; dy = sum((y-my)**2 for y in ys)**0.5
    return num/(dx*dy) if dx>0 and dy>0 else 0.0
def spearman(xs, ys): return pearson(rankdata(xs), rankdata(ys))

if len(common) < 5:
    print("Too few common names.")
else:
    ml_m = [ml_filtered[n]['M'] for n in common]
    mc_m = [mc_map[n]['M'] for n in common]
    print(f"Raw Spearman: {spearman(ml_m, mc_m):.4f}")
    
    # Filter to both M>0
    filt = [n for n in common if ml_filtered[n]['M'] > 0 and mc_map[n]['M'] > 0]
    print(f"Both M>0: {len(filt)}")
    if len(filt) >= 5:
        ml_f = [ml_filtered[n]['M'] for n in filt]
        mc_f = [mc_map[n]['M'] for n in filt]
        print(f"Filtered Spearman: {spearman(ml_f, mc_f):.4f}")
        print("\nSample common (top 20 by Mathlib M):")
        for n in sorted(filt, key=lambda x: -ml_filtered[x]['M'])[:20]:
            print(f"  {n}: ML M={ml_filtered[n]['M']:.2f} (D={ml_filtered[n]['D']}) | MC M={mc_map[n]['M']:.2f} (D={mc_map[n]['D']})")