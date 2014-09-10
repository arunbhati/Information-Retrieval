from htmlparser import HtmlParser
from evaluate_query_without_db import query_evaluation
import sys
def fetch_data(i):
   # fileName = raw_input("Enter File Name : ")
    
	htmlParser = HtmlParser("/home/arun/0/",str(i),False,True)
	word_list = htmlParser.get_all_words()
	for word in word_list:
		print word


def evaluate_query():
	
	print "starting loading evaluate query object"
	test = query_evaluation("documentYY.pickle","dictionaryYY.pickle","posting_listYY")
	print "Done with loading"
	TF = 0
	TFIDF = 1
	BM25 = 2

	while True:
		print "Enter 0(multiquery)/1(phrasalquery)/2(EXIT)"
		qtype = int(raw_input())
		if qtype == 2:
			break
		print "Enter words separated by space"
		query = sys.stdin.readline().split()
		print "Enter metric 0(TF) , 1(TFIDF) , 2(BM25)"
		metric = int(raw_input())
		if qtype == 0:
			a = sorted(test.multiquery(query,metric), key = lambda x:x.score)
			for y in a:
				print y.doc_id , y.score

		else:
			a = sorted(test.phrasalquery(query,metric), key = lambda x:x.score)
			for y in a:
				print y.doc_id , y.score


if __name__ == '__main__':
	evaluate_query()
	#fetch_data(2127)
