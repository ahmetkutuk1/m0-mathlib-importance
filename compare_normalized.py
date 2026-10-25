# compare_normalized.py
import json, math

with open('coq_m0_v2_scores.json', encoding='utf-8') as f:
    extlib = json.load(f)
with open('coq_mathcomp_filtered_m0.json', encoding='utf-8') as f:
    mc = json.load(f)

extlib_map = {r['name']: r for r in extlib}
mc_map = {r['name']: r for r in mc}
common = sorted(set(extlib_map) & set(mc_map))
print(f"common names: {len(common)}")

def rankdata(xs):
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
    mx = sum(xs)/n; my = sum(ys)/n
    num = sum((x-mx)*(y-my) for x,y in zip(xs,ys))
    dx = sum((x-mx)**2 for x in xs)**0.5
    dy = sum((y-my)**2 for y in ys)**0.5
    return num/(dx*dy) if dx>0 and dy>0 else 0.0

def spearman(xs, ys):
    return pearson(rankdata(xs), rankdata(ys))

def perm_test(xs, ys, n_perm=10000):
    """Two-sided permutation test for Spearman rho."""
    import random
    obs = spearman(xs, ys)
    count = 0
    ys2 = list(ys)
    for _ in range(n_perm):
        random.shuffle(ys2)
        if abs(spearman(xs, ys2)) >= abs(obs):
            count += 1
    return obs, count / n_perm

# --- Raw ---
e_raw = [extlib_map[n]['M'] for n in common]
m_raw = [mc_map[n]['M'] for n in common]
rho_raw = spearman(e_raw, m_raw)

# --- Normalize A: divide by mean of ALL nodes in each library ---
e_mean = sum(r['M'] for r in extlib) / len(extlib)
m_mean = sum(r['M'] for r in mc) / len(mc)
print(f"extlib mean M: {e_mean:.4f}, mathcomp mean M: {m_mean:.4f}")
e_normA = [extlib_map[n]['M'] / e_mean for n in common]
m_normA = [mc_map[n]['M'] / m_mean for n in common]
rho_normA = spearman(e_normA, m_normA)

# --- Normalize B: divide by max M ---
e_max = max(r['M'] for r in extlib)
m_max = max(r['M'] for r in mc)
print(f"extlib max M: {e_max:.4f}, mathcomp max M: {m_max:.4f}")
e_normB = [extlib_map[n]['M'] / e_max for n in common]
m_normB = [mc_map[n]['M'] / m_max for n in common]
rho_normB = spearman(e_normB, m_normB)

# --- Normalize C: min-max to [0,1] ---
e_min = min(r['M'] for r in extlib); m_min = min(r['M'] for r in mc)
e_normC = [(extlib_map[n]['M'] - e_min)/(e_max - e_min) for n in common]
m_normC = [(mc_map[n]['M'] - m_min)/(m_max - m_min) for n in common]
rho_normC = spearman(e_normC, m_normC)

# --- Z-score ---
e_var = sum((r['M']-e_mean)**2 for r in extlib)/len(extlib)
m_var = sum((r['M']-m_mean)**2 for r in mc)/len(mc)
e_sd = e_var**0.5; m_sd = m_var**0.5
e_z = [(extlib_map[n]['M']-e_mean)/e_sd for n in common]
m_z = [(mc_map[n]['M']-m_mean)/m_sd for n in common]
rho_z = spearman(e_z, m_z)

print(f"\n=== Spearman rho (n={len(common)}) ===")
print(f"Raw:       {rho_raw:.4f}")
print(f"Norm/max:  {rho_normB:.4f}")
print(f"Norm/mean: {rho_normA:.4f}")
print(f"Min-max:   {rho_normC:.4f}")
print(f"Z-score:   {rho_z:.4f}")

# Permutation test on best variant
obs, p = perm_test(e_normC, m_normC, n_perm=10000)
print(f"\nPermutation test on Min-max: rho={obs:.4f}, p={p:.4f}")

obs_z, p_z = perm_test(e_z, m_z, n_perm=10000)
print(f"Permutation test on Z-score: rho={obs_z:.4f}, p={p_z:.4f}")

# Exclude identity-like noise (eq_refl, max_l, max_r, min_l, min_r, eqb_eq etc. with one-sided zero)
filtered_common = [n for n in common if extlib_map[n]['M'] > 1 and mc_map[n]['M'] > 1]
print(f"\ncommon with both M>1: {len(filtered_common)}")
if len(filtered_common) >= 5:
    e_f = [extlib_map[n]['M'] for n in filtered_common]
    m_f = [mc_map[n]['M'] for n in filtered_common]
    rho_f = spearman(e_f, m_f)
    e_fz = [(extlib_map[n]['M']-e_mean)/e_sd for n in filtered_common]
    m_fz = [(mc_map[n]['M']-m_mean)/m_sd for n in filtered_common]
    rho_fz = spearman(e_fz, m_fz)
    print(f"Filtered raw:    {rho_f:.4f}")
    print(f"Filtered z-score: {rho_fz:.4f}")
    obs_f, p_f = perm_test(e_fz, m_fz, n_perm=10000)
    print(f"Permutation test on filtered z-score: rho={obs_f:.4f}, p={p_f:.4f}")