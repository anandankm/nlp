#! /usr/bin/python

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

if __name__ == "__main__":
    start = time.time()
    model = IBM_model1("corpus.en", "corpus.es")
    print len(model.en_lines), len(model.es_lines)
    print 'Elapsed time: ', time.time() - start, " seconds"