import PrimalDualAlgo as pda
import unittest
import numpy as np
from numpy import random

# -----------------------------------------------------------------------------------------------
# This section contains methods which generate random input sets which can be used at a later point
# for conducting tests for the pd algorithm implementation variants.

# bimodal performs a random selection of values from a triangular distribution
# source: https://stackoverflow.com/questions/651421/bimodal-distribution-in-c-or-python
# idea: a bimodal distribution reflects the distribution of goods in an auction, where
# some goods (in some cases, highly demanded goods) are scarce and remaining ones are ample,
# but their total number is sufficient to fulfill the demand amounts.


def bimodal(low1, high1, mode1, low2, high2, mode2):
    toss = random.choice((1, 2))
    if toss == 1:
        if low1 == mode1 == high1:     # this happens when more goods than bidders occur, such that av = 1
            return 1
        else:
            return np.round(random.triangular(left=low1, mode=mode1, right=high1))
    else:
        if high2 == low2:
            return 1
        else:
            return np.round(random.triangular(left=low2, mode=mode2, right=high2))

# generate_input_sets finds feasible output data for which we want to test the pd auction implementations, e.g.
# tuples with a random number of goods, bidders, their values, and a supply that provides a feasible solution.
# parameters: number of generated random samples, and upper bounds for N ( # bidders), G (# goods), val ( # bidders' values)


def generate_input_sets(number_samples=1, ub_N=15, ub_G=10, ub_val=30, print_out=False):
    testsets_list = []

    for n in range(number_samples):

        len_N = np.random.randint(1, ub_N)  # set number of bidders
        len_G = np.random.randint(1, ub_G)  # set number of goods

        N = [i for i in range(len_N)]
        G = [j for j in range(len_G)]

        values = [[np.random.randint(0, ub_val) for j in range(len_G)] for i in range(len_N)]

        av = max(len_N/ len_G, 1)
        supply = [0]

        while sum(supply) < len_N: # ensures a feasible solution that total supply is sufficient for given number of bidders
            supply = [bimodal(low1=1,high1=av,mode1=(av + 1)/2,low2=av,high2=len_N, mode2=((av+len_N)/2)) for i in range(len_G)]

        testsets_list.append((N, G, values, supply))
    return testsets_list

# ---------------------------------------------------------------------------------------------------------------------
# This section contains the tests which compare the results of 1) pd assignment algorithm with gurobi and 2) pd
# algorithm without gurobi.


class TestPDAlgo(unittest.TestCase):

    def test_results(self):
        def setup_tests( number_instances):
            return generate_input_sets(number_instances, print_out=False)

        self.number_instances = 10  #  Todo adjust number of instances
        self.list_testsets = setup_tests(self.number_instances)

        # loop through all generated test data instances:
        for i in range(self.number_instances):
            N_set = self.list_testsets[i][0]
            G_set = self.list_testsets[i][1]
            v = self.list_testsets[i][2]
            s = self.list_testsets[i][3]

            r_start = [0 for i in self.list_testsets[i][1]]

            print("Current set: " , self.list_testsets[i])

            profits, prices, obj = pda.pd_assign_algo_new(N=N_set, G=G_set, values=v, supply=s, r_start=r_start, print_out=False )

            profits_2, prices_2, obj_2 = pda.pd_algo_without_gurobi(N=N_set, G=G_set, values=v, supply=s, r_start=r_start, print_out=False)
            #self.assertEqual(profits, profits_2)
            #self.assertEqual(prices, prices_2)
            self.assertEqual(obj, obj_2)

#
if __name__ == '__main__':
    unittest.main()