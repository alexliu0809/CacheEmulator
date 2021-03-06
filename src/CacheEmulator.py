"""
Cache Emulator
Author: Alex Enze Liu
Date: 01/23/2018
Class: Computer Architecture
"""

import numpy as np
import argparse
import math
from time import time
from copy import deepcopy

conf = None #Save Running Configuration
logging = None #Save Stats

class Logging():
	def __init__(self):
		
		self.instruction_cnt = 0
		self.read_hits = 0
		self.read_misses = 0
		self.write_hits = 0
		self.write_misses = 0
		self.log_flag = False

	def log(self,log_type):
		if self.log_flag == False:
			return 

		if log_type == "read_hits":
			self.read_hits += 1

		elif log_type == "instruction_cnt":
			self.instruction_cnt += 1

		elif log_type == "read_misses":
			self.read_misses += 1

		elif log_type == "write_hits":
			self.write_hits += 1

		elif log_type == "write_misses":
			self.write_misses += 1

		else:
			raise Exception("Unknown log_type {}".format(log_type))

	def on(self):
		#Turn on logging
		self.log_flag = True

	def off(self):
		#Turn off logging
		self.log_flag = False

	def __repr__(self):
		#Print, for debug
		return "\t".join(["{}:{}".format(attr,value)for attr, value in self.__dict__.items()]) + "\n"

class Configuration():

	def __init__(self, cache_size, block_size, associativity, replacement, algorithm):
		#Global Variable Recording configurations

		self.size_of_double = 8 #8 bytes each double

		self.block_size = block_size # Bytes of a data block
		
		self.cache_size = cache_size #cache size
		self.ram_size = 1024 * 1024 * 64 

		self.blocks_in_cache = int(cache_size / block_size) # # of blocks in cache
		
		# Here we assume RAM size 64MB
		self.blocks_in_RAM = int(self.ram_size / block_size) # Assuming RAM is way larger than cache.

		self.associativity = associativity
		self.num_of_sets = int(self.blocks_in_cache / associativity)

		self.replacement = replacement 
		self.algorithm = algorithm

	def __repr__(self):
		
		return "\t".join(["{}:{}".format(attr,value)for attr, value in self.__dict__.items()]) + "\n"


