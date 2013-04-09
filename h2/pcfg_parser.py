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
                if splits[2] not in self.binrules:
                    self.binrules[splits[2]] = {}
                self.binrules[splits[2]][splits[3] + " " + splits[4]] = cnt

    def trans_word_prob(self, X, wi):
        if (wi not in self.unaryrules):
            wi = "_RARE_"
        if (wi in self.unaryrules):
            if (X in self.unaryrules[wi]):
                return float(self.unaryrules[wi][X])/self.nonter[X]
        return float(0.0)

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

    def max_pi(self, pi, i, j, X):
        max_YZ = "NONE"
        for YZ in self.binrules[X]:
            q = trans_rule_prob(X, YZ)
            YZ = YZ.split()
            Y = YZ[0]
            Z = YZ[1]
            val = float(0)
            for s in range(i, j)
                Y_key = str(i) + " " + str(s) + " " + Y
                Z_key = str(s+1) + " " + str(j) + " " + Z
                val_now = q * pi[Y_key] * float(pi[Z_key])
                if (val < val_now):
                    val = val_now
                    max_YZ = YZ
        if max_YZ == "NONE" :
            print "error"
            print i, j, X
            sys.exit(1)
        return val

    def tree_prob(self):
        sent_cnt = 0
        for words in parser.sentence_itr(self.get_file(self.test_file)):
            pi = {}
            sent_cnt += 1
            n = len(words)
            if (sent_cnt >= 2):
                break
            for i in range(1, n+1):
                stri = str(i)
                for X in self.nonter:
                    key = stri + " " + stri + " " + X
                    pi[key] = self.trans_word_prob(X, words[i-1])
            for l in range(1, n)
                for i in range(1, n-l+1)
                    j = i + l
                    for X in self.nonter:
                        key = str(i) + " " + str(j) + " " + X
                        pi[key] = self.max_pi(pi, i, j, X)


if __name__ == "__main__":
    start = time.time()
    counts_file= 'parse_train.counts.out'
    test_file = 'parse_dev.dat'
    outfile = 'parse_out.dat'
    parser = PcfgParser(counts_file, test_file, outfile)
    parser.parse_counts()
    print len(parser.nonter)
    print len(parser.unaryrules)
    print len(parser.binrules)
    pi = parser.tree_prob()
    for key in pi:
        if (pi[key] > 0):
            print key, pi[key]

    print 'Elapsed time: ', time.time() - start, " seconds"
