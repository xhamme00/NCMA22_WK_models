# Author: Jan Hammer, xhamme00@stud.fit.vutbr.cz
# Project: WK Grammar Tree Search
# list of grammars and input generators

from lib.ctf_WK_grammar import *
import random

#####################################  GRAMMAR 1  #####################################
# accepted language: a(aa)*

rules = [
	cRule('S', ['S', 'S', 'S']),
	cRule('S', [(['a'], ['a'])])
]
g1 = cWK_CFG(['S'], ['a'], 'S', rules, [('a', 'a')])
g1.desc = 'a(aa)*'

def input_gen_func(start, step, accept):
	s, curLen = '', start

	while True:
		s = 'a' * curLen
		if accept and len(s) % 2 == 0:
			s += 'a'
		elif not accept and len(s) % 2 == 1:
			s += 'a'
		curLen += step
		yield s

g1.input_gen_func = input_gen_func

#####################################  GRAMMAR 2  #####################################
# accepted strings: (a+b+c)*abc
# how does the model cope with fixed end? (rules in form xA)

rules = [
	cRule('S', [(['a'], ['a']), 'S']),
	cRule('S', [(['b'], ['b']), 'S']),
	cRule('S', [(['c'], ['c']), 'S']),
	cRule('S', [(['a'], ['a']), (['b'], ['b']), (['c'], ['c'])])
]

g2 = cWK_CFG(['S'], ['a', 'b', 'c'], 'S', rules, [('a', 'a'), ('b', 'b'), ('c', 'c')])
g2.desc = '(a+b+c)*abc'

def input_gen_func(start, step, accept):
	s, curLen = '', start
	while True:
		s = ''.join([random.choice('ab') for i in range(curLen - 3 if accept else curLen)]) + ('abc' if accept else '')
		curLen += step
		yield s
g2.input_gen_func = input_gen_func

#####################################  GRAMMAR 3  #####################################
# accepted strings: (a+b+c)*abc
# how does the model cope with fixed end? (rules in form Ax)

rules = [
	cRule('S', ['A', (['a'], ['a']), (['b'], ['b']), (['c'], ['c'])]),
	cRule('A', ['A', (['a'], ['a'])]),
	cRule('A', ['A', (['b'], ['b'])]),
	cRule('A', ['A', (['c'], ['c'])]),
	cRule('A', [([], [])])
]

g3 = cWK_CFG(['S', 'A'], ['a', 'b', 'c'], 'S', rules, [('a', 'a'), ('b', 'b'), ('c', 'c')])
g3.desc = '(a+b+c)*abc'
g3.input_gen_func = g2.input_gen_func

#####################################  GRAMMAR 4  #####################################
# accepted strings: a?b?c?d?e?f?g? + (a?b?c?d?e?f?g?)*a
# aimed to have a lot of rules after transformation to CNF

rules = [
	cRule('S', ['Q', (['a'], ['a'])]),
	cRule('S', ['A', 'B', 'C', 'D', 'E', 'F', 'G']),
	cRule('Q', ['Q', 'Q']),
	cRule('Q', ['A', 'B', 'C', 'D', 'E', 'F', 'G']),
	cRule('A', [(['a'], ['a'])]),
	cRule('A', [([], [])]),
	cRule('B', [(['b'], ['b'])]),
	cRule('B', [([], [])]),
	cRule('C', [(['c'], ['c'])]),
	cRule('C', [([], [])]),
	cRule('D', [(['d'], ['d'])]),
	cRule('D', [([], [])]),
	cRule('E', [(['e'], ['e'])]),
	cRule('E', [([], [])]),
	cRule('F', [(['f'], ['f'])]),
	cRule('F', [([], [])]),
	cRule('G', [(['g'], ['g'])]),
	cRule('G', [([], [])])
]

ts = ['a', 'b', 'c', 'd', 'e', 'f', 'g']
g4 = cWK_CFG(['S', 'Q', 'A', 'B', 'C', 'D', 'E', 'F', 'G'], ts, 'S', rules, [(x, x) for x in ts])
g4.desc = 'a?b?c?d?e?f?g? + (a?b?c?d?e?f?g?)*a'

