import sys
import os
from os import listdir
from os.path import isfile, join
from htmlparser import HtmlParser
import struct
import pickle

def get_byte_array(num):
    return struct.pack("<i", num)


def iterate_folder(fp, word_to_tail_map, file_path):

    document_list = [document_name for document_name in listdir(file_path) if isfile(join(file_path, document_name))]

    for document in document_list:
        if document.isdigit():
            print document
            html_parser = HtmlParser(file_path, document, False, True)
            word_list = html_parser.get_all_words()
            word_to_position_map = {}
            current_position = 1
            for word in word_list:
                if word not in word_to_position_map:
                    word_to_position_map[word] = []

                word_to_position_map[word].append(current_position)
                current_position += 1

            for word in word_to_position_map:
                new_tail = fp.tell()

                if word not in word_to_tail_map:
                    word_to_tail_map[word] = -1

                fp.write(get_byte_array(word_to_tail_map[word]))
                word_to_tail_map[word] = new_tail
                fp.write(get_byte_array(int(document)))
                fp.write(get_byte_array(len(word_to_position_map[word])))
                for pos in word_to_position_map[word]:
                    fp.write(get_byte_array(pos))


def main():
    fp = open("posting_list", "wb")
    word_to_tail_map = {}

    pickle_file_name = "dictionary.pickle"
    directory_name = "/home/arun/data/asd/"

    folder_list = [os.path.join(directory_name, o) for o in os.listdir(directory_name) if os.path.isdir(os.path.join(directory_name, o))]

    for folder in folder_list:
        iterate_folder(fp, word_to_tail_map, folder+"/")

    fp.close()
    fp = open(pickle_file_name, "wb")
    pickle.dump(word_to_tail_map, fp)
    fp.close()

if __name__ == "__main__":
    main()
