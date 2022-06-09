# Author: Jan Hammer, xhamme00@stud.fit.vutbr.cz
# Project: WK Grammar Tree Search
# Implementation of the main grammar class - can run WK-CYK or parse tree

from itertools import combinations
from typing import Dict, List, Tuple, Set, Union, Optional, TypeVar, Any, Callable, Generator
from queue import PriorityQueue
from copy import deepcopy
import time
import re

# typings
tNonTerm = str
tTerm = str
tTermLetter = Tuple[List[tTerm], List[tTerm]]
tLetter = TypeVar('tLetter')
tWord = List[tLetter]
tRelation = Tuple[tTerm, tTerm]
t4DInt = Tuple[int, int, int, int]

# helper functions
DEBUG = 0
def debug(s):
	if DEBUG:
		print(s)

# generates all combinations of items from list of lengths 0 - len(list)
def get_all_combinations(lst: List[int]) -> Generator:
	for i in range(len(lst) + 1):
		yield from combinations(lst, i)

# tLetter is either a str (nonterminal) or tuple (segment of terms)
def is_nonterm(letter: tLetter) -> bool:
	return not isinstance(letter, tuple)

def is_term(letter: tLetter) -> bool:
	return isinstance(letter, tuple)

# word printed nicely to read
def wordToStr(word: tWord) -> str:
	rs = []
	for symbol in word:
		if is_term(symbol):
			e1 = ''.join(symbol[0]) if len(symbol[0]) > 0 else 'λ'
			e2 = ''.join(symbol[1]) if len(symbol[1]) > 0 else 'λ'
			rs.append(e1 + '/' + e2)
		else:
			rs.append(symbol)

	return(f'{" ".join(rs)}')

# a node in the search tree
class cTreeNode:
	def __init__(self, word: tWord, upperStrLen: int, lowerStrLen: int, ntLen: int, parent: Optional['cTreeNode'], precedence: int) -> None:
		self.word = word
		self.upperStrLen = upperStrLen # count of terminals in the upper strand
		self.lowerStrLen = lowerStrLen # count of terminals in the lower strand
		self.ntLen = ntLen             # sum of length of all nonterms
		self.parent = parent           # parent node
		self.hashNo = hash(str(word))
		self.precedence = precedence   # value given by node precedence heuristic

	def __hash__(self) -> int:
		return self.hashNo

	# eq and lt needed for priority queue, sorting done by precedence
	def __eq__(self, other: object) -> bool:
		if not isinstance(other, cTreeNode):
			return NotImplemented
		return self.precedence == other.precedence

	def __lt__(self, other: 'cTreeNode') -> bool:
		return self.precedence < other.precedence

# a rule of a grammar
class cRule:
	def __init__(self, lhs: tNonTerm, rhs: tWord) -> None:
		self.lhs = lhs                   # rule's left side (nonterm)
		self.rhs = self.compactize(rhs)  # rule's right side
		self.ntsLen = 0                  # sum of all nonterms lengths
		self.upperCnt = 0                # terms cnt in upper ...
		self.lowerCnt = 0                # .. and lower strand

		self.calculate_cnts()

	# makes rules compact: A -> (a lambda)(lambda a) == A -> (a a)
	def compactize(self, word: tWord) -> tWord:
		i = 0
		# check all pairs of letters...
		while i < len(word) - 1:
			# ... and when both are terms...
			if is_term(word[i]) and is_term(word[i+1]):
				# ...merge them
				word[i:i+2] = [(word[i][0] + word[i+1][0], word[i][1] + word[i+1][1])]
			else:
				i += 1
		return word

	# count terms and nonterms
	def calculate_cnts(self):
		self.ntsLen = 0
		self.upperCnt = 0
		self.lowerCnt = 0
		for letter in self.rhs:
			if is_term(letter):
				self.upperCnt += len(letter[0])
				self.lowerCnt += len(letter[1])
			else:
				self.ntsLen += 1


	def __eq__(self, other):
		return self.rhs == other.rhs and self.lhs == other.lhs

	def __str__(self) -> str:
		return f'{self.lhs} -> {wordToStr(self.rhs)}'

	__repr__ = __str__

	def __hash__(self) -> int:
		return hash((self.lhs, str(self.rhs)))

