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
        self.tfe = {}
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

    def initialize_tfe(self):
        for en_word in self.english_words:
            len_en_word = len(self.english_words[en_word])
            if len_en_word == 0:
                self.english_words[en_word] = self.es_uniq
                len_en_word = self.es_uniq_len
            for es_word in self.english_words[en_word]:
                self.tfe[es_word + " " + en_word] = 1/float(len_en_word)

    # http://www.cs.columbia.edu/~mcollins/ibm12.pdf
    def EM_algo(self):
        delta = {}
        k = 1
        counts = {}
        while k <= len(self.en_lines):
            en_words_l = self.en_lines[k-1].strip().split()
            es_words_l = self.es_lines[k-1].strip().split()
            # for i = 1..mk where mk is the length of foreign sentence
            #               at line k of parallel corpus
            tfe_sum = {}
            for i in range(1, len(es_words_l) + 1):
                es_word = es_words_l[i-1]
                if es_word not in tfe_sum:
                    tfe_sum[es_word] = float(0.0)
                    for en_w in en_words_l:
                        tfe_sum[es_word] += self.tfe[es_word + " " + en_w]
                    tfe_sum[es_word] += self.tfe[es_word + " NULL"]
                # for j = 1..lk where lk is the length of english sentence
                for j in range(len(en_words_l) + 1):
                    index = str(k) + " " + str(i) + " " + str(j)
                    en_word = "NULL"
                    if j != 0:
                        en_word = en_words_l[j-1]
                    # delta[k, i, j] = {tfe[fi/ej]} / {sum over all english words
                    #                                  in the sentence including null
                    #                                  against the foreign word fi(tfe_sum[fi/e])}
                    fe_index = es_word + " " + en_word
                    delta[index] = self.tfe[fe_index]/float(tfe_sum[es_word])
                    if fe_index in counts:
                        counts[fe_index] += delta[index]
                    if en_word in counts:
                        counts[en_word] += delta[index]


if __name__ == "__main__":
    start = time.time()
    model = IBM_model1("corpus.en", "corpus.es")
    model.set_foreign_words()
    model.initialize_tfe()
    print len(model.en_lines), len(model.es_lines), len(model.es_uniq_words), \
            len(model.english_words['resumption']), len(model.es_uniq), \
            len(model.tfe), model.tfe["reanudación NULL"]
    file_utils.write_output(model.english_words['resumption'], "resumption_foreign_py")
    print 'Elapsed time: ', time.time() - start, " seconds"
