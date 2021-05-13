def append_sets(bool, value, set_1, set_2):
    if bool:
        return set_1 + [value], set_2
    else:
        return set_1, set_2 + [value]


def generate_D_r(p, r_j, values, G, i):
    D_r_single = [j for j in G if (p == values[i][j] - r_j[j])]
    return D_r_single


def generate_feasible_dual(N, G, values, supply, r_j, p_given=None):
    # r_j : price of item j
    # p_i : benefit of user i

    if not p_given: p = [max(max(values[i][j] - r_j[j] for j in G), 0) for i in N] # profit of a person
    else: p = p_given

    obj = sum(p[i] for i in N) + sum(supply[j] * r_j[j] for j in G)

    # compute sets
    D_r = [None] * len(N)

    for i in N:
        D_r[i] = generate_D_r(p[i], r_j, values, G, i)

    return p, r_j, obj, D_r