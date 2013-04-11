#! /usr/bin/python

__author__="Anandan Rangasmay <andy.compeer@gmail.com>"
__date__ ="$Apr 4, 2013"

import sys
import time
import json

class PcfgParser(object):

    def __init__(self, counts_file, test_file, outfile):
        self.rare_word = unicode("_RARE_")
        self.counts_file = counts_file
        self.test_file = test_file
        self.outfile = self.get_file(outfile, "w")
        self.nonter = {}
        self.unaryrules = {}
        self.binrules = {}
        self.rev_binrules = {}
        self.wordprobs = {}
        self.ruleprobs = {}

    def get_file(self, filename, mode='r'):
        try:
            file_handle = open(filename, mode)
        except IOError as e:
            sys.stderr.write("ERROR: Cannot read input test file: %s.\nError msg: %s.\n" % (filename, e.strerror))
            raise
        return file_handle

    def parse_counts(self):
        for line in self.get_file(self.counts_file):
            splits = line.strip().split()
            cnt = int(splits[0])
            if (splits[1] == 'NONTERMINAL'):
                self.nonter[splits[2]] = cnt
            if (splits[1] == 'UNARYRULE'):
                if splits[3] not in self.unaryrules:
                    self.unaryrules[splits[3]] = {}
                self.unaryrules[splits[3]][splits[2]] = cnt
            if (splits[1] == 'BINARYRULE'):
                X = splits[2]
                YZ = splits[3] + " " + splits[4]
                if YZ not in self.rev_binrules:
                    self.rev_binrules[YZ] = {}
                self.rev_binrules[YZ][X] = cnt
                if X not in self.binrules:
                    self.binrules[X] = {}
                self.binrules[X][YZ] = cnt

    def trans_word_prob(self, X, wi):
        if (wi not in self.unaryrules):
            wi = "_RARE_"
        key = X + " " + wi
        if key in self.wordprobs:
            return self.wordprobs[key]
        wordprob = float(0.0)
        if (X in self.unaryrules[wi]):
            wordprob = float(self.unaryrules[wi][X])/self.nonter[X]
        self.wordprobs[key] = wordprob
        return wordprob

    def trans_rule_prob(self, X, YZ):
        if (X in self.binrules):
            if (YZ in self.binrules[X]):
                return float(self.binrules[X][YZ])/self.nonter[X]
        return float(0.0)

    def sentence_itr(self, file_handle):
        words = []
        for l in file_handle:
            words = l.strip().split()
            if len(words) > 0:
                yield words

    def max_pi(self, bp, pi, i, j, X):
        max_YZ = "NONE"
        for YZ in self.binrules[X]:
            q = self.trans_rule_prob(X, YZ)
            YZ = YZ.split()
            Y = YZ[0]
            Z = YZ[1]
            val = float(0)
            if (max_YZ == "NONE"):
                max_YZ = YZ
            for s in range(i, j):
                Y_key = str(i) + " " + str(s) + " " + Y
                Z_key = str(s+1) + " " + str(j) + " " + Z
                if Y_key not in pi:
                    pi[Y_key] = 0.0
                if Z_key not in pi:
                    pi[Z_key] = 0.0
                try:
                    val_now = q * pi[Y_key] * float(pi[Z_key])
                except TypeError as e:
                    print e
                    print pi[Z_key]
                    print Z_key
                    raise
                if (val < val_now):
                    val = val_now
                    max_YZ = YZ
        if max_YZ == "NONE" :
            print "Error"
            print i, j, X
            sys.exit(1)

        if isinstance(val, str):
            print "Error:", val, "is a string instead of float"
        return val, max_YZ

    def calc_pi_bp(self, i, j):
        pi_key = str(i) + " " + str(j)
        for s in range(i, j):
            if pi_key not in self.pi:
                self.pi[pi_key] = {}
                self.bp[pi_key] = {}
            Y_key = str(i) + " " + str(s)
            Z_key = str(s+1) + " " + str(j)
            if Y_key not in self.bp or Z_key not in self.bp:
                continue
            for Y in self.bp[Y_key]:
                for Z in self.bp[Z_key]:
                    if Y + " " + Z not in self.rev_binrules:
                        continue
                    else:
                        YZ = Y + " " + Z
                        for X in self.rev_binrules[YZ]:
                            q = self.trans_rule_prob(X, YZ)
                            pi_v = q * float(self.pi[Y_key][Y]) * float(self.pi[Z_key][Z])
                            if X not in self.pi[pi_key]:
                                self.pi[pi_key][X] = pi_v
                                self.bp[pi_key][X] = [X, YZ, s]
                            else:
                                if pi_v > self.pi[pi_key][X]:
                                    self.pi[pi_key][X] = pi_v
                                    self.bp[pi_key][X] = [X, YZ, s]
            if len(self.pi[pi_key]) == 0:
                del self.pi[pi_key]
                del self.bp[pi_key]

    def get_max_X(self, sent_len):
        max_pi_v = 0.0
        max_X = "NONE"
        pi_key = "1 " + str(sent_len)
        error = 0
        if pi_key in self.pi:
            for key in self.pi[pi_key]:
                if self.pi[pi_key][key] > max_pi_v:
                    max_pi_v = self.pi[pi_key][key]
                    max_X = key
            if max_X == "NONE":
                error = 1
        else:
            error = 1
        if error == 1:
            print "ERROR: pi[1 sent_length X] value not found for sentence: %s" %self.sentence
            sys.exit(1)
        return max_X


    def efficient_CKY_algo(self):
        sent_cnt = 0
        for words in parser.sentence_itr(self.get_file(self.test_file)):
            self.sentence = words
            self.pi = {}
            self.bp = {}
            sent_cnt += 1
            n = len(words)
            for i in range(1, n+1):
                stri = str(i)
                word = words[i-1]
                if word not in self.unaryrules:
                    word = "_RARE_"
                for X in self.unaryrules[word]:
                    key = stri + " " + stri;
                    if key not in self.pi:
                        self.pi[key] = {}
                        self.bp[key] = {}
                    self.pi[key][X] = self.trans_word_prob(X, word)
                    self.bp[key][X] = [X, word, i]
            for l in range(1, n):
                for i in range(1, n-l+1):
                    j = i + l
                    self.calc_pi_bp(i, j)
            max_X = "NONE"
            if self.sentence[n-1] == "?":
                max_X = "SBARQ"
            else:
                max_X = self.get_max_X(n)
            yield json.dumps(self.backtrack(1, n, max_X))

    def backtrack(self, i, j, max_X):
        result = []
        result.append(max_X)
        num_key = str(i) + " " + str(j)
        s = self.bp[num_key][max_X][2]
        YZ = self.bp[num_key][max_X][1].split()
        if len(YZ) == 2:
            result.append(self.backtrack(i, s, YZ[0]))
            result.append(self.backtrack(s+1, j, YZ[1]))
        if len(YZ) == 1:
            result.append(self.sentence[i-1])
        return result

    def write_output(self):
        for line in self.efficient_CKY_algo():
            self.outfile.write(line + "\n")

    def CKY_algo(self):
        sent_cnt = 0
        for words in parser.sentence_itr(self.get_file(self.test_file)):
            print words
            pi = {}
            bp = {}
            sent_cnt += 1
            n = len(words)
            if (sent_cnt >= 2):
                break
            for i in range(1, n+1):
                stri = str(i)
                word = words[i-1]
                if word not in self.unaryrules:
                    word = "_RARE_"
                for X in self.unaryrules[word]:
                    key = stri + " " + stri;
                    if key not in pi:
                        pi[key] = {}
                        bp[key] = {}
                    pi[key][X] = self.trans_word_prob(X, word)
                    bp[key][X] = [X, word, i]
            for key in pi:
                print key, "; pi =", pi[key], "; bp = ", bp[key]
            continue
            for l in range(1, n):
                for i in range(1, n-l+1):
                    j = i + l
                    for X in self.binrules:
                        key = str(i) + " " + str(j) + " " + X
                        pi_bp = self.max_pi(bp, pi, i, j, X)
                        pi[key] = pi_bp[0]
                        bp[key] = pi_bp[1]



if __name__ == "__main__":
    start = time.time()
    counts_file= 'parse_train.counts.out'
    test_file = 'parse_test.dat'
    outfile = 'parse_test.p2.out'
    parser = PcfgParser(counts_file, test_file, outfile)
    parser.parse_counts()
    print len(parser.nonter)
    print len(parser.unaryrules)
    print len(parser.binrules)
    parser.write_output()
    print 'Elapsed time: ', time.time() - start, " seconds"
