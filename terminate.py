import multiprocessing
from time import sleep


class countNumbers(multiprocessing.Process):

	def __init__(self,c):
		multiprocessing.Process.__init__(self)
		self.exit = multiprocessing.Event()
		self.i = 0
		self.counter = c

	def run(self):
		while not self.exit.is_set():
			print self.i
			if self.i == 50:
				print 'countNumbers i = 0'
				self.i = 0
				pill.value = 1
				p2.start()
				print pill.value
			i+=1
			sleep(self.counter)
			pass
			slef.exit.set()
        print "You exited!"

    # def shutdown(self):
    #     print "Shutdown initiated"
    #     self.exit.set()






def countNumbers(pill):
	while True:
		print i
		if i == 50:
			print 'countNumbers i = 0'
			i = 0
			pill.value = 0
			p2.start()
		i+=1
		sleep(0.1)



def countNumbers2(pill):
	print 'countNumber2 started'
	i=0
	while True:
		print i
		if i == 50:
			print 'exiting'
			self.terminate()
			pill.value = 1
		i+=1
		sleep(0.05)





#def checkFlags(var):
#	while True:
#		if var.value == 1:





if __name__ == "__main__":
	print 'yo'
	pill = multiprocessing.Value('i',0)
	#p1 = countNumbers(0.05)
	#p1.start()
	p1 = multiprocessing.Process(target=countNumbers,args=(pill,))
	p2 = multiprocessing.Process(target=countNumbers2,args=(pill,))

	p1.start()
	p2.start()
	p1.join()
	p2.join()

	# while True:
	# 	print pill.value
	# 	if pill.value == 0:
	# 		#p1.start()
	# 		p2.start()
	# 		#p1.join()
	# 		p2.join()
	# 	if pill.value == 1:
	# 		#p1.terminate()
	# 		p2.terminate()