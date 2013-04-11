#! /usr/bin/python

__author__="Anandan Rangasmay <andy.compeer@gmail.com>"
__date__ ="$Mar 24, 2013"

import sys
import time
import math
import re
from collections import defaultdict
from decimal import *

## * - 0
## * - 1
## O - 2
## I-GENE - 3
## STOP - 4
##

class HmmTagger(object):

    def __init__(self, tag_counts_file, ngrams_file, test_filename, outfile):
        self.tag_counts_file = tag_counts_file
        self.ngrams_file = ngrams_file
        self.test_filename = test_filename
        self.outfile = outfile
        self.tag_counts = {}
        self.ngram_counts = defaultdict(int)
        self.unseen_words = 0
        self.probs_cnt = 0
        self.rare_tag = "NONE"
        self.lambda1 = Decimal(1)/Decimal(3);
        self.lambda2 = Decimal(1)/Decimal(3);
        self.lambda3 = Decimal(1)/Decimal(3);
        self.transition_probs = defaultdict(Decimal)
        self.tags = ["O", "I-GENE"]
        self.out_handle = self.get_file(self.outfile, "w")
        self.one_num_regex = re.compile("[0-9]")
        self.all_caps_regex = re.compile("^[A-Z]+$")
        self.caps_at_end = re.compile("[A-Z]$")
        self.all_cnt = 0

    def get_file(self, filename, mode='r'):
        try:
            file_handle = open(filename, mode)
        except IOError as e:
            sys.stderr.write("ERROR: Cannot read input test file: %s.\nError msg: %s.\n" % (filename, e.strerror))
        return file_handle

    def parse_counts(self):
        for line in self.get_file(self.ngrams_file):
            ngram_v = line.strip().split(' ', 2)
            self.ngram_counts[ngram_v[2]] = int(ngram_v[0])
        for line in self.get_file(self.tag_counts_file):
            tag_v = line.strip().split()
            if tag_v[3] not in self.tag_counts:
                self.tag_counts[tag_v[3]] = {}
            self.tag_counts[tag_v[3]][tag_v[2]] = int(tag_v[0])

        self.ngram_counts["STOP"] = self.ngram_counts["* *"]
        self.ngram_counts["*"] = 2 * self.ngram_counts["* *"]
        self.ngram_counts["TOTAL"] = self.ngram_counts["I-GENE"] + self.ngram_counts["O"] + self.ngram_counts["STOP"]

    def emission_prob(self, word, tag):
        if tag not in self.tag_counts[word]:
            return Decimal(0.0)
        return Decimal( \
                self.tag_counts[word][tag] \
                ) / Decimal(self.ngram_counts[tag])

    def sentence_itr(self, file_handle):
        sentence = []
        l = file_handle.readline()
        while l:
            line = l.strip()
            if line:
                sentence.append(line)
            else:
                yield sentence
                sentence = []
            l = file_handle.readline()

    def transition_prob(self, yi):
        if yi in self.transition_probs:
            return self.transition_probs[yi]
        y = yi.split();
        q = self.lambda1 * (Decimal(self.ngram_counts[y[0] + " " + y[1] + " " + y[2]]) \
                            /Decimal(self.ngram_counts[y[0] + " " + y[1]])) + \
            self.lambda2 * (Decimal(self.ngram_counts[y[1] + " " + y[2]]) \
                            /Decimal(self.ngram_counts[y[1]])) + \
            self.lambda3 * (Decimal(self.ngram_counts[y[2]]) \
                            /Decimal(self.ngram_counts["TOTAL"]))
        return q

    def find_rare_class(self, word):
        if self.one_num_regex.search(word):
            return '_NUM_'
        elif self.all_caps_regex.search(word):
            return '_ALL_CAPS_'
        elif self.caps_at_end.search(word):
            return '_CAPS_AT_END_'
        else:
            return '_RARE_'

    def calc_tags(self, sentence):
        sentence_tags = []
        pi_sent = defaultdict(Decimal)
        pi_sent["0 * *"] = Decimal(1.0);
        bp = {}
        avail = ["O", "I-GENE"]
        for i in range(len(sentence)):
            x = sentence[i]
            k = i + 1
            if x not in self.tag_counts:
                x = self.find_rare_class(x)
            if x == "_ALL_CAPS_":
                self.all_cnt += 1
            max_tag = "NONE"
            tags = self.tag_counts[x]
            u_tags = w_tags = avail
            if k == 1:
                u_tags = ["*"]
            if k == 2 or k == 1:
                w_tags = ["*"]
            for u in u_tags:
                for v in tags:
                    emit_prob = self.emission_prob(x, v)
                    pi = Decimal(0.0)
                    for w in w_tags:
                        trans_prob = self.transition_prob(w + " " + u + " " + v)
                        index = str(k - 1) + " " + w + " " + u
                        if index in pi_sent:
                            pi_now = Decimal(pi_sent[index]) * trans_prob * emit_prob
                            if pi_now > pi:
                                pi = pi_now
                                max_tag = w
                    index = str(k) + " " + u + " " + v
                    bp[index] = max_tag
                    pi_sent[index] = pi
        sent_len = len(sentence)
        pi = Decimal(0.0)
        yn1 = "NONE"
        yn = "NONE"
        for u in avail:
            for v in avail:
                index = str(sent_len) + " " + u + " " + v
                if index in pi_sent:
                    pi_now = Decimal(pi_sent[index]) * Decimal(self.transition_prob(u + " " + v + " " + "STOP"))
                    if pi_now > pi:
                        pi = pi_now
                        yn1 = u
                        yn = v
        if yn == "NONE" or yn1 == "NONE":
            print "error"
            print len(sentence)
            sys.exit(1)
        sentence_tags.insert(0,yn)
        sentence_tags.insert(0,yn1)
        for k in reversed(range(3, sent_len + 1)):
            index = str(k) + " " + sentence_tags[0] + " " + sentence_tags[1]
            sentence_tags.insert(0, bp[index])
        for (word, tag) in zip(sentence, sentence_tags):
            self.out_handle.write(word + " " + tag + "\n")

    def parse_sentences(self):
        fh = self.get_file(self.test_filename, 'r')
        cnt = 0
        for sentence in tagger.sentence_itr(fh):
            cnt += 1
            self.calc_tags(sentence)
            self.out_handle.write("\n")

if __name__ == '__main__':

    start = time.time()
    tags_file = 'gene.p1.tags'
    ngrams_file = 'gene.p1.ngrams'
    outfile = 'gene_test.p3.out'
    test_file = 'gene.test'
    tagger =  HmmTagger(tags_file, ngrams_file, test_file, outfile)
    tagger.parse_counts()
    print 'ngram count: ', len(tagger.ngram_counts)
    print 'tags count: ', len(tagger.tag_counts)
    tagger.parse_sentences()
    print 'All caps count: ', tagger.all_cnt;
    print 'Elapsed time: ', time.time() - start, " seconds"

