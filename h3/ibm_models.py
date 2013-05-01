#! /usr/bin/python
# -*- coding: utf-8 -*-
__author__="Anandan Rangasmay <andy.compeer@gmail.com>"
__date__ ="$Apr 25, 2013"

"""
file_utils from pyUtils repo
"""
import sys, time, file_utils, json

class IBM_model(object):
    def __init__(self, en_corpus, es_corpus, model_number):
        self.model_no = model_number
        self.en_corpus_filename = en_corpus
        self.es_corpus_filename = es_corpus
        self.num_iterations = 5
        self.english_words = {}
        self.tfe = {}
        self.q = {}
        self.set_en_filehandle()
        self.set_es_filehandle()
        self.es_uniq_words = []
        self.es_uniq = set()
        self.es_uniq_len = 0
        self.get_lines()

    """
        Call this whenever a reset of the file handles is needed
        in order to read the file from beginning.
    """
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

    def initialize_q(self):
        start = time.time()
        k = 1
        en_lens = {}
        while k <= len(self.en_lines):
            lk = len(self.en_lines[k-1].strip().split())
            mk = len(self.es_lines[k-1].strip().split())
            k += 1
            if lk not in en_lens:
                en_lens[lk] = 1/float(lk + 1)
            """
            for i = 1..mk {where mk is the length of foreign sentence
                           at line k of parallel corpus}
            """
            q_lm = " " + str(lk) + " " + str(mk)
            for i in range(1, mk + 1):
                q_i = " " + str(i) + q_lm
                """
                for j = 0..lk {where lk is the length of english sentence}
                """
                for j in range(lk + 1):
                    """
                     q[j,i,l,m] = 1/(l+1)
                    """
                    q_index = str(j) + q_i
                    if q_index not in self.q:
                        self.q[q_index] = en_lens[lk]
        print 'Initialization of q:', "done in ", time.time() - start, ' seconds'

    def initialize_tfe(self):
        start = time.time()
        if self.model_no == 1:
            self.set_foreign_words()
            for en_word in self.english_words:
                len_en_word = len(self.english_words[en_word])
                if len_en_word == 0:
                    self.english_words[en_word] = self.es_uniq
                    len_en_word = self.es_uniq_len
                    for es_word in self.english_words[en_word]:
                        fe_index = es_word + " " + en_word
                        self.tfe[fe_index] = 1/float(len_en_word)
        if self.model_no == 2:
            """
             Initialize translation probabilities from IBM Model 1
            """
            model_file = file_utils.get_gzip("ibm_model_1.gzip")
            self.tfe = json.loads(model_file.readline())
            model_file.close()
        print 'Initialization of tfe:', "done in ", time.time() - start, ' seconds'


    """
    http://www.cs.columbia.edu/~mcollins/ibm12.pdf
    """
    def EM_algo(self):
        iteration = 1
        while iteration <= self.num_iterations:
            start = time.time()
            delta = {}
            k = 1
            counts = {}
            while k <= len(self.en_lines):
                en_words_l = self.en_lines[k-1].strip().split()
                es_words_l = self.es_lines[k-1].strip().split()
                lk = len(en_words_l)
                mk = len(es_words_l)
                """
                for i = 1..mk where mk is the length of foreign sentence
                              at line k of parallel corpus
                """
                tfe_sum = {}
                qtfe_sum = float(0.0)
                for i in range(1, mk + 1):
                    es_word = es_words_l[i-1]
                    if es_word not in tfe_sum and self.model_no == 1:
                        tfe_sum[es_word] = float(0.0)
                        for en_w in en_words_l:
                            tfe_sum[es_word] += self.tfe[es_word + " " + en_w]
                        tfe_sum[es_word] += self.tfe[es_word + " NULL"]
                    if self.model_no == 2:
                        for j in range(lk + 1):
                            q_index = str(j) + " " + str(i) + " " + str(lk) + " "+ str(mk)
                            e = "NULL"
                            if j != 0:
                                e = en_words_l[j-1]
                            qtfe_sum += self.q[q_index] * float(self.tfe[unicode(es_word + " " + e, "utf-8")])

                    """
                    for j = 0..lk where lk is the length of english sentence
                    """
                    for j in range(lk + 1):
                        index = str(k) + " " + str(i) + " " + str(j)
                        en_word = "NULL"
                        if j != 0:
                            en_word = en_words_l[j-1]
                        fe_index = es_word + " " + en_word
                        if self.model_no == 1:
                            """
                            delta[k, i, j] = {tfe[fi/ej]} /
                            {sum over all english words
                            in the sentence including null
                            against the foreign word fi(tfe_sum[fi/e])}
                            """
                            delta[index] = self.tfe[fe_index]/float(tfe_sum[es_word])
                        if self.model_no == 2:
                            fe_index = unicode(fe_index, "utf-8")
                            ilm_index = str(i) + " " + str(lk) + " "+ str(mk)
                            q_index = str(j) + " " + ilm_index
                            """
                            delta[k, i, j] = {q[j,i,l,m] * tfe[fi/ej]} /
                                                        {sum over all english words
                                                         in the sentence including null
                                                         against the foreign word fi(q[j,i,l,m]*tfe_sum[fi/e])}
                            """
                            delta[index] = float(self.q[q_index]) * float(self.tfe[fe_index])/qtfe_sum
                            if q_index in counts:
                                counts[q_index] += delta[index]
                            else:
                                counts[q_index] = delta[index]
                            if ilm_index in counts:
                                counts[ilm_index] += delta[index]
                            else:
                                counts[ilm_index] = delta[index]
                        if fe_index in counts:
                            counts[fe_index] += delta[index]
                        else:
                            counts[fe_index] = delta[index]
                        if en_word in counts:
                            counts[en_word] += delta[index]
                        else:
                            counts[en_word] = delta[index]
                if self.model_no == 2:
                    for i in range(1, mk + 1):
                        for j in range(lk + 1):
                            ilm_index = str(i) + " " + str(lk) + " "+ str(mk)
                            q_index = str(j) + " " + ilm_index
                            self.q[q_index] = counts[q_index] / float(counts[ilm_index])
                for es in es_words_l:
                    fe = es + " NULL"
                    if self.model_no == 2:
                        fe = unicode(fe, "utf-8")
                    self.tfe[fe] = counts[fe] / float(counts["NULL"])
                    for en in en_words_l:
                        fe = es + " " + en
                        if self.model_no == 2:
                            fe = unicode(fe, "utf-8")
                        self.tfe[fe] = counts[fe] / float(counts[en])
                k += 1
            print 'EM algorithm:', "iteration", iteration, "done in ", time.time() - start, ' seconds'
            iteration += 1


    def use_model(self):
        start = time.time()
        model_file = file_utils.get_gzip("ibm_model_1.gzip")
        ibm_1 = json.loads(model_file.readline())
        model_file.close()
        print 'Read from model file: ', time.time() - start, ' seconds'
        print 'Model size:', len(ibm_1)
        k = 1
        while k <= len(self.es_lines):
            es_words = self.es_lines[k-1].strip().split()
            en_words = self.en_lines[k-1].strip().split()
            f_ind = 1
            for f in es_words:
                max_tfe = 0
                max_e = "NULL"
                e_ind = 0
                max_e_ind = 0
                for e in en_words:
                    e_ind += 1
                    if max_tfe < ibm_1[unicode(f + " " + e, "utf-8")]:
                        max_tfe = ibm_1[unicode(f + " " + e, "utf-8")]
                        max_e = e
                        max_e_ind = e_ind
                #print k, max_e_ind, f_ind, f, max_e, max_tfe
                yield str(k) + " " + str(max_e_ind) + " " + str(f_ind) + "\n"
                f_ind += 1
            k += 1

    def do_EM_algo(self):
        start = time.time()
        self.initialize_tfe()
        if self.model_no == 2:
            self.initialize_q()
        if self.model_no == 1:
            print len(self.en_lines), len(self.es_lines), len(self.es_uniq_words), \
                    len(self.english_words['resumption']), len(self.es_uniq), \
                    len(self.tfe), self.tfe["reanudación resumption"], "reanudación resumption"
        print 'Initialization done: ', time.time() - start, ' seconds'
        start = time.time()
        self.EM_algo()
        print 'EM algorithm done: ', time.time() - start, ' seconds'
        start = time.time()
        if self.model_no == 1:
            file_utils.write_json_gzip(self.tfe, "ibm_model_1.gzip")
        if self.model_no == 2:
            file_utils.write_json_gzip(self.q, "ibm_model_2_q.gzip")
            file_utils.write_json_gzip(self.tfe, "ibm_model_2_tfe.gzip")
        print 'IBM Model', self.model_no, 'written to a file: ', time.time() - start, ' seconds'

if __name__ == "__main__":
    model = IBM_model("corpus.en", "corpus.es", 2)
    model.do_EM_algo()
    #model = IBM_model("test.en", "test.es", 1)
    #out_f = file_utils.get_file("alignment_test.p1.out", "w")
    #start = time.time()
    #file_utils.write_itr(model.use_model(), out_f)
    #print 'Alignments are done: ', time.time() - start, ' seconds'
