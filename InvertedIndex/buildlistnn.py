import sys
import os
from os import listdir
from os.path import isfile, join, getsize
from htmlparser import HtmlParser
import struct
import pickle
import signal


def signal_handler(signum, frame):
    raise Exception("Itna time!")

signal.signal(signal.SIGALRM, signal_handler)


def get_byte_array(num):
    return struct.pack("<q", num)

def iterate_folder(fp, word_to_tail_map, document_len_map, file_path):

    document_list = [document_name for document_name in listdir(file_path) if isfile(join(file_path, document_name)) and document_name.isdigit()]
    word_info = {}
    
    for document in sorted(document_list, key=lambda x:int(x)):
        
        print "doing for ", document
        if getsize(file_path+document) > 3000000:
            continue
       
        signal.alarm(3)   # Ten seconds 
        try:
            html_parser = HtmlParser(file_path,document,False,True)
            word_list = html_parser.get_all_words()
        except Exception , e:
            log_file_to_check = open("log_file_done_tillNN","a")
            log_file_to_check.write("Time out for %s\n"%(document))
            log_file_to_check.close()
            continue

        signal.alarm(0)

        word_to_position_map = {}
        
        current_position = 1
        for word in word_list:
            if word not in word_to_position_map:
                word_to_position_map[word] = []

            word_to_position_map[word].append(current_position)
            current_position += 1
        document_len_map[int(document)] = current_position - 1 

        for word in word_to_position_map:
            if word not in word_info:
                word_info[word] = []
            word_info[word].append((int(document),word_to_position_map[word]))            


    log_file_to_check = open("log_file_done_tillNN","a")
    log_file_to_check.write("%s\n"%(file_path))
    log_file_to_check.close()
            
    for word in word_info:
        new_tail = fp.tell()
        if word not in word_to_tail_map:
            word_to_tail_map[word] = -1

        fp.write(get_byte_array(word_to_tail_map[word]))
        word_to_tail_map[word] = new_tail
        
        for (word_doc,positions) in word_info[word]:
            
            # write document id to file
            fp.write(get_byte_array(int(word_doc)))
            
            # write positions list to file with -1 as end of list symbol
            for pos in positions:
                fp.write(get_byte_array(pos))
            fp.write(get_byte_array(-1))

        
        #writting -1 as end of information related to a particular word in file
        fp.write(get_byte_array(-1))

    word_info = {}

def main():
    fp = open("posting_listNN", "ab")

    word_pickle_file = "dictionaryNN.pickle"
    document_pickle_file = "documentNN.pickle"
    directory_name = "/home/arun/irdataset/"
    
    word_to_tail_map = pickle.load(open(word_pickle_file,"rb")) if isfile(word_pickle_file) else {}
    document_len_map = pickle.load(open(document_pickle_file,"rb")) if isfile(document_pickle_file) else {}

    folder_list = [os.path.join(directory_name, o) for o in os.listdir(directory_name) if os.path.isdir(os.path.join(directory_name, o))]

    for folder in sorted(folder_list, key=lambda x: int(x.split('/')[-1])):
        iterate_folder(fp, word_to_tail_map, document_len_map, folder+"/")
    fp.close()
    
    fp = open(word_pickle_file, "wb")
    pickle.dump(word_to_tail_map, fp)
    fp.close()
    
    fp = open(document_pickle_file,"wb")
    pickle.dump(document_len_map, fp)
    fp.close()

if __name__ == "__main__":
    main()
