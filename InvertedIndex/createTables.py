import MySQLdb
import string 

def create_tables():

	ip = "172.16.27.30"
	user   = "root"
	password = "ir" 
	database = "information_retrieval2"
	connstring = MySQLdb.connect(ip,user,password)
	cursor = connstring.cursor()
	sql = 'CREATE DATABASE ' + database
	cursor.execute(sql)
	connstring = MySQLdb.connect(ip,user,password,database)
	cursor = connstring.cursor()
	atoz = string.lowercase[:26]
	for i in atoz:
		for j in atoz:
			sql = 'CREATE TABLE '+i+j+'_' + ' ( word_id INT, document_id INT, position INT ) ;'
			cursor.execute(sql)


if __name__ == '__main__':
	create_tables()