# the grammar itself
class cWK_CFG:
	def __init__(self, nts: List[tNonTerm], ts: List[tTerm], startSymbol: tNonTerm, rules: List[cRule], relation: List[tRelation]) -> None:
		self.nts = set(nts)                       # set of terms
		self.ts = set(ts)                         # set of nonterms
		self.startSymbol = startSymbol            # starting nonterm
		self.rules = set(rules)                   # set of rules - objects cRules
		self.relation = set(relation)             # set of relations - tuples (term, term)
		self.erasableNts: Set[tNonTerm] = set()   # nonterms that can be erased by lambda-rules
		self.lastCreatedNonTerm = 0               # dynamically created non-term last index
		self.timeLimit = 10                       # max computation time before timeout

		# pruning heuristics - which are active
		self.pruningOptions: Dict[Callable, bool] = {
			self.prune_check_strands_len: True,
			self.prune_check_total_len: True,
			self.prune_check_word_start: True,
			self.prune_check_relation: True,
			self.prune_check_regex: True
		}

		# pruning heuristics - how many times successful
		self.pruneCnts: Dict[Callable, int] = {
			self.prune_check_strands_len: 0,
			self.prune_check_total_len: 0,
			self.prune_check_word_start: 0,
			self.prune_check_relation: 0,
			self.prune_check_regex: 0
		}

		# idx of active node precedence, NTA+TM1 (index 5) is the default one
		self.currentNodePrecedence = 5

		# node precedence heuristics - name and function
		self.nodePrecedenceList = [
			('NTA', self.compute_precedence_NTA),
			('WNTA', self.compute_precedence_WNTA),
			('TM1', self.compute_precedence_TM1),
			('TM2', self.compute_precedence_TM2),
			('TM3', self.compute_precedence_TM3),
			('NTA+TM1', self.compute_precedence_NTA_TM1),
			('NTA+TM2', self.compute_precedence_NTA_TM2),
			('NTA+TM3', self.compute_precedence_NTA_TM3),
			('WNTA+TM1', self.compute_precedence_WNTA_TM1),
			('WNTA+TM2', self.compute_precedence_WNTA_TM2),
			('WNTA+TM3', self.compute_precedence_WNTA_TM3),
			('NONE', self.compute_precedence_no_heuristic)
		]

		# does the definition make sense?
		if not self.is_consistent():
			raise ValueError

		self.precalculate_data()


################# function for init, backup and precalcualtions   ##########################################

	# backups and restores a form of the grammar - can reverse to_wk_cnf
	def backup(self) -> None:
		self.rulesBackup = deepcopy(self.rules)
		self.ntsBackup = self.nts.copy()
		self.tsBackup = self.ts.copy()


	def restore(self) -> None:
		self.rules = self.rulesBackup
		self.nts = self.ntsBackup
		self.ts = self.tsBackup

		self.precalculate_data()


	# check grammar definition consistecy
	def is_consistent(self) -> bool:

		# is starting symbol among nonterminals?
		if self.startSymbol not in self.nts:
			print(f'the starting symbol {self.startSymbol} not found among non-terminals')
			return False

		# are terminals and non-terminals exclusive?
		for t in self.ts:
			if t in self.nts:
				print(f'terminal {t} found among non-terminals')
				return False

		# are all symbols in rules among non-terminals or terminals?
		for rule in self.rules:
			if rule.lhs not in self.nts:
				print(f'rule left-hand side {rule.lhs} not found among non-terminals')
				return False
			for letter in rule.lhs:
				if is_nonterm(letter):
					if letter not in self.nts:
						print(f'rule rhs symbol {rule.lhs} not found among non-terminals')
						return False
				else:
					for symbol in letter[0] + letter[1]:
						if symbol not in self.ts:
							print(f'rule rhs symbol {rule.lhs} not found among terminals')
							return False

		# are all symbols in the relation among terminas?
		for r in self.relation:
			if r[0] not in self.ts or r[1] not in self.ts:
				print(f'relation {r} is invalid')
				return False

		return True


	# precalculations done during init or restore or grammar transformations
	def precalculate_data(self) -> None:
		self.generate_rule_dict()
		self.generate_relation_dict()
		self.find_erasable_nts()
		self.calc_nt_distances()
		self.calc_min_terms_from_nt()
		self.calc_rules_nt_lens()


	# parse rules and create rule dictionary for more efficient access
	def generate_rule_dict(self) -> None:
		self.ruleDict: Dict[tNonTerm, List[cRule]] = {}
		for nt in self.nts:
			self.ruleDict[nt] = []
		for rule in self.rules:
			self.ruleDict[rule.lhs].append(rule)


	# parse the relation and create dictionary for more efficient access
	def generate_relation_dict(self) -> None:
		self.relDict: Dict[tTerm, str] = {}
		for t in self.ts:
			self.relDict[t] = ''

		for a, b in self.relation:
			self.relDict[a] += b


	# can all letters in the word be erased bu a lambda rule
	# helper function - called only from find_erasable_nts
	def _is_word_erasable(self, word: tWord) -> bool:
		for letter in word:
			# non-terminals must be in the erasableNts set to be erasable
			if is_nonterm(letter) and letter not in self.erasableNts:
				return False
			# terminals must be empty
			elif letter != ([], []):
				return False

		return True


	# make a set of all nonterms that can be erased by lambda-rules
	def find_erasable_nts(self) -> None:
		self.erasableNts = set()

		# continue looping until there is no new addition to the set
		loop = True
		while loop:
			loop = False
			for rule in self.rules:
				if self._is_word_erasable(rule.rhs) and rule.lhs not in self.erasableNts:
					# found a new addition - will continue looping
					loop = True
					self.erasableNts.add(rule.lhs)


	#
	def _calc_word_distance(self, word: tWord) -> int:
		maxVal = 0
		for letter in word:
			if is_nonterm(letter):
				maxVal += self.ntDistances[letter]
				#maxVal = max(maxVal, self.ntDistances[letter])
		return maxVal


	# computes minimum number of rules for each nonterminal which lead to terminal string
	def calc_nt_distances(self) -> None:
		MAX_DIST = 20
		self.ntDistances: Dict[tNonTerm, int] = {}

		# init the dictionary with maximum distance
		for nt in self.nts:
			self.ntDistances[nt] = MAX_DIST

		# continue looping until there is no decrement
		loop = True
		while loop:
			loop = False
			for rule in self.rules:
				distance = self._calc_word_distance(rule.rhs) + 1
				if distance < self.ntDistances[rule.lhs]:
					# decrement found - continue looping
					self.ntDistances[rule.lhs] = distance
					loop = True

	# calculates how many terminal can be generated from a word
	# helper function - only called from calc_min_terms_from_nt
	def _calc_terms_from_word(self, word: tWord) -> int:
		retVal = 0
		for letter in word:
			if is_term(letter):
				# for term segments simply count the terminals
				retVal += len(letter[0]) + len(letter[1])
			else:
				# for nonterminals count with their current value
				retVal += self.termsFromNts[letter]
		return retVal


	# calculates minimum amount of terminals that each non-terminal can generates
	def calc_min_terms_from_nt(self):
		MAX_TERMS = 20
		self.termsFromNts: Dict[tNonTerm, int] = {}

		# init the dictionary with max values
		for nt in self.nts:
			self.termsFromNts[nt] = MAX_TERMS

		# loop until there is no change
		loop = True
		while loop:
			loop = False
			for rule in self.rules:
				termsCnt = self._calc_terms_from_word(rule.rhs)
				if termsCnt < self.termsFromNts[rule.lhs]:
					# decrement has been found - continue looping
					self.termsFromNts[rule.lhs] = termsCnt
					loop = True


	# for each grammar rule calculate the rule non-terms len
	def calc_rules_nt_lens(self) -> None:
		for rule in self.rules:
			# len of non term on the left is subtracted
			rule.ntsLen = -self.termsFromNts[rule.lhs]
			for letter in rule.rhs:
				# len of all nonterms on the right is added
				if is_nonterm(letter):
					rule.ntsLen += self.termsFromNts[letter]

