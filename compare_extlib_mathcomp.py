# compare_extlib_mathcomp.py
import json

with open('coq_m0_v2_scores.json', encoding='utf-8') as f:
    extlib = json.load(f)
with open('coq_mathcomp_filtered_m0.json', encoding='utf-8') as f:
    mc = json.load(f)

extlib_map = {r['name']: r for r in extlib}
mc_map = {r['name']: r for r in mc}

common = sorted(set(extlib_map) & set(mc_map))
print(f"extlib nodes: {len(extlib_map)}")
print(f"mathcomp nodes: {len(mc_map)}")
print(f"common names: {len(common)}")

def rankdata(xs):
    # average ranks for ties
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    ranks = [0.0] * len(xs)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and xs[order[j+1]] == xs[order[i]]:
            j += 1
        avg = (i + j) / 2.0 + 1
        for k in range(i, j + 1):
            ranks[order[k]] = avg
        i = j + 1
    return ranks

def pearson(xs, ys):
    n = len(xs)
    mx = sum(xs) / n
    my = sum(ys) / n
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    dx = sum((x - mx) ** 2 for x in xs) ** 0.5
    dy = sum((y - my) ** 2 for y in ys) ** 0.5
    return num / (dx * dy) if dx > 0 and dy > 0 else 0.0

def spearman(xs, ys):
    return pearson(rankdata(xs), rankdata(ys))

if len(common) < 5:
    print("Too few common names for meaningful correlation.")
else:
    e_m = [extlib_map[n]['M'] for n in common]
    m_m = [mc_map[n]['M'] for n in common]
    rho = spearman(e_m, m_m)
    print(f"Spearman rho: {rho:.4f}")
    print(f"\nTop 15 common by extlib M:")
    for n in sorted(common, key=lambda x: -extlib_map[x]['M'])[:15]:
        e = extlib_map[n]; m = mc_map[n]
        print(f"  {n}: extlib M={e['M']:.2f} (D={e['D']}, F={e['F']}) | mathcomp M={m['M']:.2f} (D={m['D']}, F={m['F']})")
    print(f"\nTop 15 common by mathcomp M:")
    for n in sorted(common, key=lambda x: -mc_map[x]['M'])[:15]:
        e = extlib_map[n]; m = mc_map[n]
        print(f"  {n}: extlib M={e['M']:.2f} (D={e['D']}, F={e['F']}) | mathcomp M={m['M']:.2f} (D={m['D']}, F={m['F']})")