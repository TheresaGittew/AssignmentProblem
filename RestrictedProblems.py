import gurobipy as gp
from gurobipy import GRB

# => sowohl die "slack/tightness"-constraint aus dem dual als auch dessen Entscheidungsvariablen berücksichtigt.


# --------------------------------------------------------------
# Complementary Slackness Conditions
# if y[i, j] > 0 in the primal, then r_j + p_i in the dual (binding constraint)

def restr_primal(gm, N_b, N_f, G_b, G_f, N, G, Z_zero, Z_N, values, supply):
    y = {}
    s_1 = {}
    s_2 = {}
    for i in N:
        for j in G:
            y[i, j] = gm.addVar(name='Y'+str(i)+str(j), lb=0)

    for i in N_b:
        s_1[i] = gm.addVar(name='s1 '+str(i), lb=0)

    for j in G_b:
        s_2[j] = gm.addVar(name='s2 ' +str(j), lb=0)

# constraints
    for i in N_b:
        gm.addConstr(sum(y[i, j] for j in G) + s_1[i] == 1)

    for i in N_f:
        gm.addConstr(sum(y[i, j] for j in G) == 1)

    for j in G_b:
        gm.addConstr(sum(y[i, j] for i in N) + s_2[j] == supply[j])

    for j in G_f:
        gm.addConstr(sum(y[i, j] for i in N) <= supply[j])

    gm.setObjective(sum(-s_1[i] for i in N_b) + sum(-s_2[j] for j in G_b) + (sum(-y[d[0], d[1]] for d in Z_zero)), GRB.MAXIMIZE)
    gm.setParam('OutputFlag',False)
    gm.optimize()

    return gm.objVal, gm.getVars()

# ----------------------------------------------------------------
# => used to find a vector that improves the original vector from the dual.

def restr_dual (gm, N_b, N_f, G_b, G_f, N, G, Z_zero, Z_N, values, supply):
    phi = {} # dual dec. var, corresponds to all i elem N constraints in primal
    rho = {} # dual dec. var, corresponds to all j elem G constraints in primal
    for i in N:
        phi[i] = gm.addVar(name='phi' + str(i), lb=-100)

    for j in G:
        rho[j] = gm.addVar(name='rho' + str(j), lb=-100)

    # Add constraints - - - - - - - - - - - - - - - - - - - - - - - -
    #print("Nb", N_b)
    for i in N_b:
        gm.addConstr(phi[i] >= -1)

    for j in G_b:
        gm.addConstr(rho[j] >= -1)

    #print("N f" , N_f)
    # for i in N_f:
    #     gm.addConstr(phi[i] >= 0)

    for j in G_f:
        gm.addConstr(rho[j] >= 0)

    #print("Z zero" , Z_zero)
    for d in Z_zero: # der, der nichts abkriegt
        gm.addConstr(phi[d[0]] + rho[d[1]] >= -1)

    for d in Z_N: # die beiden ,die ein y zugeteilgt bekommen haben
        gm.addConstr(phi[d[0]] + rho[d[1]] >= 0)


    gm.setObjective((sum(phi[i] for i in N) + sum(rho[j] for j in G)), GRB.MINIMIZE)
    gm.setParam('Method', 0)
    gm.setParam('OutputFlag', False)
    gm.optimize()

    # Retrieve results - - - - - - - - - - - - - - - - - - - - - - - -
    phi_results = {}
    rho_results = {}

    for d in gm.getVars():
        if 'rho' in d.varName:
            rho_results[d.varName] = d.x
        if 'phi' in d.varName:
            phi_results[d.varName] = d.x

    return gm.objVal, phi_results, rho_results
