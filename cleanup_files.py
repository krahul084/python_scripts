DOCUMENTATION = '''
---
module: cleanup_files

short_description: Clean files in the path

version_added: "2.7"

description:
    - "Cleanup files based on some criteria in a path"
    - "Ported statinfo, age, size filter functions from ansible find module"

options:
  path_pattern:
    description:
      - The path pattern/glob style pattern of path where the files need to be deleted
      - This doesn't includes sub-directories 
    type: str
    required: true

  state:
    description: 
      - The action you want to take on the matched files.
    choices: ['list', 'absent']
    default: 'list'
    type: list

  excludes:
    description:
      - The patterns of the files to exclude
    type: list

  file_type:
    description: 
      - To search based on the directory or file
    default: any
    choices: ['file', 'directory']
    type: str

  age:
    description: 
      - Filter based on the age of the file 
      - age can be mentioned in seconds(s)/minutes(m)/hours(h)/days(d)/weeks(w) 
    default: None
    type: str

  age_stamp: 
    description: 
      - Filter the age based on the age_stamp
    default: mtime
    choices: ['mtime', 'ctime', 'atime']
    type: str 

  size:
    description:
      - Filter based on the file size 
      - size can be mentioned in bytes(b)/kilobytes(k)/megabytes(m)/gigabytes(g)/terabytes(t)

author:
    - Rahul K
'''

EXAMPLES = '''
# List the files to be deleted
- cleanup_files: 
      path_pattern: /tmp/*
      state: list
  register: foo

- debug: 
      var: foo.files

# Cleanup all the files
- cleanup_files: 
      path_pattern: /tmp/*.log
      state: absent

# Cleanup all the files based on file_type
- cleanup_files: 
      path_pattern: /tmp/*.log
      state: absent
      file_type: directory

# Cleanup all the files older than a week
- cleanup_files: 
      path_pattern: /tmp/*.log
      state: absent
      age: 1w

# Cleanup files in a path excluding patterns foo and bar
- cleanup_files:
      path_pattern: /tmp/*.log
      state: absent
      excludes:
        - foo*
        - bar*

# Cleanup files based on files larger than 5 GB
- cleanup_files:
      path_pattern: /tmp/*.log
      state: absent
      size: 5g
'''
RETURN = '''
files:
    description: The list of files to be deleted
    type: list
matched: 
    description: The numer of files matching the criteria
    type: str
msg: 
    description: The comment of action which has taken place
    type: str
'''

#!/usr/bin/env python
import os
import glob
import operator
import re
import stat
import time
import shutil
import fnmatch

from ansible.module_utils.basic import AnsibleModule

def list_files(path_pattern):
    '''list file in the path_pattern'''
    for file in sorted(glob.glob(path_pattern)):
        yield file

def filter_with_excludes(filelist,excludes):
    '''filter files excluding some based on pattern'''
    for pattern in excludes:
        excluded_files = [file for file in filelist if fnmatch.fnmatch(os.path.basename(file), pattern)]
        filelist = list(set(filelist) - set(excluded_files))
    return filelist

def agefilter(st, now, age, timestamp):
    '''filter files older than age'''
    if age is None:
        return True
    elif age >= 0 and now - st.__getattribute__("st_%s" % timestamp) >= abs(age):
        return True
    elif age < 0 and now - st.__getattribute__("st_%s" % timestamp) <= abs(age):
        return True
    return False


def sizefilter(st, size):
    '''filter files greater than size'''
    if size is None:
        return True
    elif size >= 0 and st.st_size >= abs(size):
        return True
    elif size < 0 and st.st_size <= abs(size):
        return True
    return False

def file_type_filter(st, file_type):
    '''filter files if same file_type'''
    if file_type == 'any':
        return True
    elif operator.getitem(statinfo(st),'isdir') and file_type == "directory":
        return True
    elif operator.getitem(statinfo(st),'isreg') and file_type == "file":
        return True
    else:
        return False

