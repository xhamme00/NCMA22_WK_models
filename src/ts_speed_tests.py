# Author: Jan Hammer, xhamme00@stud.fit.vutbr.cz
# Project: WK Grammar Tree Search
# Runs a tree search test using all 20 grammars increasing the input length by the step value

from lib.perf_tester import cPerfTester
from lib.grammars import *

def main():
	times = 1
	tester = cPerfTester()

	# lengths of inputs and steps for testing grammars in basic form and in CNF, positive and negative inputs
	# suitable lens have been chosen so that the tests run a reasonable amount of time
	testDataLst = [
	#    grammar  basicFormPos   basicFormNeg    cnfPos      cnfNeg
	#               len   step    len    step    len  step    len  step
		(     g1,   500,   100,   100,     20,   100,   20,    10,    2),
		(     g2,   200,   100,   200,    100,   100,   50,   100,   50),
		(     g3,   200,   100,   200,    100,     3,    1,     3,    1),
		(     g4,   100,    50,   100,     50,    10,   10,     5,    3),
		(     g5,   300,    50,   300,     50,   300,   50,   300,   50),
		(     g6,   100,    50,   100,     50,   100,   50,   100,   50),
		(     g7,   200,   100,   200,    100,   200,  100,   200,  100),
		(     g8,   200,   100,   200,    100,   200,   50,   200,   50),
		(     g9,   100,    20,    50,     20,    50,   10,    20,   10),
		(    g10,    50,    10,    20,     10,    40,   10,    30,    5),
		(    g11,   200,   100,    50,      5,     6,    2,     6,    2),
		(    g12,   200,   100,   200,    100,   200,  100,   200,  100),
		(    g13,   200,   100,   200,    100,   200,  100,   200,  100),
		(    g14,   200,   100,   200,    100,   200,  100,   200,  100),
		(    g15,   100,    50,   100,     50,   100,   50,   100,   50),
		(    g16,   100,    50,   100,     50,    50,   30,    50,   30),
		(    g17,    10,     2,    10,      2,    10,    2,    10,    2),
		(    g18,   200,   100,    80,     30,   100,   20,    80,   30),
		(    g19,   100,    50,   100,     20,   100,   30,    50,    5),
		(    g20,   100,    50,   100,     50,   100,   50,   100,   50),
	]

	#filter which tests will be run
	runTests = range(1, len(testDataLst) * 4 + 1)
	#runTests = [10, 14]

	testNo = 0
	for grammar, basicPosLen, basicPosStep, basicNegLen, basicNegStep, cnfPosLen, cnfPosStep, cnfNegLen, cnfNegStep in testDataLst:
		testNo += 1
		if testNo in runTests:
			tester.run_speed_test(grammar, grammar.input_gen_func(basicPosLen, basicPosStep, True), True, times)

		testNo += 1
		if testNo in runTests:
			tester.run_speed_test(grammar, grammar.input_gen_func(basicNegLen, basicNegStep, False), False, times)

		grammar.to_wk_cnf()

		testNo += 1
		if testNo in runTests:
			tester.run_speed_test(grammar, grammar.input_gen_func(cnfPosLen, cnfPosStep, True), True, times)

		testNo += 1
		if testNo in runTests:
			tester.run_speed_test(grammar, grammar.input_gen_func(cnfNegLen, cnfNegStep, False), False, times)

if __name__ == "__main__":
	main()
