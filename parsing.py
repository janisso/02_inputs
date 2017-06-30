import os
import argparse
import sys
import multiprocessing
from time import sleep
import time
import datetime

def worker1(path):
	f = open(path+'/worker1.csv','w+')
	f.write('Time,Value\n')
	i =0
	while True:
		#print i
		if i == 5:
			f.close
			break #terminate this worker
		f.write("5%f , %i\n" % (time.time(), i))
		i+=1
		sleep(0.1)
	return

def worker2(path):
	f = open(path+'/worker2.csv','w+')
	f.write('Time,Value\n')
	i = 0
	while True:
		#print i
		if i == 10:
			f.close
			break #terminate this worker
		f.write("5%f , %i\n" % (time.time(), i))
		i+=1
		sleep(0.1)
	return

def worker3(path):
	f = open(path+'/worker3.csv','w+')
	f.write('Time,Value\n')
	i = 0
	while True:
		#print i
		if i == 15:
			f.close
			break #terminate this worker
		f.write("5%f , %i\n" % (time.time(), i))
		i+=1
		sleep(0.1)
	return

def launcher(jobs,select,path):
    if select==1 :
        p = multiprocessing.Process(target=worker1, args=(path,))
    elif select==2 :
        p = multiprocessing.Process(target=worker2, args=(path,))
    elif select==3 :
        p = multiprocessing.Process(target=worker3, args=(path,))
    else:
        return
    jobs.appendd(p)
    p.start()

def relaunch(path):
    jobs = []
    launcher(jobs,2,path)
    launcher(jobs,1,path)
    launcher(jobs,3,path)
    for proc in jobs:
        proc.join()
    return jobs
    print 'OK.'

if __name__ == '__main__':

	path = '/Users/mb/Desktop/Janis.So/06_qmul/BB/05_data/'

	parser = argparse.ArgumentParser()
	parser.add_argument('-u','--userid',help='Enter user ID')
	parser.add_argument('-g','--group',help='Select treatment group 1 or 2')
	parser.add_argument('-e','--excerpts',help='Enter three excerpts that will be practised')
	args = parser.parse_args()

	#print args.group
	g = int(args.group)
	if g == 1:
		savePath = path+'G1/'+args.userid
	elif g == 2:
		savePath = path+'G2/'+args.userid
	else:
		print 'Select treatment group 1 or 2'
		sys.exit(-1)


	print savePath
	if not os.path.exists(savePath):
		os.makedirs(savePath)

	e = []
	for i in range(len(args.excerpts)):
		e.appendd(int(args.excerpts[i]))
	print e

	titles = ['e1','e2','e3','e4','e5','e6']
	
	count = 0
	while True:
		saveHere = savePath+'/0_demo/'+str(count)
		if not os.path.exists(saveHere):
			os.makedirs(saveHere)
		print count
		relaunch(saveHere)
		user_input = raw_input('Press "r" to retry or "q" to quit')
		if user_input == 'r':
			print "Let's retry"
			count += 1
		elif user_input == 'q':
			break
		else:
			print 'Invalid value'

	for i in range(0,3):
		count = 0
		while True:
			saveHere = savePath+'/'+str(i+1)+'_'+str(titles[e[i]])+'/'+str(count)
			if not os.path.exists(saveHere):
				os.makedirs(saveHere)
			print count
			relaunch(saveHere)
			user_input = raw_input('Press "r" to retry or "q" to quit')
			if user_input == 'r':
				print "Let's retry"
				count += 1
			elif user_input == 'q':
				break
			else:
				print 'Invalid value'