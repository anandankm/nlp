#! /usr/bin/python

__author__="Anandan Rangasmay <andy.compeer@gmail.com>"
__date__ ="$Mar 24, 2013"

import sys
import time
import re

###
### update the training data
### with __RARE__ tag for infrequent words ( < 5 count)
###

class Updater(object):
    infreq_words = {}
    one_num_regex = re.compile("[0-9]")
    all_caps_regex = re.compile("^[A-Z]+$")
    caps_at_end = re.compile("[A-Z]$")
    def find_infreq(self, wc_file):
        for line in open(wc_file):
            tags = line.strip().split();
            if (int(tags[0]) < 5):
                self.infreq_words[tags[3] + " " + tags[2]] = 1

    def modify_train_itr(self, train_file):
        for line in open(train_file):
            word = line.strip().split();
            if (word and line.strip() in self.infreq_words):
                if self.one_num_regex.search(word[0]):
                    rare_class = '_NUM_'
                elif self.all_caps_regex.search(word[0]):
                    rare_class = '_ALL_CAPS_'
                elif self.caps_at_end.search(word[0]): 
                    rare_class = '_CAPS_AT_END_'
                else:
                    rare_class = '_RARE_'
                yield rare_class, word[1]
            else:
                yield word

    def write_output(self, train_file, new_train_file):
        ntf_handle = open(new_train_file, 'w')
        for line in self.modify_train_itr(train_file):
            ntf_handle.write(' '.join(line) + "\n")



start = time.time()
wc_file = 'gene.tag.counts'
train_file = 'gene.train'
new_train_file = 'gene.p1.train'
updater = Updater()
updater.find_infreq(wc_file)
updater.write_output(train_file, new_train_file)
print 'Elapsed time: ', time.time() - start, " seconds"
