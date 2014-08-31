from bs4 import BeautifulSoup
from utility import normalize_line
from nltk.corpus import stopwords
import nltk

class HtmlParser:

    def __init__(self,  location, name, stem=False, ignore_stop_word=False):
        self.fileName = name
        self.fileLocation = location
        self.inputHtml = open(self.fileLocation+self.fileName).read()
        self.parseHtml = BeautifulSoup(self.inputHtml)
        self.ignore_stop_word = ignore_stop_word
        self.stop_word_list = stopwords.words("english")
        self.stem = stem
        self.word_stemmer = nltk.stem.porter.PorterStemmer()

    def print_file_name(self):
        print "FileName : ", self.fileName

    def is_valid_word(self, word):

        if self.stem:
            word = self.word_stemmer.stem(word)

        if word.isalnum():
            if self.ignore_stop_word and word in self.stop_word_list:
                return False, ""
            return True, word
        return False, ""

    def get_all_words(self):
        str = self.parseHtml.text
        lines = str.split("|")
        final_words = []
        for line in lines:
            line = normalize_line(line)
            if line != "":
                words = line.split()
                for word in words:
                    (valid, final_word) = self.is_valid_word(word)
                    if valid:
                        final_words.append(final_word)
        return final_words




