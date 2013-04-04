#! /usr/bin/python

__author__="Anandan Rangasmay <andy.compeer@gmail.com>"
__date__ ="$Mar 24, 2013"

import sys
import time

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
            if (int(tags[0]) < 5):
                self.infreq_words[unicode(tags[2] + " " + tags[3])] = 1

    def modify_line(self, line):
        if (len(line) == 2):
            if (" ".join(line)) in self.infreq_words):
                return [line[0], rare_word]
        line[1] = self.modify_line(line[1])
        line[2] = self.modify_line(line[2])
        return line

    def modify_train_itr(self, train_file):
        for line in open(train_file):
            l = json.loads(line);
            yield json.dumps(modify_line(l));

    def write_output(self, train_file, new_train_file):
        ntf_handle = open(new_train_file, 'w')
        for line in self.modify_train_itr(train_file):
            ntf_handle.write(line + "\n")



start = time.time()
wc_file = 'cfg.unary.counts'
train_file = 'parse_train.dat'
new_train_file = 'parse_train_new.dat'
updater = Updater()
updater.find_infreq(wc_file)
print len(updater.infreq_words)
#updater.write_output(train_file, new_train_file)
print 'Elapsed time: ', time.time() - start, " seconds"
