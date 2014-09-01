import sys
import MySQLdb
import os
from htmlparser import HtmlParser

log_file = "log_file"
######### Database 
ip = "172.16.27.30"
user   = "root"
password = "ir" 
database = "information_retrieval"
commit_iterations=100
class buildindex:
	def __init__(self):
		self.dict = {}
		#Set up the connection string
		self.connstring = MySQLdb.connect(ip,user,password,database)
		self.databasecursor = self.connstring.cursor()
		self.current_word_id=0
		self.current_doc_id=0

	def insertdict(self,words):
		current_word_index=1
		for a_word in words:
			try:
				if(self.dict.has_key(a_word)):
					sql = "INSERT INTO posting_list (document_id,word_id,position) values(%d,%d,%d)"%(self.current_doc_id,self.dict[a_word],current_word_index)
					self.databasecursor.execute(sql)
					#print self.databasecursor.fetchall()
				else:
					self.dict[a_word]=self.current_word_id
					self.current_word_id=self.current_word_id+1
					sql = "INSERT INTO posting_list (document_id,word_id,position) values(%d,%d,%d)"%(self.current_doc_id,self.dict[a_word],current_word_index)
					self.databasecursor.execute(sql)
					#print self.databasecursor.fetchall()
				current_word_index=current_word_index+1
			except Exception as e:
				fw = open(log_file,"a")
				fw.write("Unable to process the query for " + str(self.current_doc_id) + " " + str(self.dict[a_word]) + " " + str(current_word_index) + " " + a_word + "\n")
				current_word_index=current_word_index+1
				fw.close()
			
	def iteratefolder(self,filepath):
		count=1
		for dir_entry in os.listdir(filepath):
			print self.current_doc_id
			dir_entry_path = os.path.join(filepath, dir_entry)
			if os.path.isfile(dir_entry_path):
				if(self.current_doc_id%commit_iterations==0):
					self.connstring.commit()
				htmlparser=	HtmlParser(filepath, dir_entry,False,True)
				word_list = htmlparser.get_all_words()
				self.insertdict(word_list)
				self.current_doc_id=self.current_doc_id+1
	
	

if __name__ == '__main__':
	a=buildindex()
	a.iteratefolder(sys.argv[1])
