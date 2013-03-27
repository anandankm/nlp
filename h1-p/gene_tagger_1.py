#! /usr/bin/python

__author__="Anandan Rangasmay <andy.compeer@gmail.com>"
__date__ ="$Mar 24, 2013"

import sys
import time
import math
from collections import defaultdict

## * - 0
## * - 1
## O - 2
## I-GENE - 3
## STOP - 4
##

class HmmTagger(object):

    def __init__(self, tag_counts_file, ngrams_file, tf_handle, outfile):
        self.tag_counts_file = tag_counts_file
        self.ngrams_file = ngrams_file
        self.test_file = tf_handle
        self.outfile = open(outfile, 'w')
        self.tag_counts = defaultdict(list)
        self.ngram_counts = defaultdict(int)
        self.unseen_words = 0
        self.probs_cnt = 0
        self.rare_tag = "NONE"

    def parse_counts(self):
        for line in open(self.ngrams_file):
            ngram_v = line.strip().split(' ', 2)
            self.ngram_counts[ngram_v[2]] = int(ngram_v[0])
        for line in open(self.tag_counts_file):
            tag_v = line.strip().split()
            self.tag_counts[tag_v[3]].append([tag_v[2], int(tag_v[0])])

    def write_output(self):
        for l in self.emission_iterator():
            self.outfile.write(' '.join(l) + "\n")

    def calc_probs(self, tag_values):
        self.probs_cnt += 1
        emit_prob = 0
        emit_tag = "NONE"
        for tag_value in tag_values:
            val = float(tag_value[1])/self.ngram_counts[tag_value[0]]
            if (val > emit_prob):
                emit_prob = val
                emit_tag = tag_value[0]
        return emit_tag

    def emission_iterator(self):
        l = self.test_file.readline()
        while l:
            line = l.strip()
            if line:
                if (line not in self.tag_counts):
                    self.unseen_words += 1
                    if (self.rare_tag == "NONE"):
                        self.rare_tag = self.calc_probs(self.tag_counts["_RARE_"])
                    yield line, self.rare_tag
                if (line in self.tag_counts):
                    tag_values = self.tag_counts[line]
                    if len(tag_values) == 1:
                        yield line, tag_values[0][0]
                    else:
                        yield line, self.calc_probs(tag_values)
            else: # Empty line
                yield line
            l = self.test_file.readline()


if __name__ == '__main__':

    start = time.time()
    test_file = 'gene.test'
    try:
        tf_handle = file(test_file, 'r')
    except IOError:
        sys.stderr.write("ERROR: Cannot read input test file: %s.\n" % test_file)
    tagger =  HmmTagger('gene.p1.tags','gene.p1.ngrams',tf_handle, 'gene_test.p1.out')
    tagger.parse_counts()
    print 'ngram count: ', len(tagger.ngram_counts)
    print 'tags count: ', len(tagger.tag_counts)
    tagger.write_output()
    print 'unseen words: ', tagger.unseen_words
    print 'Elapsed time: ', time.time() - start, " seconds"

