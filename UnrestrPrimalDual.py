import gurobipy as gp
from gurobipy import GRB

# ---------------------------------------------------------------------------------------------
#  Primal Model


def primal(gm, N, G, values, supply):
    # Add decision variables
    y = {}
    for i in N:
        for j in G:
            y[i, j] = gm.addVar(name='Y'+str(i)+str(j))

    # Add constraints
    for i in N:
        gm.addConstr(sum(y[i, j] for j in G) <= 1)  # max 1. assigned good per Person

    for j in G:
        gm.addConstr(sum(y[i, j] for i in N) <= supply[j])  # max. amount of available goods

    gm.setObjective(sum(sum(values[i][j] * y[i, j] for j in G) for i in N), GRB.MAXIMIZE)
    gm.optimize()

    # Retrieve results
    for d in gm.getVars():
        if d.x != 0: print(d.varName, " | Result: ", d.x)

# --------------------------------------------------------------------------------------------
# Dual Problem


def dual(gm, N, G, values, supply):
    p = {}
    r = {}
    for i in N:
        p[i] = gm.addVar(name='person'+str(i),lb=0)

    for j in G:
        r[j] = gm.addVar(name='price'+str(j),lb=0)

    # Add constraints
    for i in N:
        for j in G:
            gm.addConstr(p[i] + r[j] >= values[i][j])
            # hier vektor überkreuz, d.h. legt man preis r für j fest,
            # muss der wert des gutes j für i minus preis r kleiner gleich sein als
            # der profit, den i bereits macht.
            # daher ist der profit oben für gut 4 auch so hoch;
            # da sonst bei einem anderen bidder (z.B. 1)  gelten würde:
            # 6 + 0 ! >= 7
            # Der Preis muss daher so hoch sein, dass es sich für sämtliche weitere Bieter,
            # die dieses Gut nicht erhalten, nicht lohnt, dieses Gut zu kaufen.

    gm.setObjective(sum(p[i] for i in N) + sum(supply[j] * r[j] for j in G), GRB.MINIMIZE)
    gm.setParam('Method', 0)
    gm.optimize()

    # Retrieve results
    for d in gm.getVars():
        if d.x != 0: print(d.varName, " | Result: ", d.x)

# --------------------------------------------------------------
# Dual problem => Find feasible dual solution for given price vector

# adds a value to a set_1 if value fulfills condition, otherwise to set 2
def append_sets(bool, value, set_1, set_2):
    if bool:
        return set_1 + [value], set_2
    else:
        return set_1, set_2 + [value]


def generate_feasible_dual(N, G, values, supply, r_j, p_given=None):
    # r_j : price of item j
    # p_i : benefit of user i

    if not p_given: p = [max(max(values[i][j] - r_j[j] for j in G), 0) for i in N] # profit of a person
    else: p = p_given

    obj = sum(p[i] for i in N) + sum(supply[j] * r_j[j] for j in G)

    # compute sets
    N_b = []
    N_f = []
    G_b = []
    G_f = []
    Z_zero = []
    Z_n = []

    for i in N:
        N_f, N_b = append_sets((True if p[i] == 0 else False), i, N_f, N_b)          # constraints in primal have slack or not

    for j in G:
        G_f, G_b = append_sets((True if r_j[j] == 0 else False), j, G_f, G_b)         # constraints in primal have slack or not

    for i in N:
        for j in G:
            Z_zero, Z_n = append_sets((True if p[i] + r_j[j] > values[i][j] else False), [i,j], Z_zero, Z_n)

    sets = [N_b, N_f, G_b, G_f, Z_zero, Z_n]

    return p, r_j, obj, sets

