import itertools
import math
import numpy as np


def find_supply (supply, current_set):
    res =  sum(supply[i] for i in current_set)
    return res


def find_demand (unique_demands_with_count, current_dem_set):
    return sum((s[1]) for s in unique_demands_with_count if set((s[0])) <= set((current_dem_set)))


def create_new_iter_obj(input_list, len_perm_output_list):
    return itertools.permutations(input_list, len_perm_output_list)

def iter_obj_to_list(dem_set_iter_obj):
    chain_of_sets = sorted(list(set(itertools.chain.from_iterable(list(dem_set_iter_obj)))))
    return chain_of_sets


def get_price_and_profit_vector(current_set, supply, D_r):

    price_impr_vector = {}
    for i in range(len(supply)):
        price_impr_vector[i] = 1 if i in current_set else 0

    profit_impr_vector = {}
    for i in range(len(D_r)):
        profit_impr_vector[i] = -1 if set(D_r[i]) <= set(current_set) else 0

    return profit_impr_vector, price_impr_vector

def get_max_iterations(D_r):
    res = sum (np.prod([j for j in range(i, (len(D_r) +1))]) for i in range(1, len(D_r) + 1))
    return res

def find_smallest_overdem_set(supply, D_r):

    # sort entries in D_r, such that it doesn't matter if bidder states [3,4] or [4,3]
    D_r = [sorted(i) for i in D_r]

    unique_demands_from_infl_bid = [list(x) for x in set(tuple(x) for x in D_r)]  # removes duplicates

    unique_demands_with_count = [(i, D_r.count(i)) for i in
                      unique_demands_from_infl_bid]  # counts how often these sets occur (set, #occurences)

    cache_demand_sets = {}

    len_perm_list = 1
    iter_obj = create_new_iter_obj(unique_demands_from_infl_bid, len_perm_list)

    max_iterations = get_max_iterations(D_r)

    for i in range(max_iterations + 1):

        current_dem_set = next(iter_obj, None)

        if current_dem_set is None:
            len_perm_list += 1
            iter_obj = create_new_iter_obj(unique_demands_from_infl_bid, len_perm_list)
            current_dem_set = next(iter_obj, None) # wenn hier jetzt wieder [] rauskommt, liefert create_new_iter-obj ncihts, weil länge des output arrays zu groß

        if current_dem_set is None:
            return None         # we finish in case there is no new algorithm to be computed

        else:
            # current_dem_set is still a iterable object that, when converted to a list, also can return multiple lists
            # after round 2. So we have to convert it into a concatenated, unique (e.g. sorted) list
            # or, transform the list for the dict. into a tuple
            dem_set_as_chain = iter_obj_to_list(current_dem_set)
            dem_set_as_tuple = tuple(dem_set_as_chain)
            if not (dem_set_as_tuple in cache_demand_sets):
                total_demand = find_demand(unique_demands_with_count, dem_set_as_chain)
                total_supply = find_supply(supply, dem_set_as_chain)
                cache_demand_sets[dem_set_as_tuple] = (total_demand, total_supply)
                if total_demand > total_supply:
                    return get_price_and_profit_vector(dem_set_as_chain, supply, D_r)

            # if we already have that set in the dict, we know that it's feasible and can move on.
