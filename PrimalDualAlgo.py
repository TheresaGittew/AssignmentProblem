import Z_Depr_UnrestrPrimalDual as ap
import Z_Depr_RestrictedProblems as rps
import gurobipy as gp
import NEW_UnrestrDual as nfd
import NEW_RestrictedProblems as nr
import Z_Depr_WithoutGRB as wgrb
import New_Algo_Without_Gurobi as wgrbn
import numpy as np
import time


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
    print("Q results:", phi_results) # phi = profit improvement
    print("S results", rho_results) # rho = price improvement


def pd_assign_algo_new(N, G, values, supply, r_start, print_out=False):

    # Step 1 - create feasible dual solution
    p, r_j, obj, D_r = nfd.generate_feasible_dual(N, G, values, supply, r_start)
    if print_out: print_results_sets_NEW(p=p, r=r_j, D=D_r, obj=obj)

    # Step 2 - use restricted primal if gurobi is used; otherwise obtain result from the corresponding method
    gm_1 = gp.Model()
    objVal_rp, vars = nr.restr_primal(gm_1, N, G, D_r, supply)
    if print_out: print_results_rp(objVal_rp, vars)

    # Step 3 - compute z* vector with restricted dual
    while (objVal_rp != 0):
        if print_out: print("\n- - - - * * * * Start new Iteration * * * * - - - - - - - -\n")

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

    return p, r_j, obj


def pd_algo_without_gurobi(N, G, values, supply, r_start, print_out=False):   # r_start sind die Preisvektoren, mit denen es anfängt (alles 0)
    # Step 1 - create feasible dual solution
    profits, prices, obj, D_r = nfd.generate_feasible_dual(N, G, values, supply, r_start)
    if print_out: print_results_sets_NEW(p=profits, r=prices, D=D_r, obj=obj)

    # Step 2 & 3- find improvement vector & objValue
    res = wgrb.find_smallest_overdem_set(supply, D_r)

    while res is not None:
        profit_impr_vector, price_impr_vector = res
        obj_val = (sum(profit_impr_vector[i] for i in N) + sum(supply[j] * price_impr_vector[j] for j in G))
        if print_out: print_results_rp(obj_val, [])
        if print_out: print_results_rdp(obj_val, profit_impr_vector, price_impr_vector)

        # calculate new prices
        profits = np.add(np.array(profits), np.array(list(profit_impr_vector.values())))
        prices = np.add(np.array(prices), np.array(list(price_impr_vector.values())))

        if print_out : print("\n- - - - * * * * Start new Iteration * * * * - - - - - - - -\n")
        profits, prices, obj, D_r = nfd.generate_feasible_dual(N, G, values, supply, prices.tolist(), profits.tolist())
        if print_out : print_results_sets_NEW(p=profits, r=prices, D=D_r, obj=obj)

        res = wgrbn.find_smallest_overdem_set(supply, D_r)

    if print_out: print("Final result: Profits ", profits, " Prices: ", prices)
    obj_sol = (sum(profits[i] for i in N) + sum(supply[j] * prices[j] for j in G))
    if print_out: print("Obj val: ", obj_sol)
    return profits, prices, obj_sol




v = [[1, 1, 4, 7, 6], [2, 2, 3, 9, 5], [3, 0, 4, 8, 2]]
s = [1, 3, 5, 2, 1]

v2 = [[1, 1, 4, 7, 6, 10], [2, 2, 3, 9, 5, 11], [3, 0, 4, 8, 2, 13], [3, 5, 4, 3, 2, 11]] # 4 bidders, # 6 goods / items
s2 = [1, 3, 5, 2, 1, 1] # supply / availability

N=[0, 1, 2, 3, 4, 5]
G=[0, 1, 2, 3, 4]
v3=[[11, 18, 10, 12, 8], [2, 1, 7, 9, 0], [5, 13, 7, 5, 16], [24, 12, 5, 5, 6], [17, 10, 4, 11, 6], [1, 26, 17, 1, 23]]
s3=[1.0, 3.0, 1.0, 3.0, 1.0]

