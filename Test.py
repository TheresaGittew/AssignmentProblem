import PrimalDualAlgo as pda
import unittest
import random as r
import numpy as np
from math import e
from numpy import random
# Test Instances

def bimodal(low1, high1, mode1, low2, high2, mode2):  # from https://stackoverflow.com/questions/651421/bimodal-distribution-in-c-or-python
    toss = random.choice((1, 2))
    # print("HERE")
    if toss == 1:
        if low1 == mode1 == high1:     # this happens when more goods than bidders occur, such that av = 1
            return 1
        else:
            # print("low", low1)
            # print("high: ", high1)
            # print("mode:", mode1)
            return np.round(random.triangular(left=low1, mode=mode1, right=high1))
    else:
        if high2== low2:
            return 1
        else:
            # print("low2",low2)
            # print("high2: ", high2)
            # print("mode2:" , mode2)
            return np.round(random.triangular(left=low2, mode=mode2, right=high2))

def generate_input_sets(number_samples=1, ub_N=15, ub_G=10, ub_val=30, print_out=False):

    testsets_list = []
    for n in range(number_samples):

        len_N = np.random.randint(1, ub_N)  # set number of bidders
        len_G = np.random.randint(1, ub_G)  # set number of goods

        N = [i for i in range(len_N)]
        G = [j for j in range(len_G)]

        values = [[np.random.randint(0, ub_val) for j in range(len_G)] for i in range(len_N)]

        if print_out: print("next run")
        if print_out: print(len_N, len_G)
        av = max(len_N/ len_G, 1)
        if print_out: print(av)
        supply = [0]

        while sum(supply) < len_N:
            supply = [bimodal(low1=1,high1=av,mode1=(av + 1)/2,low2=av,high2=len_N, mode2=((av+len_N)/2)) for i in range(len_G)]

        if print_out: print("\nThese are the generated input sets:")
        if print_out: print("N: ", N, "\nG: ", G)
        if print_out: print("values: ", values)
        if print_out: print("supply: ", supply)

        testsets_list.append((N, G, values, supply))
    return testsets_list





class TestPDAlgo(unittest.TestCase):


    def setup_tests(self, number_instances):
        self.number_instances = number_instances
        self.list_testsets = generate_input_sets(number_instances, print_out=False)



    def test_results(self):
        self.setup_tests(5)
        print("Test starts")
        for i in range(self.number_instances):
            print("Test ", (i+1), " / ", self.number_instances)
            N_set = self.list_testsets[i][0]
            G_set = self.list_testsets[i][1]
            v= self.list_testsets[i][2]
            s= self.list_testsets[i][3]

            r_start = [0 for i in self.list_testsets[i][1]]

            profits, prices, obj = pda.pd_assign_algo_new(N=N_set, G=G_set, values=v, supply=s, r_start=r_start, print_out=False )

            profits_2, prices_2, obj_2 = pda.pd_algo_without_gurobi(N=N_set, G=G_set, values=v, supply=s, r_start=r_start, print_out=False)
            print("Current set: " , self.list_testsets[i])
            #self.assertEqual(profits, profits_2)
            #self.assertEqual(prices, prices_2)
            self.assertEqual(obj, obj_2)


if __name__ == '__main__':
    unittest.main()