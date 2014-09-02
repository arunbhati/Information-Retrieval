from htmlparser import HtmlParser

def fetch_data():
   # fileName = raw_input("Enter File Name : ")
    
	htmlParser = HtmlParser("/home/arun/0/", "0",False,True)
	word_list = htmlParser.get_all_words()
	for word in word_list:
		print word

if __name__ == '__main__':
    fetch_data()
