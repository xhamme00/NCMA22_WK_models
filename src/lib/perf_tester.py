# Author: Jan Hammer, xhamme00@stud.fit.vutbr.cz
# Project: WK Grammar Tree Search
# Tester class

import time

# class simply for gathering test case results
class cResult:
	def __init__(self, name):
		self.name = name
		self.times = []
		self.statesOpen = []
		self.statesClosed = []
		self.timeouts = []
		self.inputLens = []


	def update(self, time, statesOpen, statesClosed, timeout, inputLen=None):
		self.times.append(time)
		self.statesOpen.append(statesOpen)
		self.statesClosed.append(statesClosed)
		self.timeouts.append(timeout)
		self.inputLens.append(inputLen)

class cPerfTester:
	def __init__(self, casesLst = []):
		self.testCnt = 0
		self.allResults = [cResult(name) for name in casesLst]


	# print the final results into a table
	def printResults(self):
		print(f'|{"="*106}|')
		print(f'|{" "*38} FINAL RESULTS{" "*53} |')
		print(f'|{"="*106}|')
		print(f'| TEST CASE{" "*30}| time total | open states total | closed states total | timeouts |')
		print(f'|{"-"*106}|')

		for result in self.allResults:
			totalTime = round(sum(result.times), 4)
			print(f'| {result.name:39}| {totalTime:10} | {sum(result.statesOpen):17} | {sum(result.statesClosed):19} |  {sum(result.timeouts):7} |')
		print(f'|{"="*106}|')


	# print the header of the result table
	def printHeader(self, grammar, inputStr, shouldAccept, title):
		print(f'|{"="*150}|')
		print(f'| TEST {self.testCnt:3}{" "*141}|')
		print(f'|{"="*150}|')
		print(f'| GRAMMAR{" "*35}| {grammar.desc:105}|')
		lengths = f'{len(grammar.rules)} / {len(grammar.nts)} / {len(grammar.ts)}'
		print(f'| RULES / NON-TERMINALS / TERMINALS COUNT   | {lengths:105}|')
		if inputStr is not None:
			if len(inputStr) > 90:
				inputStr = inputStr[:80] + f'... [length {len(inputStr)}]'
			print(f'| INPUT STRING{" "*30}| {inputStr:105}|')
		if shouldAccept is not None:
			print(f'| SHOULD ACCEPT{" "*29}| {("Yes" if shouldAccept else "No"):105}|')
		print(f'| TIMEOUT{" "*35}| {str(grammar.timeLimit):105}|')
		print(f'|{"-"*150}|')
		print(f'|{title}| TIME      | STATES QUEUED+CLOSED  | STATES PRUNED (SL, TL, WS, RL, RE)   | ACCEPTED |')
		print(f'|{"-"*150}|')


	# runs a tree search n times, calculates and returns avereges for all metrics
	def run_test_ntimes(self, grammar, inputStr, shouldAccept, times):
		statesOpenTotal, statesAllTotal, prunesTotal, timeTotal, results = 0, 0, [0, 0, 0, 0, 0, 0], 0, []

		# run the tree search n times
		for i in range(times):
			start = time.time()
			statesOpen, statesAll, prunes, result = grammar.run_tree_search(inputStr)
			end = time.time()
			timeTaken = round(end - start, 4)

			# gather results
			statesOpenTotal += statesOpen
			statesAllTotal += statesAll
			prunesTotal = [a + b[1] for a, b in zip(prunesTotal, prunes)]
			timeTotal += timeTaken
			results.append(result)

		# calculate the metrics averages
		statesOpenTotal = round(statesOpenTotal/times)
		statesAllTotal = round(statesAllTotal/times)
		prunesTotal = list(map(lambda x: round(x/times), prunesTotal))
		timeTotal = round(timeTotal/times, 4)

		# if there was one timeout, the final result it timeout
		finalResult = ('TRUE' if shouldAccept else 'FALSE')
		for r in results:
			if r is None:
				finalResult = 'TIMEOUT'
				break
			elif r != shouldAccept:
				finalResult = 'ERROR'
				break

		return statesOpenTotal, statesAllTotal, prunesTotal, timeTotal, finalResult


	# iterates over all node precedence heuristics in the grammar, runs tree search for each one, prints results
	def run_node_precedence_test(self, grammar, inputStr, shouldAccept, times=1):

		# all pruning should be active for node precedence comparison
		for k in grammar.pruningOptions:
			grammar.pruningOptions[k] = True

		self.testCnt += 1
		self.printHeader(grammar, inputStr, shouldAccept, " NODE PRECEDENCE HEURISTIC" + " "*38)

		# run test for each item from nodePrecedenceList
		for idx, t in enumerate(grammar.nodePrecedenceList):
			grammar.currentNodePrecedence = idx
			statesOpen, statesAll, prunes, timeTaken, result = self.run_test_ntimes(grammar, inputStr, shouldAccept, times)
			strategy = grammar.nodePrecedenceList[idx][0]
			statesStr = str(statesOpen) + ' + ' + str(statesAll-statesOpen)
			prunesStr = str(prunes).replace('[', '').replace(']', '')

			# save and print result
			self.allResults[idx].update(timeTaken, statesOpen, statesAll-statesOpen, result == 'TIMEOUT')
			print(f'| {strategy:63}| {timeTaken:9} | {statesStr:21} | {prunesStr:36} | {result:8} |')

		print(f'|{"="*150}|\n\n\n')


	# iterates over all pruning heuristics, turns them off one at a time
	def run_prune_test(self, grammar, inputStr, shouldAccept, times=1):

		self.testCnt += 1
		self.printHeader(grammar, inputStr, shouldAccept, " PRUNING HEURISTICS" + " "*45)

		# first test with all the pruning options active for comparison
		for k in grammar.pruningOptions:
			grammar.pruningOptions[k] = True
		statesOpen, statesAll, prunes, timeTaken, result = self.run_test_ntimes(grammar, inputStr, shouldAccept, times)

		idx = 0
		pruning = 'ALL ON'
		prunesStr = str(prunes).replace('[', '').replace(']', '')
		statesStr = str(statesOpen) + ' + ' + str(statesAll-statesOpen)

		# save and print the results
		self.allResults[idx].update(timeTaken, statesOpen, statesAll-statesOpen, result == 'TIMEOUT')
		print(f'| {pruning:63}| {timeTaken:9} | {statesStr:21} | {prunesStr:36} | {result:8} |')

		# next, test with one pruning option off for each item
		prevKey = None
		for key in grammar.pruningOptions:
			idx += 1
			# switch on the previous one, switch off the current one
			if prevKey is not None:
				grammar.pruningOptions[prevKey] = True
			grammar.pruningOptions[key] = False
			prevKey = key

			# run the test
			statesOpen, statesAll, prunes, timeTaken, result = self.run_test_ntimes(grammar, inputStr, shouldAccept, times)
			pruning = key.__name__ + ' OFF'
			prunesStr = str(prunes).replace('[', '').replace(']', '')
			statesStr = str(statesOpen) + ' + ' + str(statesAll-statesOpen)

			# print and save results
			self.allResults[idx].update(timeTaken, statesOpen, statesAll-statesOpen, result == 'TIMEOUT')
			print(f'| {pruning:63}| {timeTaken:9} | {statesStr:21} | {prunesStr:36} | {result:8} |')

		# at the end, turn off all pruning and run the test for comaprison
		for k in grammar.pruningOptions:
			grammar.pruningOptions[k] = False
		idx += 1
		statesOpen, statesAll, prunes, timeTaken, result = self.run_test_ntimes(grammar, inputStr, shouldAccept, times)
		pruning = 'ALL OFF'
		prunesStr = str(prunes).replace('[', '').replace(']', '')
		statesStr = str(statesOpen) + ' + ' + str(statesAll-statesOpen)

		# print and save results
		self.allResults[idx].update(timeTaken, statesOpen, statesAll-statesOpen, result == 'TIMEOUT')
		print(f'| {pruning:63}| {timeTaken:9} | {statesStr:21} | {prunesStr:36} | {result:8} |')
		print(f'|{"="*150}|\n\n\n')


	# runs a wk-cyk test with increasing length of input
	def run_wk_cyk_test(self, grammar, input_gen_func, shouldAccept):
		self.testCnt += 1
		self.printHeader(grammar, None, shouldAccept, " INPUT LENGTH" + " "*51)
		resultObj = cResult(self.testCnt)

		i = 0
		while True:
			# input_gen_func generates inputs of inreasing lengths
			inputStr = next(input_gen_func)
			start = time.time()
			result = grammar.run_wk_cyk(inputStr)
			end = time.time()
			timeTaken = round(end - start, 2)
			statesStr = prunesStr = 'N/A'
			
			if result is None:
				result = 'TIMEOUT'
			elif result != shouldAccept:
				result = 'ERROR'
			elif result:
				result = 'TRUE'
			else:
				result = 'FALSE'

			# print and save result
			print(f'| {str(len(inputStr)):63}| {timeTaken:9} | {statesStr:21} | {prunesStr:36} | {result:8} |')
			resultObj.update(timeTaken, 0, 0, result == 'TIMEOUT', len(inputStr))

			# do 30 tests or until it timeouts
			if i > 30 or result == 'TIMEOUT':
				break
			i += 1

		# save the test
		self.allResults.append(resultObj)
		print(f'|{"="*150}|\n\n\n')


	# runs a tree search test with increasing length of input
	def run_speed_test(self, grammar, input_gen_func, shouldAccept, times=1):
		self.testCnt += 1
		self.printHeader(grammar, None, shouldAccept, " INPUT LENGTH" + " "*51)
		resultObj = cResult(self.testCnt)

		i = 0
		while True:
			# input_gen_func generates inputs of inreasing lengths
			inputStr = next(input_gen_func)
			statesOpen, statesAll, prunes, timeTaken, result = self.run_test_ntimes(grammar, inputStr, shouldAccept, times)
			statesStr = str(statesOpen) + ' + ' + str(statesAll-statesOpen)
			prunesStr = str(prunes).replace('[', '').replace(']', '')

			# print and save result
			print(f'| {str(len(inputStr)):63}| {timeTaken:9} | {statesStr:21} | {prunesStr:36} | {result:8} |')
			resultObj.update(timeTaken, statesOpen, statesAll-statesOpen, result == 'TIMEOUT', len(inputStr))

			# do 30 tests or until it timeouts
			if i > 30 or result == 'TIMEOUT':
				break
			i += 1

		# save the test
		self.allResults.append(resultObj)
		print(f'|{"="*150}|\n\n\n')


	# runs a tree search with a manually specified input, used to test edge case inputs
	def var_inputs_test(self, grammar, inputStrLst, times=1):
		self.testCnt += 1
		self.printHeader(grammar, None, None, " INPUT" + " "*58)

		for desc, inputStr, shouldAccept in inputStrLst:
			statesOpen, statesAll, prunes, timeTaken, result = self.run_test_ntimes(grammar, inputStr, shouldAccept, times)
			statesStr = str(statesOpen) + ' + ' + str(statesAll-statesOpen)
			prunesStr = str(prunes).replace('[', '').replace(']', '')
			print(f'| {desc:63}| {timeTaken:9} | {statesStr:21} | {prunesStr:36} | {result:8} |')

		print(f'|{"="*150}|\n\n\n')
