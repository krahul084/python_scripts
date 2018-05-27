#!/usr/bin/python
import getpass,sys,os, subprocess

#Loading Existing Data for validating input
def load_data():
    with open('/var/yp/data/passwd') as f:
       lines=f.read().splitlines()
    check_username = [i.split(':')[0] for i in lines]
    check_uid = [i.split(':')[2] for i in lines]
    check_home = [i.split(':')[5] for i in lines]
    check_filer = os.listdir('/net/vnx_01')
    return check_username, check_uid, check_home, check_filer

#Gathering User Information
def gather_info():
	username = raw_input('Please enter username(Within 8 chars): ')
	password = getpass.getpass('Please enter password: ')
	gid = raw_input('Enter GID: ')
	description = raw_input('Please enter user description: ')
	filer = raw_input("Please enter the VNX filer for home_directory: ")
	return username, password, gid, description, filer


def validate_info(username, password, uid, gid, filer):
    check_username, check_uid, check_home, check_filer = load_data()

    print "***Validating the Input Provided!***"
    #Validate Username
    if username == None:
    	print "Username Not Provided!"
    	sys.exit(1)
    elif len(username) > 8:
    	print "Username exceeds 8 characters!"
    	sys.exit(2)
    elif type(username) != str:
        print "Please enter username in string!"
        sys.exit(3)
    elif username in check_username:
    	print "Username already exists!"
    	sys.exit(4)
    else:
    	print "Validated Username!"

    #Validate Password
    if (len(password) > 8) and (password.isalnum() == True):
        print "Validated Password!"
    else:
        print "Invalid Password, Please enter password more than 8 chars and should be alphnumeric!"
        sys.exit(5)

    #Validate GID
    if (type(gid) != int ):
    	print "Invalid GID"
    	sys.exit(6)
    else:
    	print "Validated GID"

    #Validate Filer
    if filer not in check_filer:
        print "Entered filer doesn't exist"
        sys.exit(7)
    else:
        print "Validated Filer"


def create_home(username, uid, gid, home_abs_path):
    if username in os.listdir(home_abs_path):
        print 'Home Directory Already Exists, Please Troubleshoot'
        sys.exit(8)
    else:
        os.mkdir(home_abs_path+username)
        os.chown(home_abs_path+username, uid, gid)
        os.chdir(home_abs_path+username)
        ret = subprocess.call("/net/ns80/fs000/MK_NEW_USR", shell=True)
        if ret == 0:
            print 'Successfully created the home directory: %s in path: %s' % (username,home_abs_path)
        else:
            print "Problem in creating home directory %s, Please verify manually" %  home_abs_path+username
            sys.exit(9)

def update_passwd(username, password, uid, gid, description, home_dir, shell):
    entries = [username, password, uid, gid, description, home_dir, shell ]
    entries = map(str,entries)
    passwd_entry = ':'.join(entries)
    with open('/var/yp/data/passwd','a') as f:
        f.write(passwd_entry+"\n")
    if username in open('/var/yp/data/passwd','r').read():
        print '***Updated Passwd File***'
    else:
        print 'Password file not updated, Please Troubleshoot'
        sys.exit(10)


def update_auto_home(username, home_perm, home_filer):
    entries = [username, home_perm, home_filer]
    auto_home_entry = '\t'.join(entries)
    with open('/var/yp/data/autohome.roc','a') as f:
        f.write(auto_home_entry+"\n")
    if username in open('/var/yp/data/autohome.roc','r').read():
        print '***Updated Auto_Home***'
    else:
        print 'Auto_home File not updated, Please Troubleshoot!'
        sys.exit(11)
    

if __name__ == '__main__':
    #Assigning Gathered Information
	username, password, gid, description, filer = gather_info()
	check_username, check_uid, check_home, check_filer = load_data()
	home_dir = '/home/'+username
	home_abs_path = '/net/vnx_01/'+filer+'/home/'
	shell = '/bin/tcsh'
	uid = map(int,check_uid)
	uid = max(uid) + 1
        gid = int(gid)
	home_perm = '-nosuid,rw'
	home_filer = 'vnx_01:/%s/home/&' % filer
        #Actual Implementation 
        print 'Please Review Below information: '
        print 'Username:\t%s\nGID:\t\t%d\nDescription:\t%s\nFiler:\t\t%s\n' % (username, gid, description, filer)
        confirmation = raw_input('Hit(Y/y) to commit! ')
        if confirmation == 'Y' or confirmation == 'y':
            validate_info(username, password, uid, gid, filer)  
            create_home(username, uid, gid, home_abs_path) 
            update_passwd(username, password, uid, gid, description, home_dir, shell) 
            update_auto_home(username, home_perm, home_filer)
            print 'Successfully Created User-%s' % username
        else:
            print 'Exiting on request' 
            sys.exit(12)
