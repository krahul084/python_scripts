#!/usr/bin/env python
#Importing the OS Module
import os
import argparse

parser = argparse.ArgumentParser(description='Identify files with input strings')
parser.add_argument('-d', '--dir', type=str, metavar='', required=True, help='Absolute Path of Directory to Search')
parser.add_argument('-if','--input_file', type=str, metavar='', required=True, help='Absolute Path of Input File')
args = parser.parse_args()

#Getting the path and input file as user input recommended to input absolute paths
path = args.dir
input_file = args.input_file

#Storing the search strings as set variable
pass_pattern = set([line.strip().split() for line in open(input_file).readlines()][0])

#Function to capture the absolute paths of all files in the path
def get_absFilePath(path):
   for fname in os.walk(path):
       for file in fname[2]:
           yield os.path.abspath(os.path.join(fname[0], file))

#Function to capture the identified files for the search strings
def find_string(path,pass_pattern):
    for file in get_absFilePath(path):
        if os.path.isfile(file):
            for string in pass_pattern:
                with open(file,'r') as file_content:
                        for num,line in enumerate(file_content,1):
                            if string in line:
                                yield string+" - "+file+":"+str(num)

#Main Function to print the files with the total identified items
def main():
    output_list = list(find_string(path,pass_pattern))
    for item in output_list:
        print item
    print "Total number of items found: %s" % len(output_list)

#Execution Starts Here
if __name__ == '__main__':
    main()

         