def input_gen_func(start, step, accept):
	curLen = start
	while True:
		s = ''.join([random.choice('abcdefg') for i in range(curLen - 1)]) + ('a' if accept else 'b')
		curLen += step
		yield s
g4.input_gen_func = input_gen_func

##################################### GRAMMAR 5  #####################################
# accepted strings: ({a,t,c,g}*ctg{a,t,c,g}*)*

rules = [
	cRule('S', [(['a'], ['t']), 'S']),
	cRule('S', [(['t'], ['a']), 'S']),
	cRule('S', [(['g'], ['c']), 'S']),
	cRule('S', [(['c'], ['g']), 'A']),
	cRule('A', [(['c'], ['g']), 'A']),
	cRule('A', [(['a'], ['t']), 'S']),
	cRule('A', [(['g'], ['c']), 'S']),
	cRule('A', [(['t'], ['a']), 'B']),
	cRule('B', [(['c'], ['g']), 'A']),
	cRule('B', [(['a'], ['t']), 'S']),
	cRule('B', [(['t'], ['a']), 'S']),
	cRule('B', [(['g'], ['c']), 'C']),
	cRule('C', [(['a'], ['t']), 'C']),
	cRule('C', [(['t'], ['a']), 'C']),
	cRule('C', [(['g'], ['c']), 'C']),
	cRule('C', [(['c'], ['g']), 'C']),
	cRule('C', [([], [])])
]
g5 = cWK_CFG(['S', 'A', 'B', 'C'], ['a', 't', 'g', 'c'], 'S', rules, [('a', 't'), ('t', 'a'), ('g', 'c'), ('c', 'g')])
g5.desc = '({a,t,c,g}*ctg{a,t,c,g}*)*'

def input_gen_func(start, step, accept):
	curLen = start

	while True:
		if accept:
			s = ''.join([random.choice('actg') for i in range(curLen-3)]) + 'ctg'
		else:
			s = ''.join([random.choice('act') for i in range(curLen)])
		curLen += step
		yield s
g5.input_gen_func =  input_gen_func

##################################### GRAMMAR 6  #####################################
# accepted strings: a^n b^n (n>0)

rules  = [
	cRule('S', [(['a'], []), 'S']),
	cRule('S', [(['a'], []), 'A']),
	cRule('A', [(['b'], ['a']), 'A']),
	cRule('A', [(['b'], ['a']), 'B']),
	cRule('B', [([], ['b']), 'B']),
	cRule('B', [([], ['b'])])
]

g6 = cWK_CFG(['S', 'A', 'B'], ['a', 'b'], 'S', rules, [('a', 'a'), ('b', 'b')])
g6.desc = 'a^n b^n (n>0)'

