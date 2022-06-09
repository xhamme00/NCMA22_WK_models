# Author: Jan Hammer, xhamme00@stud.fit.vutbr.cz
# Project: WK Grammar Tree Search
# Runs a test of tree search the grammars with some hand picked values that might be considered edge case inputs

from lib.perf_tester import cPerfTester
from lib.grammars import *

def main():
	tester = cPerfTester()

	# grammar 5 #####################################
	inputs = [
		('1000c tg'     , 'c' * 1000 + 'tg'        , True),
		('ct 1000g'     , 'ct' + 1000*'g'          , True),
		('500c t 500g'  , 500*'c' + 't' + 500*'g'  , True),
		('500a ctg 500a', 500*'a' + 'ctg' + 500*'a', True)
	]

	tester.var_inputs_test(g5, inputs, True)

	# grammar 6 #####################################
	inputs = [
		('500a'  , 'a'*500          , False),
		('500b'  , 'b'*500          , False),
		('a 500b', 'a' + 'b'*500    , False),
		('500a b', 'a'*500 + 'b'*499, False)
	]
	tester.var_inputs_test(g6, inputs)

	# grammar 7 #####################################
	inputs = [
		('1000a'       , 'a'*1000                 , False),
		('c 1000a'     , 'c' + 'a'*1000           , False),
		('1000a c 999a', 1000 *'a' + 'c' + 'a'*999, False),
		('1000a c'     , 'a'*1000 + 'c'           , False),
		('1000a c 100a', 'a'*1000 + 'c' + 100*'a' , False)
	]
	tester.var_inputs_test(g7, inputs)

	# grammar 8 #####################################
	inputs = [
		('2000ab 2000ba a', 'ab'*2000 + 'ba'*2000 + 'a', False),
		('a 2000ab 2000ba', 'a' + 'ab'*2000 + 'ba'*2000, False),
		('2000ab a 2000ba', 'ab'*1000 + 'a' + 'ba'*1000, False)
	]

	tester.var_inputs_test(g8, inputs)

	# grammar 9 #####################################
	inputs = [
		('100x"0" 2 100x"1"', 100 * '0' + '2' + 100 * '1', False),
		('2 200x"1"'        , '2' + 200 * '1'            , True),
		('0 2 200x"1"'      , '0' + '2' + 200 * '1'      , True),
		('200x"1" 2'        , 200 * '1' + '2'            , True),
		('200x"1" 2 1'      , 200 * '1' + '21'           , True),
		('100x"1" 100x"0"'  , 100*'1' + 100*'0'          , False)
	]

	tester.var_inputs_test(g9, inputs)

	# grammar 10 ####################################
	s1 = '(0+1)*(01)*0*+(111)*0011+0*+1*+(0+1)*'
	s2 = 20*'(' + '(0+1)*' + 20*')*'
	s3 = '0+'*40 + '1'
	replace_chars = lambda s: s.replace('(', 'o').replace(')', 'c').replace('+', 'p').replace('*', 's')

	inputs = [
		(f's1+s1 while s1={s1}'  , replace_chars(s1 + '+' + s1)           , True),
		('(((...(((0.1)*)*...)*)', replace_chars(s2)                      , True),
		('0+0+...0+0+1'          , replace_chars(s3)                      , True),
		('+0+0+...0+0+1'         , replace_chars('+'+s3)                  , False),
		('0+0+...0+0+1+'         , replace_chars(s3+'+')                  , False),
		('0+0+...0++0+...0+0+1'  ,  replace_chars(s3[:40] + '+' + s3[40:]), False)
	]
	tester.var_inputs_test(g10, inputs)

	# grammar 11 ####################################
	inputs = [
		('50a b 50a b', 50*'a' + 'b' + 50*'a' + 'b', False),
		('a 50b a 50b', 'a' + 50*'b' + 'a' + 50*'b', False),
		('50a b 50a'  , 50*'a' + 'b' + 50*'a'      , True),
		('50b a 50b'  , 50*'b' + 'a' + 50*'b'      , True),
		('a 100bb'    , 'a' + 100*'b'              , True),
		('100b a'     , 100*'b' + 'a'              , True)
	]
	tester.var_inputs_test(g11, inputs)

	# grammar 12 ####################################
	inputs = [
		('500r 500d 500u 500r d', 500*'r' + 500*'d' + 500*'u' + 500*'r' + 'd', False),
		('d 500r 500d 500u 500r', 'd' + 500*'r' + 500*'d' + 500*'u' + 500*'r', False),
		('500r 500d 500u 501r'  ,500*'r' + 500*'d' + 500*'u' + 501*'r'       , False),
		('500r 500d 501u 500r'  , 500*'r' + 500*'d' + 501*'u' + 500*'r'      , False),
		('500r 501d 500u 500r'  , 500*'r' + 501*'d' + 500*'u' + 500*'r'      , False),
		('501r 500d 500u 500r'  , 501*'r' + 500*'d' + 500*'u' + 500*'r'      , False),
		('r 500d 500u 500r'     , 'r' + 500*'d' + 500*'u' + 500*'r'          , False),
		('500r d 500u 500r'     , 500*'r' + 'd' + 500*'u' + 500*'r'          , False),
		('500r 500d u 500r'     , 500*'r' + 500*'d' + 'u' + 500*'r'          , False),
		('500r 500d 500u r'     , 500*'r' + 500*'d' + 500*'u' + 'r'          , False)
	]

	tester.var_inputs_test(g12, inputs)

	# grammar 13 ####################################
	inputs = [
		('501a 500c 500b'  , 501*'a' + 500*'c' + 500*'b'      , False),
		('500a 501c 500b'  , 500*'a' + 501*'c' + 500*'b'      , False),
		('500a 500c 501b'  , 500*'a' + 500*'c' + 501*'b'      , False),
		('a 500c 500b'     , 'a' + 500*'c' + 500*'b'          , False),
		('500a c 500b'     , 500*'a' + 'c' + 500*'b'          , False),
		('500a 500c b'     , 500*'a' + 500*'c' + 'b'          , False),
		('c 500a 500c 500b', 'c' + 500*'a' + 500*'c' + 500*'b', False),
		('500a 500c 500b a', 500*'a' + 500*'c' + 500*'b' + 'a', False)
	]

	tester.var_inputs_test(g13, inputs)

	# grammar 14 ####################################
	inputs = [
		('200a b 200c d'        , 'a'*200 + 'b' + 'c'*200 + 'd'              , True),
		('a 200b c 200d'        , 'a' + 'b'*200 + 'c' + 'd'*200              , True),
		('100a 100b 100c 100d'  , 'a'*100 + 'b'*100 + 'c'*100 + 'd'*100      , True),
		('100b 100c 100d'       , 100*'b' + 100*'c' + 100*'d'                , False),
		('100a 100b 100c'       , 100*'a' + 100*'b' + 100*'c'                , False),
		('100a 100b 100c 100d a', 100*'a' + 100*'b' + 100*'c' + 100*'d' + 'a', False)
	]

	tester.var_inputs_test(g14, inputs)

	# grammar 15 ####################################
	inputs = [
		('400a'       , 'a'*400                , False),
		('400a c'     , 'a'*400 + 'c'          , False),
		('400a c 399a', 'a'*400 + 'c' + 399*'a', False),
		('c 16a'      , 'c' + 'a'*100,           False),        # g15.remove_lambda_rules() helps a lot
	]

	tester.var_inputs_test(g15, inputs)

	# grammar 16 ####################################
	inputs = [
		('50a 100b 50a', 50*'a' + 100*'b' + 50*'a', True),
		('50a 150b 50a', 50*'a' + 150*'b' + 50*'a', True),
		('50a 99b 50a' , 50*'a' + 99*'b' + 50*'a' , False),
		('50a 151b 50a', 50*'a' + 151*'b' + 50*'a', False),
		('50a 150b 51a', 50*'a' + 150*'b' + 51*'a', False),
		('51a 150b 50a', 51*'a' + 150*'b' + 50*'a', False)
	]

	tester.var_inputs_test(g16, inputs)

	# grammar 17 ####################################
	inputs = [
		('100a 100b'   , 100*'a' + 100*'b'       , True),
		('100ab'       , 100*'ab'                , True),
		('100a 101b a' , 100*'a' + 101*'b' + 'a' , False),
		('b 100a 99b'  , 'b' + 100*'a' + 99*'b'  , False),
		('100ab ba'    , 100*'ab' + 'ba'         , False),
		('50ab ba 50ab', 50*'ab' + 'ba' + 50*'ab', False)
	]

	tester.var_inputs_test(g17, inputs)

	# grammar 18 ####################################
	inputs = [
		('100l 100r'                    , 100*'l' + 100*'r'                                 , True),
		('100 lr'                       , 100*'lr'                                          , True),
		('14l 14r 13l 13r ... 2l 2r l r', ''.join(['l'*i + 'r'*i for i in range(14, 0, -1)]), True),
		('100l 100r rl'                 , 100*'l' + 100*'r' + 'rl'                          , False),
		('rl 100l 100r'                 , 'rl' + 100*'l' + 100*'r' + 'rl'                   , False),
		('50l 50r rl 50l 50r'           , 50*'l' + 50*'r' + 'rl' + 50*'l' + 50*'r'          , False)
	]

	tester.var_inputs_test(g18, inputs)

	# grammar 19 ####################################
	inputs = [
		('50a 50c 51b'     , 50*'a' + 50*'c' + 51*'b'         , False),
		('101a 100c 100b'  , 101*'a' + 100*'c' + 100*'b'      , False),
		('150a 1c 150b'    , 150*'a' + 1*'c' + 150*'b'        , True),
		('100a 100c 100b'  , 100*'a' + 100*'c' + 100*'b'      , True),
		('c 100a 100c 100b', 'c' + 100*'a' + 100*'c' + 100*'b', False),
		('100a 100c 100b c', 100*'a' + 100*'c' + 100*'b' + 'c', False)
	]

	tester.var_inputs_test(g19, inputs)

	# grammar 20 ####################################
	inputs = [
		('100a b 100c d'  , 100*'a' + 'b' + 100*'c' + 'd'      , True),
		('a 100b c 100d'  , 'a' + 100*'b' + 'c' + 100*'d'      , True),
		('100a b c 100d'  , 100*'a' + 'bc' + 100*'d'           , True),
		('a 100b 100c d'  , 'a' + 100*'b' + 100*'c' + 'd'      , True),
		('50a 50b 50c 50d', 50*'a' + 50*'b' + 50* 'c' + 50*'d' , True),
		('100a b 101c d'  , 100*'a' + 'b' + 101*'c' + 'd'      , False),
		('a 100b 100c 2d' , 'a' + 100*'b' + 100*'c' + 2*'d'    , False),
		('50a 50b 50c 51d', 50 * 'a' + 50*'b' + 50*'c' + 51*'d', False),
		('51a 50b 50c 50d', 51*'a' + 50*'b' + 50*'c' + 50*'d'  , False)
	]

	tester.var_inputs_test(g20, inputs)

if __name__ == "__main__":
	main()