################# function for tree search           #######################################################

	# the main space state searching algorithm
	# has an input string for which we test the membership
	# outputs 4-tuple - 1. max number of open states
	#                   2. number of closed states
	#                   3. successful pruning statistics
	#                   4. actual result - True, False, None
	def run_tree_search(self, upperStr: str) -> Tuple[int, int, List[Tuple[str, int]], Optional[bool]]:

		# all pruning active on default
		for key in self.pruneCnts:
			self.pruneCnts[key] = 0

		# create the root node
		distance = self.compute_precedence([self.startSymbol], upperStr)
		initNode = cTreeNode([self.startSymbol], 0, 0, self.termsFromNts[self.startSymbol], None, distance)

		# init the prio queue and the closed states set
		openQueue: Any = PriorityQueue()
		openQueue.put(initNode)
		openQueueLen, openQueueMaxLen = 1, 1
		allStates: Set[int] = set()
		allStates.add(initNode.hashNo)

		startTime = time.time()

		# loop until open queue is empty, solution has been found or time limit reached
		while not openQueue.empty():
			# check the time limit, if exceeded, stop and return None
			currentTime = time.time()
			if currentTime - startTime > self.timeLimit:
				return openQueueMaxLen, len(allStates), list(map(lambda key: (key.__name__, self.pruneCnts[key]), self.pruneCnts.keys())), None

			# get another node with highest priority
			currentNode = openQueue.get()
			openQueueLen -= 1

			# generate all possible sucessors (pruning happens within get_all_successors)
			for nextNode in self.get_all_successors(currentNode, upperStr):
				# check if the node is by chance the solution, if so, return True
				if self.is_result(nextNode.word, upperStr):
					self.printPath(nextNode)
					return openQueueMaxLen, len(allStates), list(map(lambda key: (key.__name__, self.pruneCnts[key]), self.pruneCnts.keys())), True
				# if the current node new, add it to the queue
				if nextNode.hashNo not in allStates:
					openQueueLen += 1
					openQueueMaxLen = max(openQueueMaxLen, openQueueLen)
					openQueue.put(nextNode)
					allStates.add(nextNode.hashNo)

		# queue empty, solution not found - return False
		return openQueueMaxLen, len(allStates), list(map(lambda key: (key.__name__, self.pruneCnts[key]), self.pruneCnts.keys())), False


	# calls active pruning functions one by one, if false is returned, the node will be pruned
	def is_word_feasible(self, node: cTreeNode, goalStr: str) -> bool:
		for pruningFunc, pruningOptActive in self.pruningOptions.items():
			if pruningOptActive and not pruningFunc(node, goalStr):
				debug(f'not feasible - check failed in {pruningFunc.__name__}')
				self.pruneCnts[pruningFunc] += 1
				return False
		return True


	# generates node successors
	def get_all_successors(self, node: cTreeNode, goalStr: str) -> Generator:
		for ntIdx, symbol in enumerate(node.word):
			# find the first non terminal
			if is_nonterm(symbol):
				for rule in self.ruleDict[symbol]:
					# apply every possible rule of the given non-term and create a node
					newWord = self.apply_rule(node.word, ntIdx, rule.rhs)
					newNode = cTreeNode(newWord, node.upperStrLen + rule.upperCnt, node.lowerStrLen + rule.lowerCnt, node.ntLen + rule.ntsLen, node, 0)
					# if the node is not pruned, compute it's precedence and yield it
					if self.is_word_feasible(newNode, goalStr):
						newNode.precedence = self.compute_precedence(newWord, goalStr)
						yield newNode
				# since only the first non-terminal is supposed to be used, finish
				return

	# replace a nonterm with a rule right side within a word
	# needs to merge term segments if possible
	def apply_rule(self, word: tWord, ntIdx: int, ruleRhs: tWord) -> tWord:
		debug(f'\nword: {wordToStr(word)}')
		debug(f'ntIdx: {ntIdx}')
		debug(f'rule: {word[ntIdx] + " -> " + wordToStr(ruleRhs)}')

		# we can merge with the previous letter if there is one and its terminal segment
		mergePrev = ntIdx > 0 and is_term(word[ntIdx - 1])

		# can we merge with the next terminal?
		mergeNext = ntIdx < len(word) - 1 and is_term(word[ntIdx + 1])

		# rule right side is just one letter - a terminal segment
		# in that case we might need to merge on both sides
		if len(ruleRhs) == 1 and is_term(ruleRhs[0]):
			if mergePrev and mergeNext:
				# merge on both sides
				mergedUpper = word[ntIdx - 1][0] + ruleRhs[0][0] + word[ntIdx + 1][0]
				mergedLower = word[ntIdx - 1][1] + ruleRhs[0][1] + word[ntIdx + 1][1]
				retval = word[:ntIdx - 1] + [(mergedUpper, mergedLower)] + word[ntIdx + 2:]
			elif mergePrev:
				# merge only with previous segment
				mergedUpper = word[ntIdx - 1][0] + ruleRhs[0][0]
				mergedLower = word[ntIdx - 1][1] + ruleRhs[0][1]
				retval = word[:ntIdx - 1] + [(mergedUpper, mergedLower)] + word[ntIdx + 1:]
			elif mergeNext:
				# merge with followinf segment
				mergedUpper = ruleRhs[0][0] + word[ntIdx + 1][0]
				mergedLower = ruleRhs[0][1] + word[ntIdx + 1][1]
				retval = word[:ntIdx] + [(mergedUpper, mergedLower)] + word[ntIdx + 2:]
			else:
				# nothing to merge, just replace the non-term
				retval = word[:ntIdx] + [ruleRhs[0]] + word[ntIdx + 1:]
		else:
			# there is a terminal segment as the first letter of rule rhs
			mergePrev = mergePrev and is_term(ruleRhs[0])

			# there is a terminal segment as the last letter of rule rhs
			mergeNext = mergeNext and is_term(ruleRhs[-1])

			if ntIdx > 0 and mergePrev and mergeNext:
				# merge on both sides
				mergedUpperPrev = word[ntIdx - 1][0] + ruleRhs[0][0]
				mergedLowerPrev = word[ntIdx - 1][1] + ruleRhs[0][1]
				mergedUpperNext = ruleRhs[-1][0] + word[ntIdx + 1][0]
				mergedLowerNext = ruleRhs[-1][1] + word[ntIdx + 1][1]
				retval = word[:ntIdx - 1] + [(mergedUpperPrev, mergedLowerPrev)] + ruleRhs[1:-1] + [(mergedUpperNext, mergedLowerNext)] + word[ntIdx + 2:]
			elif mergePrev:
				# merge only with previous segment
				mergedUpperPrev = word[ntIdx - 1][0] + ruleRhs[0][0]
				mergedLowerPrev = word[ntIdx - 1][1] + ruleRhs[0][1]
				retval = word[:ntIdx - 1] + [(mergedUpperPrev, mergedLowerPrev)] + ruleRhs[1:] + word[ntIdx + 1:]
			elif mergeNext:
				# merge only with following segment
				mergedUpperNext = ruleRhs[-1][0] + word[ntIdx + 1][0]
				mergedLowerNext = ruleRhs[-1][1] + word[ntIdx + 1][1]
				retval = word[:ntIdx] + ruleRhs[:-1] + [(mergedUpperNext, mergedLowerNext)] + word[ntIdx + 2:]
			else:
				# nothing to merge, just replace the non-term
				retval = word[:ntIdx] + ruleRhs + word[ntIdx + 1:]

		debug(f'result: {wordToStr(retval)}')
		return retval


	# is a word a solution?
	def is_result(self, word: tWord, goal: str) -> bool:

		# word lenght must be of len 1 and it must be terminal segment
		if len(word) != 1 or is_nonterm(word[0]):
			return False

		# the len of both strands must be the same as the input length
		if len(word[0][0]) != len(word[0][1]) or len(word[0][0]) != len(goal) :
			return False

		# the complementarity relation must hold
		for symbol1, symbol2 in zip(word[0][0], word[0][1]):
			if (symbol1, symbol2) not in self.relation:
				return False

		# the upper strand must be equal to the input
		if ''.join(word[0][0]) != goal:
			return False

		return True


	# in debug mode prints path of found solution
	def printPath(self, node: cTreeNode) -> None:
		currentNode: Optional[cTreeNode] = node
		while currentNode:
			debug(f' >>> {wordToStr(currentNode.word)}')
			currentNode = currentNode.parent

