#! /usr/bin/python

__author__="Anandan Rangasmay <andy.compeer@gmail.com>"
__date__ ="$Apr 4, 2013"

import sys
import time

class PcfgParser(object):

    def __init__(self, counts_file, test_file, outfile):
        self.rare_word = unicode("_RARE_")
        self.counts_file = counts_file
        self.test_file = test_file
        self.outfile = outfile
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

    def calc_pi_bp(self, pi, bp,i, j):
        print "[i j]", [i, j]
        for s in range(i, j):
            pi_key = str(i) + " " + str(j)
            if pi_key not in pi:
                pi[pi_key] = {}
                bp[pi_key] = {}
            Y_key = str(i) + " " + str(s)
            Z_key = str(s+1) + " " + str(j)
            for Y in bp[Y_key]:
                for Z in bp[Z_key]:
                    if Y + " " + Z not in self.rev_binrules:
                        continue
                    else:
                        YZ = Y + " " + Z
                        for X in self.rev_binrules[YZ]:
                            q = self.trans_rule_prob(X, YZ)
                            pi_v = q * float(pi[Y_key][Y]) * float(pi[Z_key][Z])
                            if X not in pi[pi_key]:
                                pi[pi_key][X] = pi_v
                                bp[pi_key][X] = [X, YZ, s]
                            else:
                                if pi_v > pi[pi_key][X]:
                                    pi[pi_key][X] = pi_v
                                    bp[pi_key][X] = [X, YZ, s]

            if len(pi[pi_key]) <= 0:
                print pi[pi_key]
                print bp[pi_key]

    def tree_prob(self):
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
            cnt = 0
            for l in range(1, n):
                for i in range(1, n-l+1):
                    j = i + l
                    self.calc_pi_bp(pi, bp, i, j)
                    cnt += 1
                    if (cnt >= 2):
                        break
                break

    def tree_prob1(self):
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
    test_file = 'parse_dev_1.dat'
    outfile = 'parse_out.dat'
    parser = PcfgParser(counts_file, test_file, outfile)
    parser.parse_counts()
    print len(parser.nonter)
    print len(parser.unaryrules)
    print len(parser.binrules)
    pi = parser.tree_prob()
    print 'Elapsed time: ', time.time() - start, " seconds"
