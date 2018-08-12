#!/usr/bin/env python
#Script to display files matching the strings supplied as input from a text file containing strings delimited by space
#Importing the OS Module 
import os

#Getting the path and input file as user input recommended to input absolute paths
path = raw_input("Enter the path to search: ")
input_file = raw_input("Enter the input file absolute path: ")

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
                    if string in file_content.read():
                        yield string+" - "+file

#Main Function to print the files with the total identified items
def main():
    output_list = list(find_string(path,pass_pattern))
    for item in output_list:
        print item
    print "Total number of items found: %s" % len(output_list)
main()
         
