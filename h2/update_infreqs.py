#! /usr/bin/python

__author__="Anandan Rangasmay <andy.compeer@gmail.com>"
__date__ ="$Apr 4, 2013"

import sys
import time
import json

###
### update the training data
### with __RARE__ tag for infrequent words ( < 5 count)
###

class Updater(object):
    infreq_words = {}
    rare_word = unicode("_RARE_")
    def find_infreq(self, wc_file):
        for line in open(wc_file):
            tags = line.strip().split();
            count = int(tags[0])
            word = unicode(tags[3])
            if (word in self.infreq_words):
                self.infreq_words[word] = self.infreq_words[word] + count
            else:
                self.infreq_words[word] = count
        self.infreq_words = {item:1 for item in self.infreq_words if self.infreq_words[item] < 5}

    def modify_line(self, line):
        if (len(line) == 2):
            if (line[1] in self.infreq_words):
                return [line[0], self.rare_word]
            else:
                return line
        line[1] = self.modify_line(line[1])
        line[2] = self.modify_line(line[2])
        return line

    def modify_train_itr(self, train_file):
        for line in open(train_file):
            l = json.loads(line);
            yield json.dumps(self.modify_line(l));

    def write_output(self, train_file, new_train_file):
        ntf_handle = open(new_train_file, 'w')
        for line in self.modify_train_itr(train_file):
            ntf_handle.write(line + "\n")

start = time.time()
wc_file = 'cfg.unary.counts'
train_file = 'parse_train.dat'
new_train_file = 'parse_train_new_1.dat'
updater = Updater()
updater.find_infreq(wc_file)
updater.write_output(train_file, new_train_file)
print 'Elapsed time: ', time.time() - start, " seconds"
