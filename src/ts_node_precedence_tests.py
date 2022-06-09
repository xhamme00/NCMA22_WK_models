# Author: Jan Hammer, xhamme00@stud.fit.vutbr.cz
# Project: WK Grammar Tree Search
# Runs a test using all 20 grammars comparing performance of the tree search using different node precedence heuristics

from lib.perf_tester import cPerfTester
from lib.grammars import *

def main():
	times = 1
	tester = cPerfTester([precedence[0] for precedence in g1.nodePrecedenceList])

	# lengths of inputs for testing grammars in basic form and in CNF
	# suitable lens have been chosen so that the tests run a reasonable amount of time
	allGrammars =   [ g1,   g2,   g3,   g4,   g5,   g6,   g7,   g8,   g9,  g10,  g11,  g12,  g13,  g14,  g15,  g16,  g17,  g18,  g19,  g20]
	lensBasicForm = [500, 1000,  300,   80,  400,  600, 1200, 1200,  200,   60,  200,  400,  500,  400,  400,  400,   18,  300,  300,  380]
	lensCNF =       [300,  800,   13,   40,  400,  600,  600,  800,  120,   60,   20,  400,  300,  400,  400,  200,   14,  200,   70,  380]

	#filter which tests will be run, each grammar has 2 (1 in basic form 1 in CNF)
	runTests = range(1, len(allGrammars) * 2 + 1)
	#runTests = [25, 30]

	testNo = 0
	for grammar, lenBasic, lenCNF in zip(allGrammars, lensBasicForm, lensCNF):
		testNo += 1
		if testNo in runTests:
			inputStr = next(grammar.input_gen_func(lenBasic, 0, True))
			tester.run_node_precedence_test(grammar, inputStr, True, times)

		testNo += 1
		if testNo in runTests:
			grammar.to_wk_cnf()
			inputStr = next(grammar.input_gen_func(lenCNF, 0, True))
			tester.run_node_precedence_test(grammar, inputStr, True, times)

	tester.printResults()

if __name__ == "__main__":
	main()