################# pruning functions                  #######################################################

	# activate/deactivate heuristics
	def activate(self, name: str, value: bool=True) -> None:
		if name == 'SL':
			self.pruningOptions[self.prune_check_strands_len] = value
		elif name == 'TL':
			self.pruningOptions[self.prune_check_total_len] = value
		elif name == 'WS':
			self.pruningOptions[self.prune_check_word_start] = value
		elif name == 'RL':
			self.pruningOptions[self.prune_check_relation] = value
		elif name == 'RE':
			self.pruningOptions[self.prune_check_regex] = value
		else:
			nodePrecNames = list(map(lambda x: x[0], self.nodePrecedenceList))
			if name not in nodePrecNames:
				print(f'unknown heuristic: "{name}"')
			elif value:
				self.currentNodePrecedence = nodePrecNames.index(name)
			else:
				print(f'cannot deactivate node precedence heuristic, activate a different one')


	# SL - is one of the strands too long?
	def prune_check_strands_len(self, node: cTreeNode, goalStr: str) -> bool:
		return max(node.upperStrLen, node.lowerStrLen) <= len(goalStr)


	# TL - is the word overall too long (counting with nonterm lens)?
	def prune_check_total_len(self, node: cTreeNode, goalStr: str) -> bool:
		return node.upperStrLen + node.lowerStrLen + node.ntLen <= 2 * len(goalStr)


	# WS - does the first letter (if it's term segment) correspond to the input start?
	def prune_check_word_start(self, node: cTreeNode, goalStr: str) -> bool:
		return is_nonterm(node.word[0]) or goalStr.startswith(''.join(node.word[0][0]))


	# RL - is the complementary relation met?
	def prune_check_relation(self, node: cTreeNode, goalStr: str) -> bool:
		if is_nonterm(node.word[0]):
			return True
		shorterStrand = min(len(node.word[0][0]), len(node.word[0][1]))
		for idx in range(shorterStrand):
			if (node.word[0][0][idx], node.word[0][1][idx]) not in self.relation:
				return False
		return True


	# make word into regex
	# helper function only called from prune_check_regex
	def _word_to_regex(self, word: tWord) -> str:

		# starting nonterm is repesented by omitting ^
		regex = '^' if is_term(word[0]) else ''

		for idx, letter in enumerate(word):
			if is_nonterm(letter) and idx > 0 and is_term(word[idx-1]):
				# nonterm can generate in general anything - use wildcard
				regex += '.*'
			elif is_term(letter):
				# term from the upper strand stand for themselves
				regex += ''.join(letter[0])

		if is_term(word[-1]):
			# ending nonterm is repesented by omitting $
			regex += '$'

		return regex


	# RE - does the input correspond to the regex made from word?
	def prune_check_regex(self, node: cTreeNode, goalStr: str) -> bool:
		regex = self._word_to_regex(node.word)
		return re.compile(regex).search(goalStr) is not None