N=[0, 1, 2, 3, 4, 5]
G=[0, 1, 2, 3]
v3=[[9, 8, 0, 18], [12, 3, 14, 15], [7, 9, 2, 7], [9, 19, 28, 15], [24, 28, 22, 7], [21, 29, 21, 25]]
v4=[1.0, 1.0, 5.0, 1.0]

N=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
G=[0, 1, 2, 3, 4, 5, 6]
v4=[[13, 25, 11, 14, 17, 12, 23], [10, 4, 11, 19, 2, 16, 14], [13, 2, 20, 27, 3, 22, 11], [18, 8, 26, 23, 21, 24, 21], [21, 28, 1, 17, 29, 17, 7], [9, 0, 27, 9, 9, 20, 24], [12, 22, 20, 24, 3, 16, 11], [5, 6, 25, 11, 4, 2, 5], [12, 5, 3, 14, 21, 11, 6], [14, 7, 25, 2, 0, 28, 15], [11, 20, 22, 9, 12, 23, 22]]
s4=[7.0, 1.0, 7.0, 1.0, 1.0, 1.0, 1.0]


N=[0, 1, 2, 3, 4, 5, 6, 7]
G=[0, 1, 2, 3, 4, 5, 6, 7, 8]
v5=[[17, 21, 14, 12, 15, 4, 14, 0, 18], [9, 23, 24, 17, 24, 1, 10, 1, 0], [4, 27, 14, 26, 1, 9, 23, 11, 20], [2, 1, 26, 21, 6, 23, 18, 4, 27], [8, 20, 2, 12, 17, 7, 22, 10, 27], [27, 11, 7, 3, 19, 16, 7, 21, 3], [24, 9, 9, 26, 23, 12, 2, 15, 13], [23, 4, 19, 15, 11, 21, 9, 6, 22]]
s5=[1, 1, 1, 1, 1, 6.0, 4.0, 1, 1]



N = [0, 1, 2, 3, 4, 5, 6, 7, 8]
G = [0, 1, 2, 3, 4, 5, 6]
v6 = [[22, 4, 24, 1, 10, 28, 9], [8, 0, 27, 11, 12, 23, 28], [0, 27, 22, 0, 12, 16, 0], [26, 14, 22, 0, 2, 15, 20], [7, 2, 27, 7, 29, 1, 16], [6, 27, 4, 16, 10, 0, 6], [9, 1, 29, 15, 7, 2, 29], [4, 9, 14, 19, 21, 3, 25], [4, 4, 27, 8, 21, 9, 28]]
s6 = [1.0, 4.0, 1.0, 1.0, 1.0, 1.0, 1.0]

pd_algo_without_gurobi(N=N, G=G, values=v6, supply=s6, r_start=[0, 0, 0, 0, 0, 0, 0], print_out=True)




# gm_3 = gp.Model()
# ap.primal(gm_3, [0,1,2,3], [0,1,2,3,4,5], v2, s2)
#
#profits, prices, result = pd_assign_algo_new(N=N,G=G,values=v6, supply=s6, r_start=[0, 0, 0, 0, 0, 0, 0], print_out=True)
#print("profits : ", profits, " | prices : " , prices , " | result : " , result)
#
# v = [[1, 1, 4, 7, 6], [2, 2, 3, 9, 5], [3, 0, 4, 8, 2]]
# s = [1, 3, 5, 2, 1]

# v2 = [[1, 1, 4, 7, 6, 10], [2, 2, 3, 9, 5, 11], [3, 0, 4, 8, 2, 13], [3, 5, 4, 3, 2, 11]]
# s2 = [1, 3, 5, 2, 1, 1]

#pd_assign_algo(N=[0,1,2,3],G=[0,1,2,3,4,5],values=v2, supply=s2, r_start=[0, 0, 0, 0, 0, 0])
#

# print("\n* * * * * * Compare: True solution with gurobi : ")
# gm_3 = gp.Model()
# #ap.primal(gm_3, [0,1,2,3], [0,1,2,3,4,5], v2, s2)
#
#
# res =  np.add([1,2,3],[3,4,5])
# print("here" , res)
