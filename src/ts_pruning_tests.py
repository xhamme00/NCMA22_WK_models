# Author: Jan Hammer, xhamme00@stud.fit.vutbr.cz
# Project: WK Grammar Tree Search
# Runs a test using all 20 grammars comparing performance of the tree search switching off pruning heristics one at a time

from lib.perf_tester import cPerfTester
from lib.grammars import *

def main():
	times = 1
	# we'll test with all heuristics on, then switch off on at a time, then all off
	tester = cPerfTester(["ALL ON"] + [f'{func.__name__} OFF' for func in g1.pruningOptions] + ["ALL OFF"])

	# lengths of inputs for testing grammars in basic form and in CNF, positive and negative inputs
	# suitable lens have been chosen so that the tests run a reasonable amount of time
	allGrammars      = [ g1,   g2,   g3,   g4,   g5,   g6,   g7,   g8,   g9,  g10,  g11,  g12,  g13,  g14,  g15,  g16,  g17,  g18,  g19,  g20]
	lensBasicFormPos = [500, 1000,  300,   80,  400,  600, 1200, 1200,  200,   60,  200,  400,  500,  400,  400,  400,   18,  300,  300,  300]
	lensBasicFormNeg = [ 80,  500,  300,   80,  400,  600, 1200, 1200,  200,   60,  150,  400,  500,  400,  400,  400,   12,  150,  300,  400]
	lensCNFPos       = [300,  800,   13,   40,  400,  600,  600,  800,  120,   60,   20,  400,  300,  400,  400,  200,   14,  200,   70,  300]
	lensCNFNeg       = [ 26,  300,   13,   20,  400,  600,  600,  800,  120,   60,   20,  400,  300,  400,  400,  200,   12,  100,   70,  400]

	#filter which tests will be run
	runTests = range(1, len(allGrammars) * 4 + 1)
	#runTests = [25, 26, 27]

	testNo = 0
	for grammar, lenBasicPos, lenBasicNeg, lenCNFPos, lenCNFNeg in zip(allGrammars, lensBasicFormPos, lensBasicFormNeg, lensCNFPos, lensCNFNeg):
		testNo += 1
		if testNo in runTests:
			inputStr = next(grammar.input_gen_func(lenBasicPos, 0, True))
			tester.run_prune_test(grammar, inputStr, True, times)

		testNo += 1
		if testNo in runTests:
			inputStr = next(grammar.input_gen_func(lenBasicNeg, 0, False))
			tester.run_prune_test(grammar, inputStr, False, times)

		g1.to_wk_cnf()

		testNo += 1
		if testNo in runTests:
			inputStr = next(grammar.input_gen_func(lenCNFPos, 0, True))
			tester.run_prune_test(grammar, inputStr, True, times)

		testNo += 1
		if testNo in runTests:
			inputStr = next(grammar.input_gen_func(lenCNFNeg, 0, False))
			tester.run_prune_test(grammar, inputStr, False, times)

	tester.printResults()

if __name__ == "__main__":
	main()