def input_gen_func(start, step, accept):
	curLen = start

	while True:
		s = 'a' * (curLen // 2) + 'b' * (curLen // 2)
		if not accept:
			s += 'b'
		curLen += step
		yield s
g6.input_gen_func = input_gen_func
##################################### GRAMMAR 7 #####################################
# accepted strings: wcw^R

rules = [
	cRule('S', [(['a'], ['a']), 'S', (['a'], ['a'])]),
	cRule('S', [(['b'], ['b']), 'S', (['b'], ['b'])]),
	cRule('S', [(['c'], ['c'])])
]
g7 = cWK_CFG(['S'], ['a', 'b', 'c'], 'S', rules, [('a', 'a'), ('b', 'b'), ('c', 'c')])
g7.desc = 'wcw^R'

def input_gen_func(start, step, accept):
	curLen = start

	while True:
		s = ''.join([random.choice('ab') for i in range(curLen // 2)])
		s += ('' if accept else 'a') + 'c' + s[::-1]
		curLen += step
		yield s
		
g7.input_gen_func = input_gen_func

##################################### GRAMMAR 8  #####################################
# accepted strings: w w^r

rules = [
	cRule('S', [(['a'], ['a']), 'S', (['a'], ['a'])]),
	cRule('S', [(['b'], ['b']), 'S', (['b'], ['b'])]),
	cRule('S', [([], [])])
]
g8 = cWK_CFG(['S'], ['a', 'b'], 'S', rules, [('a', 'a'), ('b', 'b')])
g8.desc = 'w w^r'

def input_gen_func(start, step, accept):
	curLen = start

	while True:
		s = ''.join([random.choice('ab') for i in range(curLen // 2)])
		s += ('' if accept else 'a') + s[::-1]
		curLen += step
		yield s

g8.input_gen_func = input_gen_func
##################################### GRAMMAR 9  #####################################
# accepted string: x2y : x,y in {0,1}* |x| != |y|

rules = [
	cRule('S', ['B', 'L']),
	cRule('S', ['R', 'B']),
	cRule('L', ['B', 'L']),
	cRule('L', ['A']),
	cRule('R', ['R', 'B']),
	cRule('R', ['A']),
	cRule('A', ['B', 'A', 'B']),
	cRule('A', [(['2'], ['2'])]),
	cRule('B', [(['0'], ['0'])]),
	cRule('B', [(['1'], ['1'])])
]
g9 = cWK_CFG(['S', 'L', 'R', 'A', 'B'], ['0', '1', '2'], 'S', rules, [('0', '0'), ('1', '1'), ('2', '2')])
g9.desc = 'x2y : x,y in {0,1}* |x| != |y|'

def input_gen_func(start, step, accept):
	curLen = start

	while True:
		s = ''.join([random.choice('01') for i in range(curLen // 2)])
		s += '2' + ''.join([random.choice('01') for i in range(curLen // 2)]) + ('0' if accept else '')
		curLen += step
		yield s

g9.input_gen_func = input_gen_func
##################################### GRAMMAR 10 #####################################
# accepted strings: regular expressions with ones and zeros and following symbols
# p  :  +   (plus sign)
# e  :  Ø   (empty set)
# o  :  (   (left parenthesis)
# c  :  )   (right parenthesis)
# l  :  3   (empty string)
# s  :  *   (star)
# d  :  •   (dot / concatenation operator)

rules = [
	cRule('S', ['T']),
	cRule('S', ['T', (['p'], ['p']), 'S']),
	cRule('T', ['F']),
	cRule('T', ['F', 'T']),
	cRule('F', [(['e'], ['e'])]),
	cRule('F', ['W']),
	cRule('F', [(['o'], ['o']), 'T', (['p'], ['p']), 'S', (['c'], ['c'])]),
	cRule('F', ['X', (['s'], ['s'])]),
	cRule('F', [(['o'], ['o']), 'Y', (['c'], ['c']), (['s'], ['s'])]),
	cRule('X', [(['e'], ['e'])]),
	cRule('X', [(['l'], ['l'])]),
	cRule('X', [(['0'], ['0'])]),
	cRule('X', [(['1'], ['1'])]),
	cRule('Y', ['T', (['p'], ['p']), 'S']),
	cRule('Y', ['F', (['d'], ['d']), 'T']),
	cRule('Y', ['X', (['s'], ['s'])]),
	cRule('Y', [(['o'], ['o']), 'Y', (['c'], ['c']), (['s'], ['s'])]),
	cRule('Y', ['Z', 'Z']),
	cRule('W', [(['l'], ['l'])]),
	cRule('W', ['Z']),
	cRule('Z', [(['0'], ['0'])]),
	cRule('Z', [(['1'], ['1'])]),
	cRule('Z', ['Z', 'Z'])
]
nts = ['S', 'T', 'F', 'X', 'Y', 'W', 'Z']
ts = ['p', 'e', 'o', 'c', 'l', 's', 'd', '0', '1']
g10 = cWK_CFG(nts, ts, 'S', rules, [(x, x) for x in ts])
g10.desc = 'RE with 0, 1 and operators: p-plus, e-empty set, o-opening par, c-closing par, l-epsilon, s-star, d-dot'

# possible enhancement - this generator is now very simple
# it could generate more interesting strings
def input_gen_func(start, step, accept):
	curLen = start

	while True:
		s = '0p' * (curLen // 2) + ('0' if accept else '')
		curLen += step
		yield s
		
g10.input_gen_func = input_gen_func
##################################### GRAMMAR 11 #####################################
# accepted strings: (ww)^C

rules = [
	cRule('S', ['A']),
	cRule('S', ['B']),
	cRule('S', ['A', 'B']),
	cRule('S', ['B', 'A']),
	cRule('A', [(['a'], ['a'])]),
	cRule('A', [(['a'], ['a']), 'A', (['a'], ['a'])]),
	cRule('A', [(['a'], ['a']), 'A', (['b'], ['b'])]),
	cRule('A', [(['b'], ['b']), 'A', (['b'], ['b'])]),
	cRule('A', [(['b'], ['b']), 'A', (['a'], ['a'])]),
	cRule('B', [(['b'], ['b'])]),
	cRule('B', [(['a'], ['a']), 'B', (['a'], ['a'])]),
	cRule('B', [(['a'], ['a']), 'B', (['b'], ['b'])]),
	cRule('B', [(['b'], ['b']), 'B', (['b'], ['b'])]),
	cRule('B', [(['b'], ['b']), 'B', (['a'], ['a'])])
]

g11 = cWK_CFG(['S', 'A', 'B'], ['a', 'b'], 'S', rules, [('a', 'a'), ('b', 'b')])
g11.desc = '{a, b}* - ww'

def input_gen_func(start, step, accept):
	curLen = start

	while True:
		s = ''.join([random.choice('ab') for i in range(curLen // 2)])
		s += s + ('a' if accept else '')
		curLen += step
		yield s

g11.input_gen_func = input_gen_func
##################################### GRAMMAR 12 #####################################
# accepted strings: r^n d^n u^n r^n

rules = [
	cRule('S', [(['r'], []), 'S']),
	cRule('S', [(['r'], []), 'A']),
	cRule('A', [(['d'], ['r']), 'A']),
	cRule('A', [(['d'], ['r']), 'B']),
	cRule('B', [(['u'], ['d']), 'B']),
	cRule('B', [(['u'], ['d']), 'C']),
	cRule('C', [(['r'], ['u']), 'C']),
	cRule('C', [(['r'], ['u']), 'D']),
	cRule('D', [([], ['r']), 'D']),
	cRule('D', [([], ['r'])])
]

g12 = cWK_CFG(['S', 'A', 'B', 'C', 'D'], ['r', 'd', 'u'], 'S', rules, [('r', 'r'), ('d', 'd'), ('u', 'u')])
g12.desc = 'r^n d^n u^n r^n'

def input_gen_func(start, step, accept):
	curLen = start

	while True:
		s = 'r' * (curLen // 4) + 'd' * (curLen // 4) + 'u' * (curLen // 4) + 'r' * (curLen // 4) + ('' if accept else 'r')
		curLen += step
		yield s

g12.input_gen_func = input_gen_func
##################################### GRAMMAR 13 #####################################
# accepted strings: a^n c^n b^n

rules = [
	cRule('S', [(['a'], []), 'S', (['b'], [])]),
	cRule('S', [(['a'], []), 'A', (['b'], [])]),
	cRule('A', [(['c'], ['a']), 'A']),
	cRule('A', [([], ['c']), 'B', ([], ['b'])]),
	cRule('B', [([], ['c']), 'B', ([], ['b'])]),
	cRule('B', [([], [])])
]

g13 = cWK_CFG(['S', 'A', 'B'], ['a', 'b', 'c'], 'S', rules, [('a', 'a'), ('b', 'b'), ('c', 'c')])
g13.desc = 'a^n c^n b^n'

def input_gen_func(start, step, accept):
	curLen = start

	while True:
		s = 'a' * (curLen // 3) + 'c' * (curLen // 3) + 'b' * (curLen // 3) + ('' if accept else 'b')
		curLen += step
		yield s

g13.input_gen_func = input_gen_func
##################################### GRAMMAR 14 #####################################
# accepted strings: a^n b^m c^n d^m

rules = [
	cRule('S', [(['a'], []), 'S']),
	cRule('S', [(['a'], []), 'A']),
	cRule('A', [(['b'], []), 'A']),
	cRule('A', [(['b'], []), 'B']),
	cRule('B', [(['c'], ['a']), 'B']),
	cRule('B', [(['c'], ['a']), 'C']),
	cRule('C', [(['d'], ['b']), 'C']),
	cRule('C', [(['d'], ['b']), 'D']),
	cRule('D', [([], ['c']), 'D']),
	cRule('D', [([], ['d']), 'D']),
	cRule('D', [([], [])])
]

g14 = cWK_CFG(['S', 'A', 'B', 'C', 'D'], ['a', 'b', 'c', 'd'], 'S', rules, [('a', 'a'), ('b', 'b'), ('c', 'c'), ('d', 'd')])
g14.desc = 'a^n b^m c^n d^m'

def input_gen_func(start, step, accept):
	curLen = start

	while True:
		n = curLen // 6
		m = (curLen // 2) - n
		s = 'a' * n + 'b' * m + 'c' * n + 'd' * m + ('' if accept else 'd')
		curLen += step
		yield s

g14.input_gen_func = input_gen_func
##################################### GRAMMAR 15 #####################################
# accepted strings: wcw where w in {a,b }*

rules = [
	cRule('S', [(['a'], []), 'S']),
	cRule('S', [(['b'], []), 'S']),
	cRule('S', [(['c'], []), 'A']),
	cRule('A', [(['a'], ['a']), 'A']),
	cRule('A', [(['b'], ['b']), 'A']),
	cRule('A', [([], ['c']), 'B']),
	cRule('B', [([], ['a']), 'B']),
	cRule('B', [([], ['b']), 'B']),
	cRule('B', [([], [])]),
]

g15 = cWK_CFG(['S', 'A', 'B'], ['a', 'b', 'c'], 'S', rules, [('a', 'a'), ('b', 'b'), ('c', 'c')])
g15.desc = 'wcw where w in {a,b }*'

def input_gen_func(start, step, accept):
	curLen = start

	while True:
		s = ''.join([random.choice('ab') for i in range(curLen // 2)])
		s += 'c' + ('' if accept else 'a') + s
		curLen += step
		yield s
		
g15.input_gen_func = input_gen_func
##################################### GRAMMAR 16 #####################################
# accepted strings: a^n b^m a^n where 2n <= m <= 3n

rules = [
	cRule('S', [(['a'], []), 'S', (['a'], ['a'])]),
	cRule('S', [(['a'], []), 'A', (['a'], ['a'])]),
	cRule('A', [(['b', 'b'], ['a']), 'A']),
	cRule('A', [(['b', 'b', 'b'], ['a']), 'A']),
	cRule('A', [([], ['b']), 'B']),
	cRule('B', [([], ['b']), 'B']),
	cRule('B', [([], [])])
]

g16 = cWK_CFG(['S', 'A', 'B'], ['a', 'b'], 'S', rules, [('a', 'a'), ('b', 'b')])
g16.desc = 'a^n b^m a^n where 2n <= m <= 3n'

def input_gen_func(start, step, accept):
	curLen = start

	while True:
		n = curLen // 4
		m = 2 * n
		s = 'a' * n + 'b' * m + 'a' * n + ('' if accept else 'a')
		curLen += step
		yield s

g16.input_gen_func = input_gen_func
##################################### GRAMMAR 17 #####################################
# accepted strings: cnt(a) == cnt(b) and for any prefix: cnt(a) >= cnt(b)

rules = [
	cRule('S', ['S', 'S']),
	cRule('S', [(['a'], []), ([], ['a']), 'S', (['b'], []), ([], ['b'])]),
	cRule('S', [(['a'], []), 'S']),
	cRule('S', [(['a'], []), 'A']),
	cRule('A', [(['b'], []), ([], ['a']), 'A']),
	cRule('A', [(['b'], []), ([], ['a']), 'B']),
	cRule('A', [(['b'], []), ([], ['a'])]),
	cRule('B', [([], ['b']), 'B']),
	cRule('B', [([], ['b'])]),
	cRule('B', ['B', 'B']),
	cRule('B', [(['a'], []), ([], ['a']), 'S', (['b'], []), ([], ['b'])]),
	cRule('B', [(['a'], []), 'S']),
	cRule('B', [(['a'], []), 'A'])
]

g17 = cWK_CFG(['S', 'A', 'B'], ['a', 'b'], 'S', rules, [('a', 'a'), ('b', 'b')])
g17.desc = 'cnt(a) == cnt(b) and for any prefix: cnt(a) >= cnt(b)'

def input_gen_func(start, step, accept):
	curLen = start

	while True:
		bpool = apool = curLen // 2
		s = ''
		while apool > 0 or bpool > 0:
			if apool == bpool:
				s += 'a'
				apool -= 1
			elif apool == 0:
				s += 'b' * bpool
				bpool = 0
			else:
				if random.randint(1, 2) == 1:
					s += 'a'
					apool -= 1
				else:
					s += 'b'
					bpool -= 1
		if not accept:
			s += 'ba'
		curLen += step
		yield s

g17.input_gen_func = input_gen_func
##################################### GRAMMAR 18 #####################################
# accepted strings: (l^n r^n)^k where n does not increase (e.g. accepts llrrlr but not lrllrr)

rules = [
	cRule('S', [(['l'], []), 'S']),
	cRule('S', [(['l'], []), 'A']),
	cRule('A', [(['r'], ['l']), 'A']),
	cRule('A', [(['r'], ['l']), 'B']),
	cRule('B', [(['l'], ['r']), 'B']),
	cRule('B', [([], ['r']), 'B']),
	cRule('B', [([], [])]),
	cRule('B', ['A'])
]

g18 = cWK_CFG(['S', 'A', 'B'], ['l', 'r'], 'S', rules, [('l', 'l'), ('r', 'r')])
g18.desc = '(l^n r^n)^k where n does not increase'

def input_gen_func(start, step, accept):
	curLen = start if accept else max(0, start - 6)

	while True:
		lsToGenerate = maxLs = (curLen // 2)
		s = ''

		while lsToGenerate > 0:
			ls = random.randint(1, maxLs)
			lsToGenerate -= ls
			s += 'l' * ls + 'r' * ls
			maxLs = min(lsToGenerate, ls)
		if not accept:
			s += 'lrllrr'
		curLen += step
		yield s

g18.input_gen_func = input_gen_func
##################################### GRAMMAR 19 #####################################
# accepted strings: a^n c^m b^n
# non-bijective complementarity relation

rules = [
	cRule('S', [(['a'], []), 'S', (['b'], [])]),
	cRule('S', [(['a'], []), 'A', (['b'], [])]),
	cRule('A', [(['c'], ['a']), 'A']),
	cRule('A', [([], ['c']), 'B', ([], ['b'])]),
	cRule('B', [([], ['c']), 'B', ([], ['b'])]),
	cRule('B', [([], [])])
]


g19 = cWK_CFG(['S', 'A', 'B'], ['a', 'b', 'c'], 'S', rules, [('a', 'a'), ('b', 'b'), ('c', 'c'), ('a', 'b'), ('b', 'a'), ('a', 'c'), ('c', 'a')])
g19.desc = 'a^n c^m b^n'

def input_gen_func(start, step, accept):
	curLen = start

	while True:
		n = curLen // 5
		s = 'a' * (2*n) + 'c' * n + 'b' * (2*n) + ('' if accept else 'b')
		curLen += step
		yield s
		
g19.input_gen_func = input_gen_func
##################################### GRAMMAR 20 #####################################
# accepted strings: #a + #b = #c + #d
# non-bijective complementarity relation

rules = [
	cRule('S', [(['a'], []), 'S']),
	cRule('S', [(['a'], []), 'A']),
	cRule('A', [(['b'], []), 'A']),
	cRule('A', [(['b'], []), 'B']),
	cRule('B', [(['c'], ['a']), 'B']),
	cRule('B', [(['c'], ['a']), 'C']),
	cRule('C', [(['d'], ['b']), 'C']),
	cRule('C', [(['d'], ['b']), 'D']),
	cRule('D', [([], ['c']), 'D']),
	cRule('D', [([], ['d']), 'D']),
	cRule('D', [([], [])])
]

g20 = cWK_CFG(['S', 'A', 'B', 'C', 'D'], ['a', 'b', 'c', 'd'], 'S', rules, [('a', 'a'), ('b', 'b'), ('c', 'c'), ('d', 'd'), ('a', 'b'), ('b', 'a')])
g20.desc = '#a + #b = #c + #d'

def input_gen_func(start, step, accept):
	curLen = start

	while True:
		m = random.randint(1, (curLen // 2) - 1)
		n = (curLen // 2) - m
		o = random.randint(1, (curLen // 2) - 1)
		p = (curLen // 2) - o
		s = 'a' * m + 'b' * n + 'c' * o + 'd' * p + ('' if accept else 'd')
		curLen += step
		yield s

g20.input_gen_func = input_gen_func
