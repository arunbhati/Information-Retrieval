import sys
import MySQLdb
import os
import os.path
from htmlparser import HtmlParser
import pickle
from os import listdir
from os.path import isfile, join

log_file = "log_file"
ip = "172.16.27.30"
user   = "root"
password = "ir" 
database = "information_retrieval"
commit_iterations=200
document_len_file="doc_len.txt"
pickle_file_name="dictionary.pickle"

class buildindex:
	def __init__(self):
		self.dict = {}
		#Set up the connection string
		self.connstring = MySQLdb.connect(ip,user,password,database)
		self.databasecursor = self.connstring.cursor()
		self.current_word_id=0
		self.current_doc_id=0
		self.fp_doc_len=open(document_len_file,"w")

	def insertdict(self,words):
		
		sql = "INSERT INTO posting_list (document_id,word_id,position) values "		
		try:
			for word in words:
				if not self.dict.has_key(word):
					self.dict[word] = self.current_word_id
					self.current_word_id = self.current_word_id + 1

			rsql = sql + ','.join(["(%d,%d,%d)"%(self.current_doc_id,self.dict[words[index]],index) for index in xrange(len(words)) ])
			if rsql != sql:			
				self.databasecursor.execute(rsql)
		except Exception as e:
			fw = open(log_file,"a")
			fw.write("Unable to process the query for " + str(self.current_doc_id) + "\n")
			fw.close()
		self.fp_doc_len.write("%d %d\n"%(self.current_doc_id,len(words)))

	def iteratefolder(self,filepath):
		count = 1
		
		document_list = [ document_name for document_name in listdir(filepath) if isfile(join(filepath,document_name)) ]

		for document in document_list:
			if document.isdigit():
				print document
				dir_entry_path = filepath + document
				if os.path.isfile(dir_entry_path):
					if self.current_doc_id%commit_iterations==0 :
						self.connstring.commit()
						self.fp_doc_len.close()
						self.fp_doc_len=open(document_len_file,"a")
					htmlparser=	HtmlParser(filepath, document,False,True)
					word_list = htmlparser.get_all_words()
					self.insertdict(word_list)
					self.current_doc_id= int(document)
				else:
					print "Fatal Error , file not found %s"%(dir_entry_path)
					sys.exit(-1)


if __name__ == '__main__':
	a=buildindex()
	
	directory_name  = sys.argv[1]
	folder_list = [os.path.join(directory_name,o) for o in os.listdir(directory_name) if os.path.isdir(os.path.join(directory_name,o))]

	for folder in folder_list:
		a.iteratefolder(folder+"/")

	fp = open(pickle_file_name,"wb")
	pickle.dump(a.dict,fp)
	fp.close()	
