# Author: Jan Hammer, xhamme00@stud.fit.vutbr.cz
# Project: WK Grammar Tree Search
# Runs a test of wk-cyk using 17 grammars increasing the input length by the step value, all grammars must be in CNF

from lib.perf_tester import cPerfTester
from lib.grammars import *

def main():
	t = cPerfTester()

	# not applicable for grammars 5, 19, 20 - not compl. relation not identity
	allGrammars =   [g1, g2, g3, g4, g6, g7, g8, g9, g10, g11, g12, g13, g14, g15, g16, g17, g18]

	# all tests have the same starting length and step as the WK-CYK performance is very consistent
	INPUT_START_LEN = 10
	INPUT_STEP = 2

	#filter which tests will be run
	runTests = range(1, len(allGrammars) * 2 + 1)
	#runTests = [1, 6]

	testNo = 0
	for grammar in allGrammars:
		grammar.to_wk_cnf()

		testNo += 1
		if testNo in runTests:
			t.run_wk_cyk_test(grammar, grammar.input_gen_func(INPUT_START_LEN, INPUT_STEP, True), True)

		testNo += 1
		if testNo in runTests:
			t.run_wk_cyk_test(grammar, grammar.input_gen_func(INPUT_START_LEN, INPUT_STEP, False), False)


if __name__ == "__main__":
	main()
