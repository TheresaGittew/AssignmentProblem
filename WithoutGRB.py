import UnrestrPrimalDual as ap
import RestrictedProblems as rps
import gurobipy as gp
import NEW_UnrestrDual as nfd
import NEW_RestrictedProblems as nr
import itertools

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


class unique_element:
    def __init__(self,value,occurrences):
        self.value = value
        self.occurrences = occurrences

def perm_unique(elements):
    eset=set(elements)
    listunique = [unique_element(i,elements.count(i)) for i in eset]
    u=len(elements)
    return perm_unique_helper(listunique,[0]*u,u-1)

def perm_unique_helper(listunique,result_list,d):
    if d < 0:
        yield tuple(result_list)
    else:
        for i in listunique:
            if i.occurrences > 0:
                result_list[d]=i.value
                i.occurrences-=1
                for g in  perm_unique_helper(listunique,result_list,d-1):
                    yield g
                i.occurrences+=1



def find_supply (supply, current_set):
    return sum(supply[i] for i in current_set)


def find_indirect_demand (sum_occurences_sorted, current_set_core):

    return sum((s[2]) for s in sum_occurences_sorted if set((s[1])) < set((current_set_core)))

#remove_duplicates([[4,1],[2],[4,1]])
# Todo: Method returns one currently overdemanded set, for which the price has to be subseuently increased.
# Also, it returns the affected bidders
def find_smallest_overdem_set(supply, D_r):
    current_length = 1

    # sort entries in D_r, such that it doesn't matter if bidder states [3,4] or [4,3]
    D_r = [sorted(i) for i in D_r]

    unique_demands_from_infl_bid = [list(x) for x in set(tuple(x) for x in D_r)]        # removes duplicates

    sum_occurences = [(len(i), i, D_r.count(i)) for i in unique_demands_from_infl_bid]  # counts how often these sets occur (set size, set, #occurences)
    sum_occurences_sorted = sorted(sum_occurences, key= lambda a: a[0])                 # sorts "sum_occurences" according to length of array


    # this is especially challenging for larger sets
    foundImprovement = False
    iterList = iter(sum_occurences_sorted)

    # First round
    for next_set in iterList:
        direct_demand = next_set[2]
        indirect_demand = find_indirect_demand(sum_occurences_sorted, next_set[1]) # finds bidders which demand subsets of current set
        demand = indirect_demand + direct_demand

        supply_of_current_set = find_supply(supply, next_set[1])

        if demand > supply_of_current_set:
            foundImprovement = True
            overdem_set = next_set[1]  # fetches the "true" set of objects which belong to the overdemanded set
            price_impr_vector = {}
            for i in range(len(supply)):
                price_impr_vector[i] = 1 if i in overdem_set else 0

            # Find profit change vector for all bidders
            profit_impr_vector = {}
            for i in range(len(D_r)):
                profit_impr_vector[i] = -1 if set(D_r[i]) <= set(overdem_set) else 0
            break

    # Second round
    # Todo

    # am besten doch erst alle Permutationen ausrechnen und dann der Länge nach ordnen; duplikate rauswerfen
    # dann alle durchrechnen, angefangen vom kleinsten.
    if not foundImprovement:
        for i in range(2, len(sum_occurences_sorted)+ 2) :        #  kann noch viel cleaner gemacht werden, da häufig ähnliche permutationen vorkommen u. sich wiederholen, auch bei varriierenden Werten von i, hat man es meistens vorher schonmal berechnet.
            #print(unique_demands_from_infl_bid)
            results_itertools = list(itertools.permutations(unique_demands_from_infl_bid, i))           # Todo : 2 auf i setzen, Verbesserung für Performance: erst kleine sets mergen

            #print(results_itertools)
            # merge lists
            resulting_list_meta = []
            for a in range(len(results_itertools)):
                resulting_list_sub = []
                for l in range(i):
                    resulting_list_sub = list(set(resulting_list_sub + results_itertools[a][l]))
                resulting_list_meta.append(resulting_list_sub)

            results_list_meta = set ([tuple(sorted(i)) for i in resulting_list_meta])
            #print(results_list_meta)

            for next_set in results_list_meta:
                #print("are here with set " , next_set)


                demand = find_indirect_demand(sum_occurences_sorted, next_set)
               # print("demand ", demand)
                supply_of_current_set = find_supply(supply, next_set)
                #print("demand ", demand, "supply ", supply_of_current_set)


                if demand > supply_of_current_set:
                    foundImprovement = True
                    overdem_set = next_set  # fetches the "true" set of objects which belong to the overdemanded set
                    price_impr_vector = {}
                    for i in range(len(supply)):
                        price_impr_vector[i] = 1 if i in overdem_set else 0

                    # Find profit change vector for all bidders
                    profit_impr_vector = {}
                    for i in range(len(D_r)):
                        profit_impr_vector[i] = -1 if set(D_r[i]) <= set(overdem_set) else 0
                    break




    # Through with everything
    if foundImprovement:
        return profit_impr_vector, price_impr_vector
    else:
        return None

#  [[5], [5], [5], [5]]
#  [[5], [3, 5], [5], [5]]
#  [[3, 5], [3], [5], [5]]
# [[3], [3], [5], [5]]
# [[3], [3], [3, 5], [5]]
# [[3, 4], [3], [3, 5], [1, 5]]


#print(find_smallest_overdem_set(supply=[1, 3, 5, 2, 1, 1] , D_r=[[3, 4], [3], [3, 5], [1, 5]]))



