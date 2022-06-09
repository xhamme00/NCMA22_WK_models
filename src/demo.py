# Author: Jan Hammer, xhamme00@stud.fit.vutbr.cz
# Project: WK Grammar Tree Search
# demonstrates how to use the cWK_CFG class

# one option is to use one of the grammars (g1-g20) from lib/grammars.py
from lib.grammars import *

# this grammar defines the a^n b^n language, is has the following rules:
print(f'grammar {g6.desc} rules:')
for rule in g6.rules:
	print(rule)
print('\n')

# we can define an input string that will be tested for membership in the grammar
inputStr1 = 'aaaaabbbbb'

# or we can use the generator to generate an input of a given length that will be accepted
gen  = g6.input_gen_func(30, 0, True)
inputStr2 = next(gen)

# or rejected
gen  = g6.input_gen_func(30, 0, False)
inputStr3 = next(gen)

# and then, let's run the tree search on these inputs and print the results
for inputStr in [inputStr1, inputStr2, inputStr3]:
	openStates, allStates, pruneStats, result = g6.run_tree_search(inputStr)
	print(f'the input "{inputStr}" returned with result: {result}')

# now we can try to run the wk-cyk, for that the grammar must be in WK-CNF
g6.to_wk_cnf()

# now it has the following rules
print(f'\ngrammar {g6.desc} rules after transformation to CNF:')
for rule in g6.rules:
	print(rule)
print('\n')

# now the wk-cyk run (this may take a few seconds)
for inputStr in [inputStr1, inputStr2, inputStr3]:
	result = g6.run_wk_cyk(inputStr)
	print(f'the input "{inputStr}" returned with result: {result}')

# we can define a new grammar, say (ab)*
from lib.ctf_WK_grammar import *

# firstly, rules:
rules = [
	cRule('S', ['A', 'B', 'S']),    # S -> A B S
	cRule('S', [([], [])]),          # S -> lambda/lambda
	cRule('A', [(['a'], ['a'])]),  # A -> a/a
	cRule('B', [(['b'], ['b'])])   # B -> b/b
]

# then the non-terminals, terminals, starting non-terminal and complementarity relation
nts = ['S', 'A', 'B']
ts = ['a', 'b']
startingNt = 'S'
relation = [('a', 'a'), ('b', 'b')]

# then the grammar object:
g = cWK_CFG(nts, ts, startingNt, rules, relation)
g.desc = '(ab)*'

# now we have a grammar with rules:
print(f'\ngrammar {g.desc} rules:')
for rule in g.rules:
	print(rule)
print('\n')

# of course, this grammar has no input string generator (unless we write one), the inputs must be crated manually
inputStr1 = 'ab' * 100

# we could write the input generator
def input_gen_func(start, step, accept):
	curLen = start
	while True:
		yield 'ab' * (curLen //2) + ('' if accept else 'a')
		curLen += step

g.input_gen_func = input_gen_func

# now we can generate inputs both positive and negative
gen = g.input_gen_func(200, 0, True)
inputStr2 = next(gen)

gen = g.input_gen_func(200, 0, False)
inputStr3 = next(gen)

# and run tree search
for inputStr in [inputStr1, inputStr2, inputStr3]:
	openStates, allStates, pruneStats, result = g.run_tree_search(inputStr)
	print(f'the input "{inputStr}" returned with result: {result}')

# and we can remove the lambda rule, we can save the current grammer form first
g.backup()
g.remove_lambda_rules()

# now we have a grammar with rules:
print(f'\ngrammar {g.desc} rules:')
for rule in g.rules:
	print(rule)
print('\n')

# nothing changes when running the tree search, the grammars are equivalent
for inputStr in [inputStr1, inputStr2, inputStr3]:
	openStates, allStates, pruneStats, result = g.run_tree_search(inputStr)
	print(f'the input "{inputStr}" returned with result: {result}')
	print(pruneStats)

# and we can restore the original form of the grammar
g.restore()

print(f'\ngrammar {g.desc} rules:')
for rule in g.rules:
	print(rule)
print('\n')

# it is possible to change the active node precedence heuristic
g.activate('NTA')

# also the pruning heuristics can be turned off,
# maybe the statistics show that some are not used with a particular grammar
g.activate('SL', False)
g.activate('RL', False)

# the tree search is now using this now configuration
for inputStr in [inputStr1, inputStr2, inputStr3]:
	openStates, allStates, pruneStats, result = g.run_tree_search(inputStr)
	print(f'the input "{inputStr}" returned with result: {result}')
	print(pruneStats)