################# node precedence functons           #######################################################

	# just call the right precedence method based on currentNodePrecedence
	def compute_precedence(self, word: tWord, goalStr: str) -> int:
		return self.nodePrecedenceList[self.currentNodePrecedence][1](word, goalStr)


	# no heurictic - return 0
	def compute_precedence_no_heuristic(self, word: tWord, goal: str) -> int:
		return 0


	# return number of nonterms
	def compute_precedence_NTA(self, word: tWord, goal: str) -> int:
		evaluation = 0
		for letter in word:
			if is_nonterm(letter):
				evaluation += 1
		return evaluation


	# return sum of distances of all nonterms
	def compute_precedence_WNTA(self, word: tWord, goal: str) -> int:
		evaluation = 0
		for letter in word:
			if is_nonterm(letter):
				evaluation += self.ntDistances[letter]
		return evaluation


	# look only at terminals with some upper strands
	# if symbol in upper strand match goal -> priority increases
	# once you find one that doesn't, finish
	def compute_precedence_TM1(self, word: tWord, goal: str) -> int:
		goalIdx, evaluation = 0, 0

		for letter in word:
			if is_term(letter):
				for symbol in letter[0]:
					if len(goal) > goalIdx and symbol == goal[goalIdx]:
						evaluation -= 1
						goalIdx += 1
					else:
						return evaluation
		return evaluation


	# look at terminals with some upper strands only
	# if symbol in upper strand match goal -> priority increases
	# but unlike previous case, if you find one that doesn't match input, just descrease priority and continue
	def compute_precedence_TM2(self, word: tWord, goal: str) -> int:
		goalIdx, evaluation = 0, 0

		for letter in word:
			if is_term(letter):
				for symbol in letter[0]:
					if len(goal) > goalIdx and symbol == goal[goalIdx]:
						evaluation -= 1
					else:
						evaluation += 1
					goalIdx += 1
		return evaluation


	# look at first letter
	# if it is terminal and has upper strand - check how it matches goal - increase priority
	# else do nothing
	def compute_precedence_TM3(self, word: tWord, goal: str) -> int:
		goalIdx, evaluation = 0, 0

		if len(word) > 0 and is_term(word[0]):
			for symbol in word[0][0]:
				if len(goal) > goalIdx and symbol == goal[goalIdx]:
					evaluation -= 1
					goalIdx += 1
				else:
					return evaluation
		return evaluation


	# NTA + TM1 combination
	def compute_precedence_NTA_TM1(self, word: tWord, goal: str) -> int:
		goalIdx, evaluation = 0, 0

		for letter in word:
			if is_term(letter):
				for symbol in letter[0]:
					if len(goal) > goalIdx and symbol == goal[goalIdx]:
						evaluation -= 10
						goalIdx += 1
					else:
						return evaluation

			else:
				evaluation += 1
		return evaluation


	# NTA + TM2 combination
	def compute_precedence_NTA_TM2(self, word: tWord, goal: str) -> int:
		goalIdx, evaluation = 0, 0

		for letter in word:
			if is_term(letter):
				for symbol in letter[0]:
					if len(goal) > goalIdx and symbol == goal[goalIdx]:
						evaluation -= 10
						goalIdx += 1
					else:
						evaluation += 10
						goalIdx += 1

			else:
				evaluation += 1
		return evaluation


	# NTA + TM3 combination
	def compute_precedence_NTA_TM3(self, word: tWord, goal: str) -> int:
		goalIdx, evaluation = 0, 0

		for letter in word:
			if is_nonterm(letter):
				evaluation += 1

		if len(word) > 0 and is_term(word[0]):
			for symbol in word[0][0]:
				if len(goal) > goalIdx and symbol == goal[goalIdx]:
					evaluation -= 10
					goalIdx += 1
				else:
					return evaluation
		return evaluation


	# WNTA + TM1 combination
	def compute_precedence_WNTA_TM1(self, word: tWord, goal: str) -> int:
		goalIdx, evaluation = 0, 0

		for letter in word:
			if is_term(letter):
				for symbol in letter[0]:
					if len(goal) > goalIdx and symbol == goal[goalIdx]:
						evaluation -= 10
						goalIdx += 1
					else:
						return evaluation

			else:
				evaluation += self.ntDistances[letter]
		return evaluation


	# WNTA + TM2 combination
	def compute_precedence_WNTA_TM2(self, word: tWord, goal: str) -> int:
		goalIdx, evaluation = 0, 0

		for letter in word:
			if is_term(letter):
				for symbol in letter[0]:
					if len(goal) > goalIdx and symbol == goal[goalIdx]:
						evaluation -= 10
					else:
						evaluation += 10
					goalIdx += 1

			else:
				evaluation += self.ntDistances[letter]
		return evaluation


	# WNTA + TM3 combination
	def compute_precedence_WNTA_TM3(self, word: tWord, goal: str) -> int:
		goalIdx, evaluation = 0, 0

		for letter in word:
			if is_nonterm(letter):
				evaluation += self.ntDistances[letter]

		if len(word) > 0 and is_term(word[0]):
			for symbol in word[0][0]:
				if len(goal) > goalIdx and symbol == goal[goalIdx]:
					evaluation -= 10
					goalIdx += 1
				else:
					return evaluation
		return evaluation