def statinfo(st):
    return {
        'mode': "%04o" % stat.S_IMODE(st.st_mode),
        'isdir': stat.S_ISDIR(st.st_mode),
        'ischr': stat.S_ISCHR(st.st_mode),
        'isblk': stat.S_ISBLK(st.st_mode),
        'isreg': stat.S_ISREG(st.st_mode),
        'isfifo': stat.S_ISFIFO(st.st_mode),
        'islnk': stat.S_ISLNK(st.st_mode),
        'issock': stat.S_ISSOCK(st.st_mode),
        'uid': st.st_uid,
        'gid': st.st_gid,
        'size': st.st_size,
        'inode': st.st_ino,
        'dev': st.st_dev,
        'nlink': st.st_nlink,
        'atime': st.st_atime,
        'mtime': st.st_mtime,
        'ctime': st.st_ctime,
        'wusr': bool(st.st_mode & stat.S_IWUSR),
        'rusr': bool(st.st_mode & stat.S_IRUSR),
        'xusr': bool(st.st_mode & stat.S_IXUSR),
        'wgrp': bool(st.st_mode & stat.S_IWGRP),
        'rgrp': bool(st.st_mode & stat.S_IRGRP),
        'xgrp': bool(st.st_mode & stat.S_IXGRP),
        'woth': bool(st.st_mode & stat.S_IWOTH),
        'roth': bool(st.st_mode & stat.S_IROTH),
        'xoth': bool(st.st_mode & stat.S_IXOTH),
        'isuid': bool(st.st_mode & stat.S_ISUID),
        'isgid': bool(st.st_mode & stat.S_ISGID),
    }
    
def delete_files(filelist):
    for file in filelist:
        if os.path.islink(file):
            os.unlink(file)
        elif os.path.isdir(file):
            shutil.rmtree(file)
        else:
            os.remove(file)

def main():
    module = AnsibleModule(
        argument_spec=dict(
            path_pattern=dict(type='list', required=True, aliases=['name', 'path']),
            state=       dict(type='str', default='list', choices=['list', 'absent']),
            excludes=    dict(type='list', aliases=['exclude']),
            file_type=   dict(type='str', default="any", choices=['any', 'directory', 'file', 'link']),
            age=         dict(type='str', default=None),
            age_stamp=   dict(type='str', default="mtime", choices=['atime', 'mtime', 'ctime']),
            size=        dict(type='str', default=None),
        ),
        supports_check_mode=True,
    )

    params = module.params
    filelist = []

    if params['age'] is None:
        age = None
    else:
        # convert age to seconds:
        m = re.match(r"^(-?\d+)(s|m|h|d|w)?$", params['age'].lower())
        seconds_per_unit = {"s": 1, "m": 60, "h": 3600, "d": 86400, "w": 604800}
        if m:
            age = int(m.group(1)) * seconds_per_unit.get(m.group(2), 1)
        else:
            module.fail_json(age=params['age'], msg="failed to process age")

    if params['size'] is None:
        size = None
    else:
        # convert size to bytes:
        m = re.match(r"^(-?\d+)(b|k|m|g|t)?$", params['size'].lower())
        bytes_per_unit = {"b": 1, "k": 1024, "m": 1024**2, "g": 1024**3, "t": 1024**4}
        if m:
            size = int(m.group(1)) * bytes_per_unit.get(m.group(2), 1)
        else:
            module.fail_json(size=params['size'], msg="failed to process size")

    now = time.time()
    msg = ''
    for npath in params['path_pattern']:
        for fsname in list_files(npath):
            try:
                st = os.lstat(fsname)
            except Exception:
                msg += "%s was skipped as it does not seem to be a valid file or it cannot be accessed\n" % fsname
                continue
            # Filter based on size, age and file_type
            if agefilter(st, now, age, params['age_stamp']) and sizefilter(st, size) and file_type_filter(st, params['file_type']):
                filelist.append(fsname)
            else:
                continue
    
    # Filter based on excludes
    if params['excludes'] and len(params['excludes']) > 0:
        filelist = filter_with_excludes(filelist, params['excludes'])  
    
    # Caluclate total matched files
    matched = len(filelist)
    
    # Handle check_mode
    if module.check_mode == True:
        if matched == 0:
            msg = "No files matched to delete"
        else:
            msg = "The files will be deleted"
        module.exit_json(msg=msg,files=filelist, changed=False, matched=matched)
        
    if matched == 0:
        msg = "No files matched to delete"
        module.exit_json(msg=msg, files=filelist, changed=False, matched=matched)
    elif matched > 0 and params['state'] == 'list':
        msg = "The files will be deleted"
        module.exit_json(msg=msg, files=filelist, changed=False, matched=matched)
    elif matched > 0 and params['state'] == 'absent':
        delete_files(filelist)
        msg = "The files are deleted"
        module.exit_json(msg=msg, files=filelist, changed=True, matched=matched)
    else:
        msg = "Failed to receive valid parameters"
        module.exit_json(msg=msg)
# Execute the main function
if __name__ == '__main__':
    main()
