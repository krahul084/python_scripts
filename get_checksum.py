#!/usr/bin/python

DOCUMENTATION = '''
---
module: get_checksum

short_description: 
   - Generate a checksum for a directory/file
   - References:
        Took some source code from https://pypi.org/project/checksumdir and converted into ansible module
        

version_added: "2.6"

description:
    - "Generate a checksum for a directory/file"

options:
  path:
    description:
      - The full path of the file/object to get the facts of.
    required: true
  follow_links:
    description:
      - Whether to follow symlinks.
      - Only works for directory
    type: bool
    default: 'no'
  checksum_type:
    description:
      - Which checksum algorithm to use to apply to the path
    choices: ['md5', 'sha1', 'sha256', 'sha512']
    default: 'md5'
    type: str
  exclude_files:
    description: 
      - The files to be excluded in the path for the checksum calculation
      - Only works for directory 
    default: None
    type: list
  ignore_hidden: 
    description: 
      - If hidden files should be included
      - Only works for directory
    default: False
    type: bool
  exclude_extensions:
    description:
      - If certain file extensions should be ignored
      - Only works for directory
    default: None
    type: list

author:
    - Rahul K
'''

EXAMPLES = '''
# Generate Checksum Value for a directory/file
# Default to checksum_type of md5
- get_checksum:
    path: path/to/(directory/file)
  register:  checksum

- debug
    msg:  'Checksum_value is {{ checksum.checksum_value }}'

# Generate the Checksum Value with certain checksum_algorithm 
- get_checksum: 
     path: path/to/directory
     checksum_type: sha1/md5/sha256/sha512
  register: checksum

# Generate checksum value of directory excluding files
- get_checksum:
      path: path/to/directory
      exclude_files: 
         - test1
         - test2
  register: checksum

# Generate checksum value of directory excluding certain extensions
- get_checksum:
      path: path/to/directory
      exclude_extensions: 
          - py
          - git
  register: checksum

# Generate checksum value of directory ignoring hidden files
- get_checksum:
      path: path/to/directory
      ignore_hidden: yes
  register: checksum

# If the contents of sym links needs to be included
- get_checksum:
      path: path/to/directory
      follow_symlinks: yes
  register: checksum
'''

RETURN = '''
checksum_value:
    description: The checksum value generated
    type: str
'''

# Importing the required modules for calculating the checksum
import os
import hashlib
import re

# Importing the Ansible Module 
from ansible.module_utils.basic import *

# Defining the methods from the hashlib library for each hashing algorithm
HASH_FUNCS = {
    'md5': hashlib.md5,
    'sha1': hashlib.sha1,
    'sha256': hashlib.sha256,
    'sha512': hashlib.sha512
}

# Method to perform hashing of a directory with extra options
def dirhash(dirname, hashfunc, exclude_files, ignore_hidden,
            followlinks, exclude_extensions):
    hash_func = HASH_FUNCS.get(hashfunc)
    hashvalues = []
    for root, dirs, files in os.walk(dirname, topdown=True, followlinks=followlinks):
        if ignore_hidden:
            if not re.search(r'/\.', root):
                hashvalues.extend(
                    [_filehash(os.path.join(root, f),
                               hash_func) for f in files if not
                     f.startswith('.') and not re.search(r'/\.', f)
                     and f not in exclude_files
                     and f.split('.')[-1:][0] not in exclude_extensions
                     ]
                )
        else:
            hashvalues.extend(
                [
                    _filehash(os.path.join(root, f), hash_func) 
                    for f in files 
                    if f not in exclude_files
                    and f.split('.')[-1:][0] not in exclude_extensions
                ]
            )
    return _reduce_hash(hashvalues, hash_func)

# Method to perform the hash of a single file
def _filehash(filepath, hashfunc):
    hasher = hashfunc()
    blocksize = 64 * 1024
    with open(filepath, 'rb') as fp:
        while True:
            data = fp.read(blocksize)
            if not data:
                break
            hasher.update(data)
    return hasher.hexdigest()

# Method to reduce the individual hashes of each file
def _reduce_hash(hashlist, hashfunc):
    hasher = hashfunc()
    for hashvalue in sorted(hashlist):
        hasher.update(hashvalue.encode('utf-8'))
    return hasher.hexdigest()

# Method for getting arguments and running the main logic
def run_module():
    # define the available arguments/parameters that a user can pass to
    # the module
    module_args = dict(
        path=dict(required=True, type='path'),
        checksum_type=dict(type='str', default='md5', 
                      choices=['md5', 'sha1', 'sha256', 'sha512']),
        exclude_files=dict(type='list', default=[]),
        exclude_extensions=dict(type='list', default=[]),
        ignore_hidden=dict(type='bool', default=False),
        follow_links=dict(type='bool', default=False),
    )

    # seed the result dict in the object
    # we primarily care about changed and state
    # change is if this module effectively modified the target
    # state will include any data that you want your module to pass back
    # for consumption, for example, in a subsequent task
    result = dict(
        changed=False,
        checksum_value=''
    )

    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    # if the user is working with this module in only check mode we do not
    # want to make any changes to the environment, just return the current
    # state with no modifications
    if module.check_mode:
        return result

    # Store the passed arguments in variables
    path = module.params['path']
    checksum_type = module.params['checksum_type']
    exclude_files = module.params['exclude_files']
    exclude_extensions = module.params['exclude_extensions']
    ignore_hidden = module.params['ignore_hidden'] 
    follow_links = module.params['follow_links']

# Check if the path is a directory and calculate checksum
    if os.path.isdir(path):
        result['checksum_value'] = dirhash(path, checksum_type, exclude_files, 
                                  ignore_hidden, follow_links, exclude_extensions)

# Check if the path is a file and calculate the checksum
    elif os.path.isfile(path):
        hasher = HASH_FUNCS.get(checksum_type)
        result['checksum_value'] = _filehash(path, hasher)

# Fail if its neither a file nor a directory
    else:
        result['failed'] = True
        error = '{} is not a valid path.'.format(path)
        module.fail_json(msg=error, meta=result)

    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    result['changed'] = True
    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()
