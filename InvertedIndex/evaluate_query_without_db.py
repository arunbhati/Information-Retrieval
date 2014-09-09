import pickle
import sys
import math
import linecache as lc
import struct


log = math.log
getline = lc.getline
TF = 0
TFIDF = 1
BM25 = 2
N = 1600000

class plentry:
    def __init__(self, doc_id, positions):
        self.doc_id       = doc_id
        self.positions    = positions

class score_entry:
    def __init__(self, doc_id , score):
        self.doc_id = doc_id
        self.score  = score

class query_evaluation:
        

    def __init__(self, doc_len_file, word_to_tail_file , posting_list_file):
        
        self.posting_file    = open(posting_list_file, "rb")
        
        self.word_to_tail    = pickle.load(open(word_to_tail_file, "rb"))
        
        self.doc_len_map     = pickle.load(open(doc_len_file, "rb"))
        doc_len_sum          = sum(self.doc_len_map[doc_id] for doc_id in self.doc_len_map)
        self.avg_doc_len     = float(doc_len_sum)/N 
    
    def __enter__(self):
        return self
    def __exit__(self, type, value, traceback):
        self.posting_file.close()   
    
    def byte_array_to_int(self, byte_array):
        return struct.unpack("<i",byte_array)[0]
         

    def getPostingListEntry(self, starting_byte):
        
        pfile = self.posting_file
        pfile.seek(starting_byte)
        parent  = self.byte_array_to_int(pfile.read(4))
        cur_pl_len = self.byte_array_to_int(pfile.read(4))
        cur_pl = []
        while cur_pl_len:
            doc_id  = self.byte_array_to_int(pfile.read(4))
            pos_len = self.byte_array_to_int(pfile.read(4))
            positions = []
            while pos_len:
                positions.append(self.byte_array_to_int(pfile.read(4)))
                pos_len -=1
            cur_pl.append((doc_id,positions))
            cur_pl_len -=1
        
        return (parent,cur_pl)

    def getPostingList(self, word):
        
        cur = self.word_to_tail[word]       
        posting_list = []
        
        while True:
            (parent, cur_pl) = self.getPostingListEntry(cur)
            for (doc_id,positions) in cur_pl:
                posting_list.append(plentry(doc_id, positions))
            if parent == -1:
                break
            cur = parent
    
        
        return sorted(posting_list, key=lambda x: x.doc_id)
    
    def getScore(self, posting_list, metric, BM25_k1 = -1):
        
        if metric == TF:
            score_list = []
            for i in range (len(posting_list)):
                score_list.append(score_entry(posting_list[i].doc_id, len(posting_list[i].positions)))
            return sorted(score_list, key=lambda x: x.doc_id)
                

        elif metric == TFIDF:
            score_list = []
            try:
                idf = log(N/len(posting_list))
            except ZeroDivisionError:
                print query , "not present in any document"
                return []
            for i in range(len(posting_list)):
                score_list.append(score_entry(posting_list[i].doc_id, idf*len(posting_list[i].positions)))
            return sorted(score_list, key=lambda x: x.doc_id)
        
        
        elif metric == BM25:
            score_list = []
            
            if BM25_k1 < 1.2 or BM25_k1 > 2.0:
                print "Unacceptable value of k1 parameter, must be in range [1.2,2.0]"
                return []
            n = len(posting_list)
            idf = log (float(N - n + 0.5)/(n + 0.5))
            
            k1 = BM25_k1
            b = 0.75
            avgdl = self.avg_doc_len
            for i in range(len(posting_list)):
                doc_id = posting_list[i].doc_id
                tf = len(posting_list[i].positions)
                doc_len = self.doc_len_map[doc_id]
                score = (idf * (tf * (k1 + 1)))/(tf + k1 * (1 - b + b * (doc_len/avgdl)))
                score_list.append(score_entry(doc_id,score))
            return sorted(score_list, key=lambda x:x.doc_id)
        
        
        else:
            print "Fatal Error , unrecognized metric"
            sys.exit(-1)            
        
    def getPhrasalPostingList(self, query):
        if len(query) == 0:
            print "Fatal Error, empty query found"
            return []       
        cur_pl = self.getPostingList(query[0])
        for word in query[1:]:
            word_pl = self.getPostingList(word)
            new_pl = []
            i = 0
            j = 0
            while i<len(cur_pl) and j<len(word_pl):
                if cur_pl[i].doc_id < word_pl[j].doc_id:
                    i += 1
                elif word_pl[j].doc_id < cur_pl[i].doc_id:
                    j += 1
                else:
                    ii = 0
                    jj = 0
                    doc_cur_pl = sorted(cur_pl[i].positions)
                    doc_word_pl = sorted(word_pl[j].positions)
                    while ii < len(doc_cur_pl) and jj < len(doc_word_pl):
                        if doc_cur_pl[ii] > doc_word_pl[jj]:
                            jj += 1
                        # doc_cur_pl[ii] == doc_word_pl[jj], iff last_cur_word == word
                        # increment any one index in this case
                        elif doc_cur_pl[ii] == doc_word_pl[jj]:
                            jj += 1
                        else:
                            if doc_cur_pl[ii] == doc_word_pl[jj] -1:
                                #Found "phrase strict" following
                                if len(new_pl) > 0 and new_pl[-1].doc_id == cur_pl[i].doc_id:
                                    new_pl[-1].positions.append(doc_word_pl[jj])
                                else:
                                    new_pl.append(plentry(cur_pl[i].doc_id, [doc_word_pl[jj]]))
                                ii += 1
                                jj += 1
                            else:
                                ii += 1
                    i += 1
                    j += 1
            del cur_pl[:]
            cur_pl = new_pl
        return cur_pl
    
    def phrasalquery(self, query, metric):
        return self.getScore(self.getPhrasalPostingList(query), metric)

    def multiquery(self, query, metric):
        
        cur_score = []
        for word in query:
            word_score = self.getScore(self.getPostingList(word),metric)
            i = 0
            j = 0
            new_score = []
            while i<len(cur_score) or j<len(word_score):
                
                if i == len(cur_score):
                    new_score.append(word_score[j])
                    j+=1
                elif j == len(word_score):
                    new_score.append(cur_score[i])
                    i+=1
                elif cur_score[i].doc_id < word_score[j].doc_id:
                    new_score.append(cur_score[i])
                    i+=1
                elif word_score[j].doc_id < cur_score[i].doc_id:
                    new_score.append(word_score[j])
                    j+=1
                else:
                    word_score[j].score += cur_score[i].score
                    new_score.append(word_score[j])
                    i+=1
                    j+=1
            del cur_score[:]
            cur_score = new_score
        return cur_score
