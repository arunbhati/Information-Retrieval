import sys
import os
from os import listdir
from os.path import isfile, join
from htmlparser import HtmlParser
import struct
import pickle

def get_byte_array(num):
    return struct.pack("<i", num)


def iterate_folder(fp, word_to_tail_map, document_len_map, file_path, file_chunk_size):

    document_list = [document_name for document_name in listdir(file_path) if isfile(join(file_path, document_name))]
    
    word_info = {}
    cur_chunk_size = 0
    for document in document_list:
        if document.isdigit():
            html_parser = HtmlParser(file_path, document, False, True)
            word_list = html_parser.get_all_words()
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

            cur_chunk_size += 1
            if cur_chunk_size < file_chunk_size:
                continue            

            print document

            for word in word_info:
                new_tail = fp.tell()
                if word not in word_to_tail_map:
                    word_to_tail_map[word] = -1

                fp.write(get_byte_array(word_to_tail_map[word]))
                word_to_tail_map[word] = new_tail
                fp.write(get_byte_array(0))
                #space for number of documents containing the word reserved
                total_int_written = 0
                for (word_doc,positions) in word_info[word]:
                    fp.write(get_byte_array(int(word_doc)))
                    fp.write(get_byte_array(0))
                    pos_len = 0
                    for pos in positions:
                        fp.write(get_byte_array(pos))
                        pos_len += 1
                    fp.seek(fp.tell()-(pos_len+1)*4)
                    fp.write(get_byte_array(pos_len))
                    fp.seek(fp.tell()+pos_len*4)
                    total_int_written += (pos_len+2)
                
                fp.seek(fp.tell()-(total_int_written+1)*4)
                fp.write(get_byte_array(total_int_written))
                fp.seek(fp.tell()+total_int_written*4)
                    
            word_info = {}
            cur_chunk_size = 0


def main():
    fp = open("posting_list", "wb")
    


    word_pickle_file = "dictionary.pickle"
    document_pickle_file = "document.pickle"
    directory_name = "/home/arun/dataset/asd/"
    
    """
    if isfile(word_pickle_file):
        word_to_tail_map = pickle.load(open(word_pickle_file,"rb"))
    else:
        word_to_tail_map = {}
    """

    word_to_tail_map = pickle.load(open(word_pickle_file,"rb")) if isfile(word_pickle_file) else {}

    """
    if isfile(document_pickle_file):
        document_len_map = pickle.load(open(document_pickle_file,"rb"))
    else:
        document_len_map = {}
    """

    document_len_map = pickle.load(open(document_pickle_file,"rb")) if isfile(document_pickle_file) else {}

    folder_list = [os.path.join(directory_name, o) for o in os.listdir(directory_name) if os.path.isdir(os.path.join(directory_name, o))]

    for folder in folder_list:
        iterate_folder(fp, word_to_tail_map, document_len_map, folder+"/", 2000)
    fp.close()
    
    fp = open(word_pickle_file, "wb")
    pickle.dump(word_to_tail_map, fp)
    fp.close()
    
    fp = open(document_pickle_file,"wb")
    pickle.dump(document_len_map, fp)
    fp.close()

if __name__ == "__main__":
    main()
