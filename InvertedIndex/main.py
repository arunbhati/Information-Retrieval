from htmlparser import HtmlParser
from evaluate_query_without_db import query_evaluation

def fetch_data(i):
   # fileName = raw_input("Enter File Name : ")
    
	htmlParser = HtmlParser("/home/arun/0/",str(i),False,True)
	word_list = htmlParser.get_all_words()
	for word in word_list:
		print word


def evaluate_query(query,metric):
	
	test = query_evaluation("document.pickle","dictionary.pickle","posting_list")
	a = sorted(test.multiquery(query,metric), key = lambda x:x.score)
	for y in a:
		print y.doc_id , y.score




if __name__ == '__main__':
	query = ['sex','porn']
	TF = 0
	TFIDF = 1
	BM25 = 2
	evaluate_query(query,TF)
	#fetch_data(2127)
