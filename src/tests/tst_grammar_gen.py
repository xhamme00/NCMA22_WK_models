# Author: Jan Hammer, xhamme00@stud.fit.vutbr.cz
# Project: WK Grammar Tree Search
# Testing correctness of the cWK_CFG.run_tree_search method and run_wk_cyk method

import sys
sys.path.append("../")

from lib.ctf_WK_grammar import *
from lib.grammars import *

RES_TIMEOUT = '\033[93m' + 'TIMEOUT' + '\x1b[0m'
RES_OK = '\033[92m' + 'OK' + '\x1b[0m'
RES_FAILED = '\033[91m' + 'FAILED' + '\x1b[0m'

hline = f'|{"-"*11}|{"-"*37}|{"-"*42}|{"-"*12}|{"-"*10}|{"-"*23}|{"-"*14}|{"-"*8}|{"-"*9}|'
testNo = 1

print(hline)
print(f'|{" "*11}| GRAMMAR{" "*29}| STRING{" "*35}|  EXPECTED  |  ACTUAL  | STATES  (OPEN/CLOSED) | TIME TAKEN   |  NOTE  | STATUS  |')
print(hline)

def runTest(grammar, inputStr, expected, toCNF, runWKCYK):
	global testNo

	note = ''
	if toCNF or runWKCYK:
		grammar.backup()
		grammar.to_wk_cnf()
		note = 'CNF'

	if runWKCYK:
		start = time.time()
		openStates, closedStates, actual = 0, 0, grammar.run_wk_cyk(inputStr)
		end = time.time()
		note = 'WK-CYK'
	else:
		start = time.time()
		openStates, closedStates, _, actual = grammar.run_tree_search(inputStr)
		end = time.time()

	timeTaken = round(end - start, 8)

	if toCNF or runWKCYK:
		grammar.restore()

	if actual is None:
		status = RES_TIMEOUT
		actual = ''
	else:
		status = RES_OK if actual == expected else RES_FAILED

	print(f'| TEST {testNo:3}  | {grammar.desc:35} | {inputStr:40} |   {expected:6}   |  {actual:6}  | {openStates:10} {closedStates:10} | {timeTaken:12} | {note:6} | {status:16} |')
	testNo += 1

############################ GRAMMAR 1:   a(aa)*      #####################################################################################

for toCnf, runWkCyk in [(False, False), (False, True), (True, False)]:
	runTest(g1, '', False, toCnf, runWkCyk)
	runTest(g1, 'a', True, toCnf, runWkCyk)
	runTest(g1, 'aa', False, toCnf, runWkCyk)
	runTest(g1, 'aaa', True, toCnf, runWkCyk)
	runTest(g1, 'aaaaaaaaaaa', True, toCnf, runWkCyk)
	runTest(g1, 'aaaaaaaaaaaa', False, toCnf, runWkCyk)

############################ GRAMMAR 2:   a^n b^n (n>0)    ################################################################################

	runTest(g6, 'ab', True, toCnf, runWkCyk)
	runTest(g6, 'aaabbb', True, toCnf, runWkCyk)
	runTest(g6, 'aaabb', False, toCnf, runWkCyk)
	runTest(g6, 'abab', False, toCnf, runWkCyk)
	runTest(g6, '', False, toCnf, runWkCyk)
	runTest(g6, 'aabb', True, toCnf, runWkCyk)
	runTest(g6, 'abc', False, toCnf, runWkCyk)

############################ GRAMMAR 3:   r^n d^n u^n r^n    ##############################################################################

	runTest(g12, 'rdur', True, toCnf, runWkCyk)
	runTest(g12, 'rrrrrrdddddduuuuuurrrrrr', True, toCnf, runWkCyk)
	runTest(g12, 'rrrrrrdddddduuuuuuurrrrrr', False, toCnf, runWkCyk)
	runTest(g12, 'rrrrrrddddduuuuuurrrrrr', False, toCnf, runWkCyk)

############################ GRAMMAR 4:   a^n c^n b^n    ##################################################################################

	runTest(g13, 'aaaaaaaaaaaaccccccccccccbbbbbbbbbbbb', True, toCnf, runWkCyk)
	runTest(g13, 'aaaaaaaaaaaccccccccccccbbbbbbbbbbbb', False, toCnf, runWkCyk)

############################ GRAMMAR 5:   a^n b^m c^n d^m     ##############################################################################

	runTest(g14, 'aaaabbbbbbbccccddddddd', True, toCnf, runWkCyk)
	runTest(g14, 'aaaabbbbbbbccccdddddd', False, toCnf, runWkCyk)

############################ GRAMMAR 6:   wcw where w in {a,b }*     ######################################################################

	runTest(g15, 'abbabacabbaba', True, toCnf, runWkCyk)
	runTest(g15, 'abbabacababa', False, toCnf, runWkCyk)

############################ GRAMMAR 7:   a^n b^m a^n where 2n <= m <= 3n   ###############################################################

	for m, n in [(m, n) for m in range(1, 7) for n in range (1, 7)]:
		runTest(g16, 'a'*n + 'b'*m + 'a'*n, 2*n <= m and m <= 3*n, toCnf, runWkCyk)

print(hline)
