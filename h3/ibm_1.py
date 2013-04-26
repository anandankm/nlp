#! /usr/bin/python
# -*- coding: utf-8 -*-
__author__="Anandan Rangasmay <andy.compeer@gmail.com>"
__date__ ="$Apr 25, 2013"

# file_utils from pyUtils repo
import sys, time, file_utils

class IBM_model1(object):
    def __init__(self, en_corpus, es_corpus):
        self.en_corpus_filename = en_corpus
        self.es_corpus_filename = es_corpus
        self.english_words = {}
        self.set_en_filehandle()
        self.set_es_filehandle()
        self.es_uniq_words = []
        self.es_uniq = set()
        self.es_uniq_len = 0
        self.get_lines()

    ## Call this whenever a reset of the file handles is needed
    ## in order to read the file from beginning.
    def set_en_filehandle(self):
        self.en_corpus_file = file_utils.get_file(self.en_corpus_filename, "r")

    def set_es_filehandle(self):
        self.es_corpus_file = file_utils.get_file(self.es_corpus_filename, "r")

    def get_lines(self):
        self.en_lines = list(self.en_corpus_file)
        self.es_lines = list(self.es_corpus_file)
        for es_line in self.es_lines:
            line_set = set(es_line.strip().split())
            self.es_uniq_words.append(line_set)
            self.es_uniq.update(line_set)
        self.es_uniq_len = len(self.es_uniq)

    def set_foreign_words(self):
        k = 1
        self.english_words["NULL"] = self.es_uniq
        while k <= len(self.en_lines):
            en_words_l = self.en_lines[k-1].strip().split()
            for en_word in en_words_l:
                if en_word in self.english_words:
                    self.english_words[en_word].update(self.es_uniq_words[k-1])
                else:
                    self.english_words[en_word] = set(self.es_uniq_words[k-1])
            k += 1


if __name__ == "__main__":
    start = time.time()
    model = IBM_model1("corpus.en", "corpus.es")
    model.set_foreign_words()
    print len(model.en_lines), len(model.es_lines), len(model.es_uniq_words), \
            len(model.english_words)
    print 'Elapsed time: ', time.time() - start, " seconds"
