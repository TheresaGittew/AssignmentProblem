- "PrimalDualAlgo" :    Main file, including multiple examples used for testing purposes.
  Here, the pd_assign_algo_new starts the primal dual algorithm that solves primal / restricted
  by using gurobi; pd_algo_without_gurobi is a function that performs the auction without the
  primal / dual
- NEW_RestrictedProblems / NEW_UnrestrDual : Formulations of linear problems as needed for parts
  of the algorithms
- NEW_AlgoWithoutGurobi: Contains single steps for Method to implement the pd auction without solving lps
- Testing: Tests pd_algo_without_gurobi against pd_assign_algo_new with randomly selected input data sets