class Address():
	#An Address Specified By An Integer (I.e. Byte Address).
	def __init__(self, address):

		if type(address) != int:
			raise Exception("Address Initialization Should Be Int")

		self.address = address
		self.conf = conf

	def getTag(self):
		#The upper bits for Tagging
		return self.address // (conf.block_size * conf.num_of_sets)

	def getIndex(self):
		#Treat address as double number. ie. the nth double
		#Block Number = floor(Address / block_size) -- block_size means number of doubles
		#set number (index) = Block Number % number_of_sets
		#Log2(num_of_sets) bits for indexing
		return (self.address // conf.block_size) % conf.num_of_sets

	def getOffset(self):
		#The lowest log2(block_size) bits for block offset.
		return self.address % conf.block_size

	def __mod__(self,p2):
		if type(p2) != int:
			raise Exception("type(p2) != int")

		return self.address % p2

	def __floordiv__(self,p2):
		if type(p2) != int:
			raise Exception("type(p2) != int")

		return self.address // p2



class DataBlock():
	#DataBlock contains a data block; 
	#in this implementation, the data is an array of doubles
	def __init__(self):

		if conf.block_size % conf.size_of_double != 0:
			raise Exception("conf.block_size %% conf.size_of_double != 0:")

		self.num_of_doubles = conf.block_size // conf.size_of_double
		self.data = np.zeros(self.num_of_doubles, dtype=np.float);

		#The Time It's Last Visited By CPU
		self.last_visited_time = None

		#The Time It's Recent Loaded Into Cache
		self.last_loaded_time = None

	def __repr__(self):
		return repr(self.data) + "\n"

	def getDouble(self,key):
		#return the double at address

		if key % 8 != 0:
			raise Exception("Setting Double Should Use Start Address")

		if int(key/8) >= len(self.data):
			raise Exception("Indexing Outside Block")

		return self.data[int(key/8)]

	def setDouble(self,key,val):
		#set the double at address
		if key % 8 != 0:
			raise Exception("Setting Double Should Use Start Address")

		if int(key/8) >= len(self.data):
			raise Exception("Indexing Outside Block")

		self.data[int(key/8)] = val

	def set_last_visited_time(self,time):
		self.last_visited_time = time

	def set_last_loaded_time(self,time):
		self.last_loaded_time = time

class CPU():
	def __init__(self):
		self.cache = Cache()

	def getDouble(self,address):
		#Load a double from cache.
		if address % 8 != 0:
			raise Exception("Loading Double Should Use Start Address")

		logging.log("instruction_cnt")
		return self.cache.getDouble(address)

	def setDouble(self, address, value):
		if address % 8 != 0:
			raise Exception("Storing Double Should Use Start Address")

		logging.log("instruction_cnt")
		self.cache.setDouble(address, value)

	def addDouble(self,val1, val2):
		logging.log("instruction_cnt")
		return val1 + val2

	def multDouble(self, val1, val2):
		logging.log("instruction_cnt")
		return val1 * val2

class Cache():
	def __init__(self):
	
		self.blocks_per_set = conf.associativity;
		self.num_of_sets = conf.num_of_sets;
		self.blocks = [[DataBlock() for j in range(self.blocks_per_set)] for i in range(self.num_of_sets)]
		self.valid = [[False for j in range(self.blocks_per_set)] for i in range(self.num_of_sets)]
		self.tags = [[0 for j in range(self.blocks_per_set)]for i in range(self.num_of_sets)]
		self.ram = RAM()
		self.conf = conf

	def getDouble(self,address):
		global logging
		# See if the block this double belongs to is in cache.
		
		#Search In Corresponding Set (Theoratically In Parallel) and See If the Block exists
		find_block_result = self.find_block_in_cache(address)
		#print("Finding Block {}".format(find_block_result))
		# If the current block in cache, return the double from the block.
		if find_block_result != None:
			logging.log("read_hits")
			find_block_result.set_last_visited_time(time())
			return find_block_result.getDouble(address.getOffset())

		# Otherwise load the block into cache and return the block
		else:
			logging.log("read_misses")
			return self.load_block_from_ram(address).getDouble(address.getOffset())

	def setDouble(self, address, val):
		#The same as getDouble except that it sets value here.
		global logging
		#Search In Corresponding Set (Theoratically In Parallel) and See If the Block exists
		find_block_result = self.find_block_in_cache(address)
		#print("Finding Block {}".format(find_block_result))
		# If the current block in cache, return the double from the block.
		if find_block_result != None:
			logging.log("write_hits")
			find_block_result.set_last_visited_time(time())
			find_block_result.setDouble(address.getOffset(),val)

		# Otherwise load the block into cache and return the block
		else:
			logging.log("write_misses")
			self.load_block_from_ram(address).setDouble(address.getOffset(),val)

	def load_block_from_ram(self, address):
		#Retrieve datablock from RAM if not in cache and place in cache.

		#print("load_block_from_ram")

		current_time = time()

		#block = deepcopy(self.ram.getBlock(address))
		#If you don't use deepcopy here, then it returns the references, and it's automatically write-through with write-back
		block = self.ram.getBlock(address)
		#print("Block Retrieved {}".format(block))

		block.set_last_loaded_time(current_time)
		block.set_last_visited_time(current_time)

		set_index_of_address = address.getIndex()

		for block_idx in range(self.blocks_per_set):
			# If there's space in the corresponding set
			if self.valid[set_index_of_address][block_idx] == False:
				self.valid[set_index_of_address][block_idx] = True
				self.tags[set_index_of_address][block_idx] = address.getTag()
				self.blocks[set_index_of_address][block_idx] = block
				return block

		#If there's no space in the corresponding set
		#Perform replace algo.
		if self.conf.replacement == "LRU":
			#print("LRU")

			lru_index = None

			for block_idx in range(self.blocks_per_set):
				# If there's no space in the corresponding set. Then valid bit are all True

				#Find lru index
				lru_index = block_idx if lru_index == None or self.blocks[set_index_of_address][block_idx].last_visited_time < self.blocks[set_index_of_address][lru_index].last_visited_time else lru_index

			#write back ignored because ram and cache referring to same instance. -- auto write back

			#Replace it with new one
			self.tags[set_index_of_address][lru_index] = address.getTag() #Set Tag
			self.blocks[set_index_of_address][lru_index] = block #Set Block

		elif self.conf.replacement == "random":
			rand_evict_idx = np.random.randint(self.blocks_per_set) #Randomly evict one 

			#write back ignored because ram and cache referring to same instance. -- auto write back

			#Replace it with new one
			self.tags[set_index_of_address][rand_evict_idx] = address.getTag() #Set Tag
			self.blocks[set_index_of_address][rand_evict_idx] = block #Set Block

		elif self.conf.replacement == "FIFO":
			fifo_index = None

			for block_idx in range(self.blocks_per_set):
				# If there's no space in the corresponding set. Then valid bit are all True

				#Find lru index
				fifo_index = block_idx if fifo_index == None or self.blocks[set_index_of_address][block_idx].last_visited_time < self.blocks[set_index_of_address][fifo_index].last_visited_time else fifo_index

			#write back ignored because ram and cache referring to same instance. -- auto write back
			
			#Replace it with new one
			self.tags[set_index_of_address][fifo_index] = address.getTag() #Set Tag
			self.blocks[set_index_of_address][fifo_index] = block #Set Block

		else:
			raise Exception("Unknown Replacement Type")

		return block

	"""
	def mapped_set_full(self,address):
		# A Block is mapped to a set (set size 1 - xxx)
		# If All space is occupied in the set, return True
		# Else return false
		set_index_of_address = address.getIndex()

		for block_idx in len(self.blocks[set_index_of_address]):
			if self.valid[set_index_of_address][block_idx] == False:
				return False

		return True
	"""

	def find_block_in_cache(self,address):
		#See if the block is in cache

		set_index_of_address = address.getIndex()
		tag_of_address = address.getTag()

		for block_idx in range(self.blocks_per_set):

			if self.valid[set_index_of_address][block_idx] == True and self.tags[set_index_of_address][block_idx] == tag_of_address:

				return self.blocks[set_index_of_address][block_idx]

		return None

	def __repr__(self):
		#For debug
		string = "Cache Status:\n" 
		for j in range(self.blocks_per_set):
			for i in range(self.num_of_sets):
				string += str(self.blocks[i][j])
		return string


class RAM():
	def __init__(self):

		self.blocks_in_RAM = conf.blocks_in_RAM
		self.data = [DataBlock() for i in range(self.blocks_in_RAM)]
		self.conf = conf

	def getBlock(self, address):
		if address % 8 != 0:
			raise Exception("Storing Double Should Use Start Address")

		return self.data[address // self.conf.block_size]

	def setBlock(self):
		#write back ignored because ram and cache referring to same instance. -- auto write back
		pass

	def __repr__(self):
		#For Debug
		return "RAM Status:\n"+"Number of Blocks In Ram:{}\n".format(self.blocks_in_RAM)+"Data:\n{}\n".format(self.data)


def dot():
	#Dot operation
	
	myCPU = CPU()

	### Initialize Three Arrays
	n = 20000
	a = [Address(i * 8) for i in range(0,n)]
	b = [Address(i * 8) for i in range(n,2*n)]
	c = Address(2 * n * 8)

	### Set Array Val Without Interfering Cache
	doubles_per_block = conf.block_size // conf.size_of_double
	for i in range(n):
		#print(a[i].address)
		myCPU.cache.ram.data[a[i]//conf.block_size].data[(a[i]//conf.size_of_double)%doubles_per_block] = 1 * i
		myCPU.cache.ram.data[b[i]//conf.block_size].data[(b[i]//conf.size_of_double)%doubles_per_block] = 2 * i
		#myCPU.cache.ram.data[c[i]//conf.block_size].data[(c[i]//conf.size_of_double)%doubles_per_block] = 3 * i
	
	#print(myCPU.cache.ram.data[:376]
	#print(myCPU.cache)
	#print(myCPU.cache.ram)


	#Start Simulation
	logging.on()
	register0 = 0
	for i in range(n):
		register1 = myCPU.getDouble(a[i])
		register2 = myCPU.getDouble(b[i])
		register3 = myCPU.multDouble(register1,register2)
		register0 = myCPU.addDouble(register0,register3)
	myCPU.setDouble(c, register0)
	logging.off()
	#End Simulation

	#Debug
	#register1 = myCPU.getDouble(Address(0 * 8))
	#register1 = myCPU.getDouble(Address(8 * 8))
	#register1 = myCPU.getDouble(Address(0 * 8))
	#register1 = myCPU.getDouble(Address(6 * 8))
	#register1 = myCPU.getDouble(Address(8 * 8))

	
	#Double Checking Dot Result
	val1 = myCPU.cache.ram.data[c//conf.block_size].data[(c//conf.size_of_double)%doubles_per_block]
	cnt = 0
	for i in range(n):
		cnt += myCPU.cache.ram.data[a[i]//conf.block_size].data[(a[i]//conf.size_of_double)%doubles_per_block] * myCPU.cache.ram.data[b[i]//conf.block_size].data[(b[i]//conf.size_of_double)%doubles_per_block]
	if cnt != val1:
		raise Exception("Dot Error")



def mxm():
	#see the book for algorithm
	myCPU = CPU()

	x = y = z = 100

	### Initialize Three Arrays With Address
	a = [Address(i * 8) for i in range(x*y)] # x * y
	b = [Address(i * 8) for i in range(x*y,x*y+y*z)] #y * z
	c = [Address(i * 8) for i in range(x*y+y*z,x*y+y*z+x*z)] #x * z

	### Set Array Val Without Interfering Cache
	doubles_per_block = conf.block_size // conf.size_of_double
	for i in range(x*y):
		myCPU.cache.ram.data[a[i]//conf.block_size].data[(a[i]//conf.size_of_double)%doubles_per_block] = i
	for i in range(y*z):
		myCPU.cache.ram.data[b[i]//conf.block_size].data[(b[i]//conf.size_of_double)%doubles_per_block] = i
	for i in range(x*z):
		myCPU.cache.ram.data[c[i]//conf.block_size].data[(c[i]//conf.size_of_double)%doubles_per_block] = i
	#print(myCPU.cache.ram.data[:376]

	#Start Simulation
	logging.on()
	for i in range(x):
		for j in range(z):
			Cij = myCPU.getDouble(c[i * z + j])
			for k in range(y):
				Aik = myCPU.getDouble(a[i * y + k])
				Bkj = myCPU.getDouble(b[k * z + j])
				tmp = myCPU.multDouble(Aik,Bkj)
				Cij = myCPU.addDouble(Cij,tmp)
			myCPU.setDouble(c[i * z + j],Cij)
	logging.off()
	#End Simulation

	#Double Checking Dot Result
	for i in range(x):
		for j in range(z):
			Cij = i * z + j
			for k in range(y):
				Aik = myCPU.cache.ram.data[a[i * y + k]//conf.block_size].data[(a[i * y + k]//conf.size_of_double)%doubles_per_block]
				Bkj = myCPU.cache.ram.data[b[k * z + j]//conf.block_size].data[(b[k * z + j]//conf.size_of_double)%doubles_per_block]
				Cij += Aik * Bkj
			if Cij != myCPU.cache.ram.data[c[i * z + j]//conf.block_size].data[(c[i * z + j]//conf.size_of_double)%doubles_per_block]:
				raise Exception("Error, Result Doesn't Match")
			

def mxm_block():
	#see the book for algorithm

	myCPU = CPU()

	x = y = z = 100

	mxm_block_size = int(x / 10)
	doubles_per_block = conf.block_size // conf.size_of_double
	### Initialize Three Arrays With Address
	a = [Address(i * 8) for i in range(x*y)] # x * y
	b = [Address(i * 8) for i in range(x*y,x*y+y*z)] #y * z
	c = [Address(i * 8) for i in range(x*y+y*z,x*y+y*z+x*z)] #x * z

	### Set Array Val Without Interfering Cache
	for i in range(x*y):
		myCPU.cache.ram.data[a[i]//conf.block_size].data[(a[i]//conf.size_of_double)%doubles_per_block] = i
	for i in range(y*z):
		myCPU.cache.ram.data[b[i]//conf.block_size].data[(b[i]//conf.size_of_double)%doubles_per_block] = i
	for i in range(x*z):
		myCPU.cache.ram.data[c[i]//conf.block_size].data[(c[i]//conf.size_of_double)%doubles_per_block] = i

	#Start Simulation
	logging.on()
	for sj in range(0,z,mxm_block_size):
		for si in range(0,x,mxm_block_size):
			for sk in range(0,y,mxm_block_size):
				for i in range(si,si+mxm_block_size):
					for j in range(sj,sj+mxm_block_size):
						Cij = myCPU.getDouble(c[i * z + j])
						for k in range(sk,sk+mxm_block_size):
							Aik = myCPU.getDouble(a[i * y + k])
							Bkj = myCPU.getDouble(b[k * z + j])
							tmp = myCPU.multDouble(Aik,Bkj)
							Cij = myCPU.addDouble(Cij,tmp)
						myCPU.setDouble(c[i * z + j],Cij)
	logging.off()

	#Double Checking Dot Result
	for i in range(x):
		for j in range(z):
			Cij = i * z + j
			for k in range(y):
				Aik = myCPU.cache.ram.data[a[i * y + k]//conf.block_size].data[(a[i * y + k]//conf.size_of_double)%doubles_per_block]
				Bkj = myCPU.cache.ram.data[b[k * z + j]//conf.block_size].data[(b[k * z + j]//conf.size_of_double)%doubles_per_block]
				Cij += Aik * Bkj
			if Cij != myCPU.cache.ram.data[c[i * z + j]//conf.block_size].data[(c[i * z + j]//conf.size_of_double)%doubles_per_block]:
				raise Exception("Error, Result Doesn't Match")
			


def main(args):
	global conf,logging

	np.random.seed(0) #For repetibility 

	conf = Configuration(args.cache_size, args.block_size, args.associativity, args.replacement, args.algorithm)
	logging = Logging()

	print("Running Configuration:\n{}".format(conf))

	if conf.algorithm == "mxm":

		mxm()

	elif conf.algorithm == "dot":

		dot()

	elif conf.algorithm == "mxm_block":

		mxm_block()

	else:
		raise Exception("Unknown Conf.algorithm: {}".format(conf.algorithm))

	# Print Result		
	print(logging)
	print()
	print()

	return logging

if __name__ == "__main__":
	
	parser = argparse.ArgumentParser(description='Python Argument Parser')

	parser.add_argument("-c","--cache-size",help = "The size of the cache in bytes", default = 65536, type = int)
	parser.add_argument("-b","--block-size",help = "The size of a data block in bytes", default = 64, type = int)
	parser.add_argument("-n","--associativity",help = "The n-way associativity of the cache", default = 2, type = int)
	parser.add_argument("-r","--replacement",help = "The replacement policy", default = "LRU", choices=['LRU', 'FIFO', 'random'])
	parser.add_argument("-a","--algorithm",help = "The algorithm to simulate", default = "mxm", choices=['dot', 'mxm', 'mxm_block'])
	
	args = parser.parse_args()

	main(args)
	




