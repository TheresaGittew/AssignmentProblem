from gurobipy import GRB

# --------------------------------------------------------------
# Complementary Slackness Conditions
# if y[i, j] > 0 in the primal, then r_j + p_i in the dual (binding constraint)


def restr_primal(gm, N, G, D_r, supply):
    y = {}
    z = {}

    for i in N:
        for j in G:
            y[i, j] = gm.addVar(name='Y'+str(i)+str(j), lb=0)

    for i in N:
        z[i] = gm.addVar(name='z'+str(i), lb=0)


# constraints
    for i in N:
        for j in (set(G) - set(D_r[i])):
            gm.addConstr(y[i, j] == 0)

    for i in N:
        gm.addConstr(sum(y[i, j] for j in G) + z[i] == 1)

    for j in G:
        gm.addConstr(sum(y[i, j] for i in N) <= supply[j])

    gm.setObjective(sum(z[i] for i in N), GRB.MINIMIZE)
    gm.setParam('OutputFlag', False)
    gm.optimize()

    return gm.objVal, gm.getVars()


def restr_dual(gm, N, G, D_r, supply):

    q = {}
    s = {}

    for i in N:
        q[i] = gm.addVar(name='q' + str(i), lb=-100, ub=1)

    for j in G:
        s[j] = gm.addVar(name='s' + str(j), ub=0, lb=-100)

    for i in N:
        for j in D_r[i]:
            gm.addConstr(q[i] + s[j] <= 0)

    gm.setObjective(sum(q[i] for i in N) + sum(supply[j] * s[j] for j in G), GRB.MAXIMIZE)
    gm.setParam('Method', 0)
    gm.setParam('OutputFlag', False)
    gm.optimize()

    # Retrieve results - - - - - - - - - - - - - - - - - - - - - - - -
    q_results = {}
    s_results = {}

    for d in gm.getVars():

        if 'q' in d.varName:
            q_results[d.varName] = d.x
        if 's' in d.varName:
            s_results[d.varName] = d.x

    return gm.objVal, q_results, s_results



