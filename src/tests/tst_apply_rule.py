# Author: Jan Hammer, xhamme00@stud.fit.vutbr.cz
# Project: WK Grammar Tree Search
# Testing of the cWK_CFG.apply_rule method

import sys
sys.path.append("../")

from lib.ctf_WK_grammar import *

RES_OK = '\033[92m' + 'OK' + '\x1b[0m'
RES_FAILED = '\033[91m' + 'FAILED' + '\x1b[0m'

testNo = 1

# parameters 1. the word before  2. idx of the nonterm to be replaced  3. word that replaces  4. expected string (after stringification)
def runTest(word: tWord, ntIdx: int, ruleRhs: tWord, expected: str) -> None:
	global testNo
	g = cWK_CFG(['A'], [], 'A' , [], [])
	actual = wordToStr(g.apply_rule(word, ntIdx, rule))
	status = RES_OK if actual == expected else RES_FAILED
	print(f'| TEST {testNo:2} | {wordToStr(word):20} | {ntIdx:6} | {word[ntIdx] + " -> " + wordToStr(rule):20} | {expected:20} | {actual:20} | {status:15}   |')
	testNo += 1

hline = '|---------|----------------------|--------|----------------------|----------------------|----------------------|----------|'

print(hline)

print('|         |      WORD            | NT IDX |       RULE           |       EXPECTED       |       ACTUAL         | STATUS   |')
print(hline)

rule: tWord = [(['a'], ['a'])]
runTest(['A'],                                         0, rule, 'a/a')
runTest([(['a'], ['a']), 'A'],                         1, rule, 'aa/aa')
runTest(['A', (['a'], ['a'])],                         0, rule, 'aa/aa')
runTest([(['a'], ['b']), 'A', (['c'], ['d'])],         1, rule, 'aac/bad')
runTest([(['a'], ['a']), 'A', 'B'],                    1, rule, 'aa/aa B')
runTest(['B', 'A', (['b'], ['b'])],                    1, rule, 'B ab/ab')
runTest(['A', 'A', 'B'],                               1, rule, 'A a/a B')

rule = [(['a'], ['a']), 'B', (['c'], ['c'])]
runTest(['A', 'A', 'A'],                               1, rule, 'A a/a B c/c A')
runTest(['A', 'A', 'A'],                               0, rule, 'a/a B c/c A A')
runTest(['A', 'A', (['a'], ['b'])],                    1, rule, 'A a/a B ca/cb')
runTest([(['a'], ['b']), 'A'],                         1, rule, 'aa/ba B c/c')
runTest([(['a'], ['b']), 'A', (['c'], ['d']), 'B'],    1, rule, 'aa/ba B cc/cd B')
runTest([(['a'], []), 'A'],                            1, rule, 'aa/a B c/c')

rule = [([], ['b']), 'A', (['a'], [])]
runTest([(['a'], ['b']), 'A', (['c'], ['d'])],         1, rule, 'a/bb A ac/d')
runTest([(['a'], ['a']), 'A', 'B'],                    1, rule, 'a/ab A a/λ B')

rule = [(['a'], []), 'S']
runTest([(['a'], []), 'S'],                    1, rule, 'aa/λ S')
print(hline)
