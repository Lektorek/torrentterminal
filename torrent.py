#!/usr/bin/env python2.7
import warnings
warnings.filterwarnings('ignore')
import libtorrent as lt
import time
import sys
from hurry.filesize import size
import os
import datetime
from tqdm import tqdm
import hashlib
import argparse

class bcolors:
	HEADER = '\033[95m'
	OKBLUE = '\033[94m'
	OKGREEN = '\033[92m'
	WARNING = '\033[93m'
	FAIL = '\033[91m'
	ENDC = '\033[0m'
	BOLD = '\033[1m'
	UNDERLINE = '\033[4m'

# BUF_SIZE is totally arbitrary, change for your app!
def hashfile(file):
	BUF_SIZE = 65536  # lets read stuff in 64kb chunks!

	md5 = hashlib.md5()
	sha1 = hashlib.sha1()

	with open(file, 'rb') as f:
	    while True:
	        data = f.read(BUF_SIZE)
	        if not data:
	            break
	        md5.update(data)
	        sha1.update(data)

	print("MD5: {0}".format(md5.hexdigest()))
	print("SHA1: {0}".format(sha1.hexdigest()))

def sizeof_fmt(num, suffix='B'):
	for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
		if abs(num) < 1024.0:
			return '%3.1f %s%s' % (num, unit, suffix)
		num /= 1024.0
	return "%.1f%s%s" % (num, 'Yi', suffix)

def help():
	print ''
	print 'Usage: ./torrent.py [OPTIONS]    <.torrent file>    <save_directory (home default)>' + bcolors.ENDC
	print ''
	print 'Optons:'
	print '-i, --info	: Info about .torrent file'
	print '-h, --help	: This help window'
	print ''
	exit()

def notorrent():
	print ''
	print bcolors.BOLD+bcolors.FAIL+'[-] Wrong .torrent file.'+bcolors.ENDC
	print ''
	exit()

def nodir():
	print ''
	print bcolors.BOLD+bcolors.FAIL+'[-] Wrong directory to save torrent.'+bcolors.ENDC
	print ''
	exit()

def info():

	info = lt.torrent_info(args.torrent)
	print ''
	print bcolors.HEADER+'Torrent info:\n\n', 'Total size:	', sizeof_fmt(info.total_size()), '\nCreator:	', info.creator(),'\nName:	', info.name(), '\nFiles:',
	i = 0
	while (i < info.files().num_files()):
		print '	', info.files().file_path(i)
		i += 1
	print ''
	hashfile(args.torrent)
	print '' + bcolors.ENDC
	exit()


try:
	parser = argparse.ArgumentParser()
	parser.add_argument('-i', '--info', help='Info about .torrent file', action='store_true')
	parser.add_argument('-s', '--save', help='File save path', default=os.getenv('HOME'))
	parser.add_argument('torrent', help='Path to .torrent file')
	if len (sys.argv)==1:
		parser.print_help()
		parser.exit(1)
	args=parser.parse_args()

	#if not sys.argv[1]:
	#	help()

	#	warnings.warn('torrent file not found')
	#	exit()
	#for argv in sys.argv:
	#if argv == '--help' or argv == '-h':
	#	help()
	if args.info :
		info()

	ses = lt.session()
	ses.listen_on(6881, 6891)

	info = lt.torrent_info(args.torrent)

	#if len(sys.argv) < 3:
		#h = ses.add_torrent({'ti': info, 'save_path': os.getenv('HOME')})
	#	save_path = os.getenv('HOME')
	#else:
	#	if os.path.isdir(sys.argv[2]):
	#		save_path = sys.argv[2]
	#	else:
	#		nodir()

	h = ses.add_torrent({'ti': info, 'save_path': args.save})

	print bcolors.OKGREEN + '[+] starting', h.name() + bcolors.ENDC

	print ''
	print bcolors.HEADER+'Torrent info:\n\n', 'Total size: ', sizeof_fmt(info.total_size()), '\nCreator: ', info.creator(),\
	 '\nSave patch: ', args.save+'/'+info.name(), '\nName:	'+info.name(),  '\nFiles:',
	i = 0
	while (i < info.files().num_files()):
		print '	', info.files().file_path(i)
		i += 1
	print ''
	hashfile(args.torrent)
	print '' + bcolors.ENDC

	while (not h.is_seed()):
		s = h.status()

		state_str = ['queued', 'checking', 'downloading metadata', \
		'downloading', 'finished', 'seeding', 'allocating', 'checking fastresume']
		print bcolors.BOLD + '\r%.2f%% complete (down: %.1f kB/s up: %.1f kB/s peers: %d ETA: %s) %s' % \
		(s.progress * 100, s.download_rate / 1000, s.upload_rate / 1000, \
		s.num_peers, str(datetime.timedelta(seconds=((s.total_wanted-s.total_wanted_done) / s.download_rate ))) if (s.download_rate > 0) else u"\u221E", \
		state_str[s.state]) + bcolors.ENDC,
		sys.stdout.flush()

		time.sleep(1)

	print bcolors.OKGREEN + '\n[+] ' + h.name(), 'complete' + bcolors.ENDC

except KeyboardInterrupt:
	print ''
	print bcolors.OKBLUE + 'Bye!' + bcolors.ENDC
	exit()
#except IndexError:
#	help()

#except RuntimeError:
#	notorrent()
