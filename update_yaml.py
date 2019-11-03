#!/usr/bin/env python
from __future__ import print_function
import six
import argparse
try:
    from ruamel.yaml import YAML
except ImportError:
    raise ImportError('cannot import ruamel.yaml')
import collections
from copy import deepcopy
import os
import sys

"""
Description: 
  - This Script is to update a key value in yaml file of varying key depth
  - Supports python version 2 and 3
  - As we are using the ruamel.yaml module the comments and order will be preserved
Usage: 
  update_yaml.py -k <key_path_in_yaml_file> -v <value you want to update> -f <file_path> -t <type>
Example:
  update_yaml.py -k foo.bar -v abc -f dummy.txt -t str
Note:
  - key_path should always be used with separator '.'
  - value will be string by default unless specified with -t parameter
  - file_path can either be relative or absolute path
  - Supported types with -t are str, int, float and bool. 
  - Updating lists and dictionaries are not yet supported

"""

yaml = YAML()

parser = argparse.ArgumentParser(description='Update the yaml files with keys')
parser.add_argument('-k', '--key_path', type=str, required=True, help='Key path in yaml file to be updated')
parser.add_argument('-f', '--file_path', type=str, required=True, help='Absolute Path of Input File')
parser.add_argument('-v', '--key_value', type=str, required=True, help='Value for key to be updated')
parser.add_argument('-t', '--type', choices=['str','int','float', 'bool'], required=False, default='str', help='Type of value to be updated')
args = parser.parse_args()

def input_to_lst(keypath, value):
    '''To convert the input parameters to a list'''
    try:
        key_path_list = keypath.split('.')
    except:
        raise Exception('Error: Input key path should be in format of <key>.<key>')
    else:
        key_path_list.append(value)
        return key_path_list

def load_yaml(file_path):
    '''Convert source yaml file to dictionary'''
    try:
        with open(file_path) as yaml_input_file:
            file_content_dict = yaml.load(yaml_input_file)
    except:
        raise Exception('Error: Not able to open file')
    else:
        return file_content_dict

def gen_dict(lst):
    '''Generating a dictionary based on input keypath and value'''
    if len(lst) == 2:
        return {lst[0]:lst[1]}
    else:
        return {lst[0]:gen_dict(lst[1:])}

def merge(dict1, dict2):
    ''' Return a new dictionary by merging two dictionaries recursively. '''
    try:
        result = deepcopy(dict1)
        for key, value in six.iteritems(dict2):
            if isinstance(value, collections.Mapping):
                result[key] = merge(result.get(key, {}), value)
            else:
                result[key] = deepcopy(dict2[key])
    except AttributeError:
        raise AttributeError("Error: Key path not supported for update")
    except TypeError:
        raise TypeError("Error: key path conflict, cannot update already existing string with new keypath")
    else:
        return result 

def update_yaml_file(file_path, file_content_dict):
    '''To write the filewith the updated content'''
    try: 
        with open(file_path,'w') as yaml_file:
            yaml.dump(file_content_dict, yaml_file)
    except:
        raise Exception('Error: Not able to open file to write')
    else: 
        print('{} updated!'.format(file_path))

def determine_value_type(key_value, key_type='str'):
    if (key_type == 'bool') and (key_value == 'True' or key_value == 'False'):
        return bool(key_value)
    elif key_type == 'int':
        try:
            key_value = int(key_value)
        except ValueError:
            raise ValueError('Cannot convert {} to {}'.format(key_value, key_type))
        else: 
            return key_value
    elif key_type == 'float':
        try:
            key_value = float(key_value)
        except ValueError:
            raise ValueError('Cannot convert {} to {}'.format(key_value, key_type))
        else: 
            return key_value
    else:
        return key_value

def main():
    ''' Main function where core logic is used'''
    if os.path.exists(args.file_path):
        file_content_dict = load_yaml(args.file_path)
    else:
        print("Error: File --> {} not found".format(args.file_path))
        sys.exit(1)

    key_value = determine_value_type(args.key_value, args.type)
    key_value_list = input_to_lst(args.key_path, key_value)
    dict_to_merge = gen_dict(key_value_list)
    file_content_dict = merge(file_content_dict, dict_to_merge)
    update_yaml_file(args.file_path, file_content_dict)

# Execution Starts here
if __name__ == '__main__':
    main()
