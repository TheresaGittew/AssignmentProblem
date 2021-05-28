
import itertools


def find_supply (supply, current_set):
    return sum(supply[i] for i in current_set)


def find_indirect_demand (sum_occurences_sorted, current_set_core):
    return sum((s[2]) for s in sum_occurences_sorted if set((s[1])) < set((current_set_core)))

def create_new_iter_obj(input_list, len_perm_output_list):
    return itertools.permutations(input_list, len_perm_output_list)


# Also, it returns the affected bidders
def find_smallest_overdem_set(supply, D_r):

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

    # am besten doch erst alle Permutationen ausrechnen, vlt gibts ne Möglichkeit das lazy zu machen
    res = [list(itertools.permutations(unique_demands_from_infl_bid, i)) for i in range(2, len(sum_occurences_sorted))]


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
                #print("are here with D_r " , D_r)


                demand = find_indirect_demand(sum_occurences_sorted, next_set)
                #print("demand ", demand)
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

D_r = [[1, 8], [2, 4], [1, 3, 6], [2, 8], [8], [0], [3, 4], [0, 5, 8]]

s5=[1, 1, 1, 1, 1, 6.0, 4.0, 1, 1]

print(find_smallest_overdem_set(supply=s5 , D_r=D_r))