################# transformation to CBF              #######################################################

	# create new nonterm Ni where i increases can specify differnt prefix than N
	def createNewNt(self, prefix: str = 'N') -> tNonTerm:
		self.lastCreatedNonTerm += 1
		# double check the the nonterm is unique (should be)
		while prefix + str(self.lastCreatedNonTerm) in self.nts:
			self.lastCreatedNonTerm += 1
		return prefix + str(self.lastCreatedNonTerm)


	# remove lambda rules (A -> lambda/lamda)
	def remove_lambda_rules(self) -> None:
		newRules: Set[cRule] = set()

		for rule in self.rules:

			# we need to differentiate between more occurences of the same nonterm in the word
			# hence we use erasableIdxs
			erasableIdxs: List[int] = []
			for idx, letter in enumerate(rule.rhs):
				if is_nonterm(letter) and letter in self.erasableNts:
					erasableIdxs.append(idx)

			# get all combinations of word with or without all erasable nonterms
			for idxLst in get_all_combinations(erasableIdxs):
				newRuleRhs = []
				# for each such combination create a special rule
				for idx, letter in enumerate(rule.rhs):
					# compose the rule rhs - add erasable nonterms according to the current combination
					if idx not in erasableIdxs or idx in idxLst:
						newRuleRhs.append(deepcopy(letter))

				newRule = cRule(rule.lhs, newRuleRhs)
				# make sure the rule isn't empty (we removing those and is unique)
				if newRule.rhs != [([], [])] and newRule.rhs != [] and newRule not in newRules:
					newRules.add(newRule)

		self.rules = newRules
		self.precalculate_data()


	# remove unit rules (A -> B)
	def remove_unit_rules(self) -> None:

		# dictionary - which nonterm can generate key nonterm
		simpleRules: Dict[tNonTerm, List[tNonTerm]] = {}

		# init - every nonterm can generate itself (in 0 steps)
		for nt in self.nts:
			simpleRules[nt] = [nt]

		# loop until no change occure
		loop = True
		while loop:
			loop = False
			for rule in self.rules:
				if len(rule.rhs) == 1 and is_nonterm(rule.rhs[0]) and rule.lhs != rule.rhs:
					# find all non terminals which have lhs in their N but no rhs
					for k, v in simpleRules.items():
						if rule.lhs in v and rule.rhs[0] not in v:
							# a new simple rule found - keep looping
							simpleRules[k].append(rule.rhs[0])
							loop = True

		newRules: Set[cRule] = set()
		for rule in self.rules:
			# if this is not a simple rule...
			if len(rule.rhs) != 1 or is_term(rule.rhs[0]):
				# ...create rules replacing the lhs with nonterms that can generate this one
				for k, v in simpleRules.items():
					if rule.lhs in v:
						newRules.add(cRule(k, deepcopy(rule.rhs)))

		self.rules = newRules
		self.precalculate_data()


	# if a symbol cannot generate terminal string, it can never be used on a successful run
	# it can be erased (and rules using it)
	def remove_unterminatable_symbols(self) -> None:
		terminatableNts: Set[tNonTerm] = set()

		# keep looping until no change occures
		loop = True
		while loop:
			loop = False
			for rule in self.rules:
				# terminatable symbol generates only terms, or other terminatable symbols
				if len(list(filter(lambda letter: is_nonterm(letter) and letter not in terminatableNts, rule.rhs))) == 0:
					if rule.lhs not in terminatableNts:
						terminatableNts.add(rule.lhs)
						# found something - keep looping
						loop = True


		# check all rules and remove those that use unterminatable symbols
		newRules: Set[cRule] = set()
		for rule in self.rules:
			if rule.lhs in terminatableNts and all(map(lambda letter: is_term(letter) or letter in terminatableNts, rule.rhs)):
				newRules.add(rule)

		# keep only nonterms that are terminatable
		self.nts = self.nts.intersection(terminatableNts)
		self.rules = newRules
		self.precalculate_data()


	# if a symbol cannot be generated from the starting symbol, it is useless
	# it can be erased (and rules using it)
	def remove_unreachable_symbols(self) -> None:
		# both nts and ts can be unreachable, starting symbol is reachable trivially
		reachableNts: Set[tNonTerm] = set(self.startSymbol)
		reachableTs: Set[tTerm] = set()

		# keep looping until there is no change, find all reachable symbols
		loop = True
		while loop:
			loop = False
			# follow all rules, see what you can find
			for rule in self.rules:
				if rule.lhs in reachableNts:
					for letter in rule.rhs:
						if is_nonterm(letter):
							if letter not in reachableNts:
								# new reachable nonterm found, keep looping
								reachableNts.add(letter)
								loop = True
						else:
							for terminal in letter[0] + letter[1]:
								if terminal not in reachableTs:
									# new reachable term found, keep looping
									reachableTs.add(terminal)
									loop = True

		# check all rules and remove those that use unreachable symbols
		newRules: Set[cRule] = set()
		for rule in self.rules:
			if rule not in newRules and rule.lhs in reachableNts and all(map(lambda letter: is_term(letter) or letter in reachableNts, rule.rhs)):
				newRules.add(rule)

		# keep only terminal that are reachable
		self.nts = self.nts.intersection(reachableNts)
		self.ts = self.ts.intersection(reachableTs)
		self.rules = newRules

		self.precalculate_data()


	# splits a segment - creates a new one with 1 symbol
	# helper function use only in dismantle_term_letters
	def _pop_term_from_letter(self, letter: tTermLetter) -> tTermLetter:
		if len(letter[0]) > len(letter[1]):
			t = letter[0].pop(0)
			return ([t], [])
		else:
			t = letter[1].pop(0)
			return ([], [t])


	# each terminal in rules (that don't generate only one terminal) is replaced by non-term
	# and new rule is generated for to place the term there
	def dismantle_term_letters(self) -> None:
		newRules: List[cRule] = []

		for rule in self.rules:
			# rules of the form A -> a/lambda, A -> lambda/a  are ok
			if len(rule.rhs) == 1 and is_term(rule.rhs[0]) and len(rule.rhs[0][0]) + len(rule.rhs[0][1]) == 1:
				continue

			# otherwise find terminal segments in the rhs...
			for idx, letter in enumerate(rule.rhs):
				if is_term(letter):
					# ...replace each term from the segment (but the last one) them with a new nonterm
					newNt = self.createNewNt()
					self.nts.add(newNt)
					rule.rhs[idx] = newNt

					# if there is only one letter - term segment - we don't want to just replace it with a nonterm
					# we would get a unit rule, lets split the segment
					if len(rule.rhs) == 1:
						rule.rhs.insert(0, self._pop_term_from_letter(letter))

					currentNt = newNt
					# pop terms from this segment one by one until only one is left
					# for each one create a new rule
					while len(letter[0]) + len(letter[1]) > 1:
						t = self._pop_term_from_letter(letter)
						newNt = self.createNewNt()
						self.nts.add(newNt)
						newRules.append(cRule(currentNt, [t, newNt]))
						currentNt = newNt

					newRules.append(cRule(currentNt, [letter]))
			rule.calculate_cnts()

		self.rules.update(newRules)
		self.precalculate_data()


	# does the actual breaking down of rules
	# helper function use only in transform_to_wk_cnf_form
	def _dismantle_rule(self, rule: cRule) -> List[cRule]:
		newRules: List[cRule] = []

		# in rules of form (A -> term B) replace the term with a new nonterm and create a rule
		for idx, letter in enumerate(rule.rhs):
			if is_term(letter):
				newNt = self.createNewNt()
				newRules.append(cRule(newNt, [letter]))
				rule.rhs[idx] = newNt
				self.nts.add(newNt)

		currentNt: tNonTerm = rule.lhs

		# rules of form (A -> BCD...) break down the rhs with new nonterm and rules until the rhs len is 2
		while len(rule.rhs) > 2:
			newNt = self.createNewNt()
			self.nts.add(newNt)
			newRules.append(cRule(currentNt, [rule.rhs.pop(0), newNt]))
			currentNt = newNt

		newRules.append(cRule(currentNt, rule.rhs))
		return newRules


	# rules of form (A -> BCD...) or form (A -> a\lambda B) (A -> lambda/a B) need to be futher broken down
	def transform_to_wk_cnf_form(self) -> None:
		newRules: Set[cRule] = set()

		for rule in self.rules:
			# the rules in the WK-CNF form we keep
			if len(rule.rhs) == 1 and is_term(rule.rhs[0]) or len(rule.rhs) == 2 and is_nonterm(rule.rhs[0]) and is_nonterm(rule.rhs[1]):
				newRules.add(rule)

			# as for the rest, swap terminal letters for respective non-terminals and break down words longer than 2
			elif len(rule.rhs) >= 2:
				newRules.update(self._dismantle_rule(rule))

		self.rules = newRules
		self.precalculate_data()


	# transform grammar to WK-CNF
	def to_wk_cnf(self) -> None:
		self.remove_lambda_rules()
		self.remove_unit_rules()
		self.remove_unterminatable_symbols()
		self.remove_unreachable_symbols()
		self.dismantle_term_letters()
		self.transform_to_wk_cnf_form()

		# possible optimization - only one non-term generates each term among the dynamically generated nonterms
		# - could be the last step of transformation, but the impact is probably negligable

