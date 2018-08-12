#!/usr/bin/env python
import os

path = raw_input("Enter the path to search: ")
input_file = raw_input("Enter the input file absolute path: ")
pass_pattern = set([i.strip().split() for i in open(input_file).readlines()][0])

def get_absFilePath(path):
   for fname in os.walk(path):
       for file in fname[2]:
           yield os.path.abspath(os.path.join(fname[0], file))


def find_string(path,pass_pattern):
    for file in get_absFilePath(path):
        if os.path.isfile(fname):
            for string in pass_pattern:
                with open(file,'r') as file_content:
                    if string in file_content.read():
                        yield string+"-"+file


def main():
    for item in find_string(path,pass_pattern):
        print item

main()
