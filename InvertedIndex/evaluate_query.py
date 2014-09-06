import pickle
import sys
import math
import linecache as lc

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

class score:
	def __init__(self, doc_id , score):
		self.doc_id = doc_id
		self.score  = score

class query_evaluation:
	def __init__(self, doc_len_file, word_to_id_file , start_idx_file , posting_list_file):
		self.posting_file    = posting_list_file
		self.hash_file       = start_idx_file
		
		self.word_id_map     = pickle.load(open(word_to_id_file,"rb")) 	
		self.doc_len_map     = pickle.load(open(doc_len_file, "rb"))
		doc_len_sum          = sum(self.doc_len_map[doc_id] for doc_id in self.doc_len_map)
		self.avg_doc_len     = float(doc_len_sum)/N	

		f = open(start_idx_file,"r").read().split('\n')[:-1]
		self.wid_idx_map = {}
		for i in range(len(f)):
			(word_id , start_idx) = map(int,f[i].split(' '))
			self.wid_idx_map[word_id] = start_idx
		
	def getPostingList(self, word):
		word_id   = self.word_id_map[word]
		start_idx = self.wid_idx_map[word_id]
		pfile 	  = self.posting_file
		posting_list = []
		last_idx = self.wid_idx_map[word_id+1] if self.wid_idx_map.has_key(word_id + 1) else -1
		last_insert_idx = -1
		cur_line_idx = start_idx
		prev_doc_id = -1
		while True:
			line = getline(pfile,cur_line_idx)
			if cur_line_idx == last_idx or line == '':
				break
			(doc_id , pos) = map(int, line[:-1].split())
			if doc_id != prev_doc_id:
				posting_list.append(plentry(doc_id,[pos]))
				prev_doc_id = doc_id
				last_insert_idx += 1
			else:
				posting_list[last_insert_idx].positions.append(pos)
			cur_line_idx += 1
		
		return sorted(posting_list, key=lambda x: x.doc_id)
	
	def getScore(self, posting_list, metric, BM25_k1 = -1):
		
		if metric == TF:
			score_list = []
			for i in range (len(posting_list)):
				score_list.append(score(posting_list[i].doc_id, len(posting_list[i].positions)))
			return sorted(score_list, key=lambda x: x.doc_id, reverse = False)
				

		elif metric == TFIDF:
			score_list = []
			try:
				idf = log(N/len(posting_list))
			except ZeroDivisionError:
				print query , "not present in any document"
				return []
			for i in range(len(posting_list)):
				score_list.append(score(posting_list[i].doc_id, idf*len(posting_list[i].positions)))
			return sorted(score_list, key=lambda x: x.doc_id, reverse = False)
		elif metric == BM25:
			score_list = []
			
			if BM25_k1 < 1.2 or BM25_k1 > 2.0:
				print "Unacceptable value of k1 parameter, must be in range [1.2,2.0]"
				return []
			
			#idf = 

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
					#print "doc_id match at ", cur_pl[i].doc_id
					ii = 0
					jj = 0
					doc_cur_pl = sorted(cur_pl[i].positions)
					doc_word_pl = sorted(word_pl[j].positions)
					while ii < len(doc_cur_pl) and jj < len(doc_word_pl):
						#print "\t%d %d\n"%(doc_cur_pl[ii],doc_word_pl[jj])
						if doc_cur_pl[ii] > doc_word_pl[jj]:
							jj += 1
						# doc_cur_pl[ii] == doc_word_pl[jj], iff last_cur_word == word
						# increment any one index in this case
						elif doc_cur_pl[ii] == doc_word_pl[jj]:
							jj += 1
						else:
							if doc_cur_pl[ii] == doc_word_pl[jj] -1:
								#Found "phrase strict" following
								#print "Found matching positions %d %d\n"%(doc_cur_pl[ii],doc_word_pl[jj])
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
						
					

test = query_evaluation("d","dictionary.pickle","h","p")

a = sorted(test.phrasalquery(['new','york'],TF), key = lambda x:x.score)
for y in a:
	#y = 1
	print y.doc_id , y.score

'''l = []
for query in test.word_id_map:
	l.append(query)
for query in l:
	try:
	    for score_entry in test.unigram(query,TFIDF):
		    (a,b) =  (score_entry.doc_id , score_entry.score)
	except KeyError:
		pass'''