################# run wk-cyk                         #######################################################

	# add a nonterm to the covering set
	def addToX(self, idx: t4DInt, nt: tNonTerm) -> None:
		if idx not in self.X:
			self.X[idx] = []
		self.X[idx].append(nt)


	# find rule(s) that have nonterms from idx1, idx2 as the right side
	# add left hand side of such rules to target set
	def find_generating_rules(self, idx1: t4DInt, idx2: t4DInt, target: t4DInt) -> None:
		if idx1 not in self.X or idx2 not in self.X:
			return
		for rule in self.rules:
			if rule.rhs[0] in self.X[idx1] and rule.rhs[1] in self.X[idx2]:
				self.addToX(target, rule.lhs)


	# find non terminals that can generate term segment given by the four indexes
	def compute_set(self, i: int, j: int, k: int ,l: int) -> None:
		# i = j = 0 -> segment has only lower part
		if i == 0 and j == 0:
			for t in range(k, l):
				self.find_generating_rules((0, 0, k, t), (0, 0 ,t+1, l), (i, j, k, l))

		# k = l = 0 -> segment has only upper part
		elif k == 0 and l == 0:
			for s in range(i, j):
				self.find_generating_rules((i, s, 0, 0), (s+1, j ,0 , 0), (i, j, k, l))

		# segment has symbols from both strands find all possible combinations, there are 7 types of divisions
		else:
			# 1. first non-term generates upper strand, the second lower...
			self.find_generating_rules((i, j, 0, 0), (0, 0, k, l), (i, j, k, l))
			# 2. ... or vice versa
			self.find_generating_rules((0, 0, k, l), (i, j, 0, 0), (i, j, k, l))

			# 3. both nonterms contain symbols from both strands
			for s in range(i, j):
				for t in range(k, l):
					self.find_generating_rules((i, s, k, t), (s+1, j, t+1, l), (i, j, k, l))

			for s in range(i, j):
				# 4. first contains whole upper and bit of lower strand, the second contains rest of lower strand...
				self.find_generating_rules((i, s, k, l), (s+1, j, 0, 0), (i, j, k, l))
				# 5. ...or vice versa
				self.find_generating_rules((i, s, 0, 0), (s+1, j, k, l), (i, j, k, l))

			for t in range(k, l):
				# 6. first contains whole lower and bit of upper strand, the second contains rest of upper strand...
				self.find_generating_rules((i, j, k, t), (0, 0, t+1, l), (i, j, k, l))
				# 7. ...or vice versa
				self.find_generating_rules((0, 0, k, t), (i, j, t+1, l), (i, j, k, l))


	# the main wk-cyk function
	# technically, double stranded string (2 strings) should be on the input, but since they have to be identical,
	# we use one string (goalStr) in the role of upper or lower strand
	def run_wk_cyk(self, goalStr: str) -> Optional[bool]:
		start_time = time.time()
		n = len(goalStr)
		self.X: Dict[t4DInt, List[tNonTerm]] = {}  # what nonterms can generate segment soecified by the indexes

		# the first step - finding nonterm that generate individual terms
		# for each term in the input find the appropriate rules and add to X
		for i, word in enumerate(goalStr):
			for rule in self.rules:
				if len(rule.rhs) == 1 and is_term(rule.rhs[0]):
					letter = rule.rhs[0]
					if len(letter[0]) == 1 and letter[0][0] == word:
						self.addToX((i+1, i+1, 0, 0), rule.lhs)
					elif len(letter[1]) == 1 and letter[1][0] == word:
						self.addToX((0, 0, i+1, i+1), rule.lhs)

		# continuously increase the len of analysed segment
		for y in range(2, 2*n+1):
			# check the time limit, if it has been exceeded return None
			current_time = time.time()
			if current_time - start_time > self.timeLimit:
				return None

			# do the search for all segment len divisions between upper (alpha) and lower (beta) strand
			for beta in range(max(y - n, 0), min(n, y)+1):
				alpha = y - beta

				if alpha == 0:
					# symbols only in lower strand
					i = j = 0
					for k in range(1, n-y+2):
						l = k + y - 1
						self.compute_set(i, j, k, l)

				elif beta == 0:
					# symbols only in upper strand
					k = l = 0
					for i in range(1, n - y + 2):
						j = i + y - 1
						self.compute_set(i, j, k, l)

				else:
					# symbols in both strnads, consider all posiible distributions
					for i in range(1, n - alpha + 2):
						for k in range(1, n - beta + 2):
							j = i + alpha - 1
							l = k + beta - 1
							self.compute_set(i, j, k, l)

		# the result is positive if
		# 1. the set of symbols that generate the whole input is non empty
		# 2. starting symbol is in this set
		return (1, n, 1, n) in self.X and self.startSymbol in self.X[(1, n, 1, n)]
