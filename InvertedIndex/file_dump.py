import MySQLdb as mdb
import pickle

ip = "172.16.27.30"
user = "root"
passwd = "ir"
database = "information_retrieval"

'''
test = dump_to_file("imput_hash_file_name","input_posting_file_name", "table_name" , "field_name_to_group")
test.start_dump()
sampe usage:
test = dump_to_file("h","p","posting_list1","word_id")
test.start_dump()
'''	
class dump_to_file:
	def __init__(self, start_idx_file , posting_list_file, doc_len_file, table_name, field_name):
		self.db = mdb.connect(ip,user,passwd,database)
		self.cursor        = self.db.cursor()
		self.posting_file  = posting_list_file
		self.hash_file     = start_idx_file
		self.doc_len_file  = doc_len_file
		self.table_name    = table_name
		self.field_name    = field_name
	
	def start_dump(self):
		tablenm = self.table_name
		pfile   = open(self.posting_file, "w")
		hfile   = open(self.hash_file, "w")
		fieldnm = self.field_name
		self.cursor.execute("SELECT word_id, document_id , position FROM %s ORDER BY %s"%(tablenm,fieldnm))
		doc_len_map = {}
		prev_word_id = -1
		line_num = 1
		for (word_id , doc_id , pos) in self.cursor:
			if word_id != prev_word_id:
				hfile.write("%d %d\n"%(word_id,line_num))
				prev_word_id = word_id
			pfile.write("%d %d\n"%(doc_id,pos))
			line_num += 1
			if doc_id not in doc_len_map:
				doc_len_map[doc_id] = 0
			doc_len_map[doc_id] += 1

		pickle.dump(doc_len_map, open(self.doc_len_file, "wb"))
			
				
				
test = dump_to_file("h","p","d","posting_list1","word_id")
test.start_dump()

