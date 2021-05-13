import UnrestrPrimalDual as ap
import RestrictedProblems as rps
import gurobipy as gp
import NEW_UnrestrDual as nfd
import NEW_RestrictedProblems as nr

def print_results_sets_NEW (p, r, D, obj, rpt=False):
    print("\n - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -")
    if not rpt: print("Step 1: Find a feasible dual solution y")
    else:
        print("Step 1 (Repeat): Find a feasible dual solution y")
    print("Dual variable p_j's: ", p)
    print("Dual variable r_j's: ", r)
    print("Objective: ", obj)
    print("Set D: " , D)



def print_result_sets(N_b, N_f, G_b, G_f, Z_n, Z_zero, p, r, obj, rpt=False):
    print("\n - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -")
    if not rpt: print("Step 1: Find a feasible dual solution y")
    else: print("Redo: Find a feasible dual solution y")
    print("Dual variable p_i's: ",p)
    print("Dual variable r_j's: ",r)
    print("Objective: ", obj)
    print("\n**Set Results:**")
    print("i's in Set N^B (so p_i > 0): ", N_b, "  |\ni's in Set N^f (so p_i == 0):", N_f)
    print("j's in Set G^B (so r_j > 0): ", G_b, "  |\nj's in Set G^f (so r_j == 0):", G_f)
    print("Z_(i,j), where it should hold: (so Y_i_j > 0): ", Z_n, "  |\nZ_zero, where it should hold: (so Y_i_j = 0):", Z_zero)

def print_results_rp(objVal, vars):
    print("\n- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -")
    print("Step 2: Check if this solution is optimal, using the restricted primal")
    print("\nResults:")
    print("ObjVal:: " , objVal)
    for d in vars:
        if d.x != 0: print(d.varName, " | Result: ", d.x)

def print_results_rdp(objVal, phi_results, rho_results):
    print("\n - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -")
    print("Step 3: Compute solution of restricted dual for finding the improvement vector")
    print("Objective: ", objVal)
    print("Q results:", phi_results)
    print("S results", rho_results)

#test

def pd_assign_algo(N, G, values, supply, r_start, print_out=True):
    # Step 1 - create feasible dual solution
    p_i, r_j, obj, ([N_b, N_f, G_b, G_f, Z_zero, Z_n])  = ap.generate_feasible_dual(N,G,values, supply, r_start)
    if print_out: print_result_sets(N_b, N_f, G_b, G_f, Z_n, Z_zero, p_i, r_j, obj)

    # Step 2 - use restricted primal
    gm_1 = gp.Model()
    objVal_rp, vars = rps.restr_primal(gm_1, N_b, N_f, G_b, G_f, N, G, Z_zero, Z_n, values, supply)
    if print_out: print_results_rp(objVal_rp, vars)

    # Step 3 - compute z* vector with restricted dual
    while (objVal_rp != 0):
        print ("\n- - - - * * * * Start new Iteration * * * * - - - - - - - -\n")

        gm_2 = gp.Model()
        objVal_rd, phis_z, rhos_z = rps.restr_dual(gm_2, N_b, N_f, G_b, G_f, N, G, Z_zero, Z_n, values, supply)
        if print_out: print_results_rdp(objVal_rd, phis_z, rhos_z)
        p_i_new = [a + b for a, b in zip(p_i, phis_z.values())]
        r_j_new =[a + b for (a,b) in zip(r_j, rhos_z.values())]

        # Back to Step 2: Find sets with dual
        p_i, r_j, obj, ([N_b, N_f, G_b, G_f, Z_zero, Z_n]) = ap.generate_feasible_dual(N,G,values, supply, r_j_new, p_i_new)
        if print_out: print_result_sets(N_b, N_f, G_b, G_f, Z_n, Z_zero, p_i, r_j, obj, True)

        # Use restricted primal to evaluate new solution
        gm_1 = gp.Model()
        objVal_rp, vars = rps.restr_primal(gm_1, N_b, N_f, G_b, G_f, N, G, Z_zero, Z_n, values, supply)
        if print_out: print_results_rp(objVal_rp, vars )



def pd_assign_algo_new(N, G, values, supply, r_start, print_out=True):

    # Step 1 - create feasible dual solution
    p, r_j, obj, D_r = nfd.generate_feasible_dual(N, G, values, supply, r_start)
    if print_out: print_results_sets_NEW(p=p, r=r_j, D=D_r, obj=obj)

    # Step 2 - use restricted primal
    gm_1 = gp.Model()
    objVal_rp, vars = nr.restr_primal(gm_1, N, G, D_r, supply)
    if print_out: print_results_rp(objVal_rp, vars)

    # Step 3 - compute z* vector with restricted dual
    while (objVal_rp != 0):
        print("\n- - - - * * * * Start new Iteration * * * * - - - - - - - -\n")

        gm_2 = gp.Model ()
        objVal_rd, q_results, s_results = nr.restr_dual(gm=gm_2, N=N, G=G, D_r=D_r, supply=supply)
        if print_out: print_results_rdp(objVal_rd, q_results, s_results)
        p_i_new = [a - b for a, b in zip(p, q_results.values())]
        r_j_new = [a - b for (a, b) in zip(r_j, s_results.values())]

        # Back to Step 1: Find sets with the dual
        p, r_j, obj, D_r = nfd.generate_feasible_dual(N, G, values, supply, r_j_new, p_i_new)
        if print_out: print_results_sets_NEW(p, r_j, D_r, obj, True)

        # Back to Step 2: use restricted Primal to evaluate solution
        gm_3 = gp.Model ()
        objVal_rp, vars = nr.restr_primal(gm_3, N, G, D_r, supply)
        if print_out: print_results_rp(objVal_rp, vars)






v = [[1, 1, 4, 7, 6], [2, 2, 3, 9, 5], [3, 0, 4, 8, 2]]
s = [1, 3, 5, 2, 1]

v2 = [[1, 1, 4, 7, 6, 10], [2, 2, 3, 9, 5, 11], [3, 0, 4, 8, 2, 13], [3, 5, 4, 3, 2, 11]]
s2 = [1, 3, 5, 2, 1, 1]

#pd_assign_algo(N=[0,1,2,3],G=[0,1,2,3,4,5],values=v2, supply=s2, r_start=[0, 0, 0, 0, 0, 0])
#
gm_3 = gp.Model()
ap.primal(gm_3, [0,1,2,3], [0,1,2,3,4,5], v2, s2)

pd_assign_algo_new(N=[0,1,2,3],G=[0,1,2,3,4,5],values=v2, supply=s2, r_start=[0, 0, 0, 0, 0, 0])

v = [[1, 1, 4, 7, 6], [2, 2, 3, 9, 5], [3, 0, 4, 8, 2]]
s = [1, 3, 5, 2, 1]

v2 = [[1, 1, 4, 7, 6, 10], [2, 2, 3, 9, 5, 11], [3, 0, 4, 8, 2, 13], [3, 5, 4, 3, 2, 11]]
s2 = [1, 3, 5, 2, 1, 1]

pd_assign_algo(N=[0,1,2,3],G=[0,1,2,3,4,5],values=v2, supply=s2, r_start=[0, 0, 0, 0, 0, 0])
#

print("\n* * * * * * Compare: True solution with gurobi : ")
gm_3 = gp.Model()
ap.primal(gm_3, [0,1,2,3], [0,1,2,3,4,5], v2, s2)
