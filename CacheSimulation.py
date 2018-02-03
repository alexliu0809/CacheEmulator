import argparse
import matplotlib.pyplot as plt
import numpy as np
from CacheEmulator import main

parser = argparse.ArgumentParser(description='Python Argument Parser')
parser.add_argument("-c","--cache-size",help = "The size of the cache in bytes", default = 65536, type = int)
parser.add_argument("-b","--block-size",help = "The size of a data block in bytes", default = 64, type = int)
parser.add_argument("-n","--associativity",help = "The n-way associativity of the cache", default = 2, type = int)
parser.add_argument("-r","--replacement",help = "The replacement policy", default = "LRU", choices=['LRU', 'FIFO', 'random'])
parser.add_argument("-a","--algorithm",help = "The algorithm to simulate", default = "mxm", choices=['dot', 'mxm', 'mxm_block'])



def generate_graph(data, arg_arr):
	
	if arg_arr[0].cache_size != arg_arr[1].cache_size:
		var_type = "c"
	elif arg_arr[0].block_size != arg_arr[1].block_size:
		var_type = "b"
	elif arg_arr[0].associativity != arg_arr[1].associativity:
		var_type = "n"
	elif arg_arr[0].replacement != arg_arr[1].replacement:
		var_type = "r"


	title_string = ""
	title_string += arg_arr[0].algorithm.upper() + ": "
	
	if var_type != "c":
		title_string += "CacheSize=" + str(arg_arr[0].cache_size) + " "
	if var_type != "b":
		title_string += "BlockSize=" + str(arg_arr[0].block_size) + " "
	if var_type != "n":
		title_string += "Associativity=" + str(arg_arr[0].associativity) + " "
	if var_type != "r":
		title_string += "Replace=" + str(arg_arr[0].replacement) + " "

	N = 5 #Fixed
	ind = np.array([0,2,4,6,8])  # the x locations for the groups
	width = 0.2       # the width of the bars

	fig = plt.figure()
	ax = fig.add_subplot(111)

	colors = ['r','g','b','pink','lightseagreen']
	rects = []
	for idx,ele in enumerate(data):
		vals = []
		vals.append(ele.instruction_cnt)
		vals.append(ele.read_hits)
		vals.append(ele.read_misses)
		vals.append(ele.write_hits)
		vals.append(ele.write_misses)
		rects.append(ax.bar(ind + idx * width, vals, width, color=colors[idx]))

	
	for rect_group in rects:
		for rect in rect_group:
			h = rect.get_height()
			if (int(h) <= 0):
				ax.text(rect.get_x()+rect.get_width()/2., 1.01*h, '%d'%int(h), ha='center', va='bottom')
	
	ax.set_yscale('symlog')
	ax.set_ylabel('Count')
	ax.set_xticks(ind+width)
	ax.set_xticklabels( ('Insturction_Count', 'Read_Hit', 'Read_Miss','Write_Hit','Write_Miss') )
	if var_type == "c":
		ax.legend( (x for x in rects), ("CacheSize=" + str(arg.cache_size) for arg in arg_arr) )
	if var_type == "b":
		ax.legend( (x for x in rects), ("BlockSize=" + str(arg.block_size) for arg in arg_arr) )
	if var_type == "n":
		ax.legend( (x for x in rects), ("Associativity=" + str(arg.associativity) for arg in arg_arr) )
	if var_type == "r":
		ax.legend( (x for x in rects), ("Replace=" + str(arg.replacement) for arg in arg_arr) )

	plt.title(title_string)
	plt.savefig("./graphs/"+title_string+".eps", format='eps', dpi=1200)

if __name__ == "__main__":


	
	### Dot Algorithm
	#Fixed Cache Size: 1024, Block Size: 64. 
		
	
	#Different Associativity
	data = []
	arg_arr = []

	args = parser.parse_args(["-c=1024","-n=1","-a=dot"])
	arg_arr.append(args)
	data.append(main(args))

	args = parser.parse_args(["-c=1024","-n=2","-a=dot"])
	arg_arr.append(args)
	data.append(main(args))

	args = parser.parse_args(["-c=1024","-n=4","-a=dot"])
	arg_arr.append(args)
	data.append(main(args))

	args = parser.parse_args(["-c=1024","-n=8","-a=dot"])
	arg_arr.append(args)
	data.append(main(args))

	generate_graph(data, arg_arr)


	#Different Replacement Policy

	data = []
	arg_arr = []
	args = parser.parse_args(["-c=1024","-r=LRU","-a=dot"])
	arg_arr.append(args)
	data.append(main(args))

	args = parser.parse_args(["-c=1024","-r=random","-a=dot"])
	arg_arr.append(args)
	data.append(main(args))

	args = parser.parse_args(["-c=1024","-r=FIFO","-a=dot"])
	arg_arr.append(args)
	data.append(main(args))

	generate_graph(data, arg_arr)
	
	
	#Different Block Size
	data = []
	arg_arr = []

	args = parser.parse_args(["-c=1024","-b=8","-a=dot"])
	arg_arr.append(args)
	data.append(main(args))

	args = parser.parse_args(["-c=1024","-b=16","-a=dot"])
	arg_arr.append(args)
	data.append(main(args))

	args = parser.parse_args(["-c=1024","-b=64","-a=dot"])
	arg_arr.append(args)
	data.append(main(args))

	args = parser.parse_args(["-c=1024","-b=128","-a=dot"])
	arg_arr.append(args)
	data.append(main(args))

	generate_graph(data, arg_arr)

	#Different Cache Size

	data = []
	arg_arr = []

	args = parser.parse_args(["-c=256","-a=dot"])
	arg_arr.append(args)
	data.append(main(args))

	args = parser.parse_args(["-c=512","-a=dot"])
	arg_arr.append(args)
	data.append(main(args))

	args = parser.parse_args(["-c=1024","-a=dot"])
	arg_arr.append(args)
	data.append(main(args))

	args = parser.parse_args(["-c=2048","-a=dot"])
	arg_arr.append(args)
	data.append(main(args))

	generate_graph(data, arg_arr)
	

	
	### MXM Algorithm
	#Fixed Cache Size: 1024, Block Size: 64

	#Different associativity
	data = []
	arg_arr = []

	args = parser.parse_args(["-c=1024","-n=1"])
	arg_arr.append(args)
	data.append(main(args))

	args = parser.parse_args(["-c=1024","-n=2"])
	arg_arr.append(args)
	data.append(main(args))

	args = parser.parse_args(["-c=1024","-n=4"])
	arg_arr.append(args)
	data.append(main(args))

	args = parser.parse_args(["-c=1024","-n=8"])
	arg_arr.append(args)
	data.append(main(args))

	generate_graph(data, arg_arr)

	

	#Different Replacement Policy
	data = []
	arg_arr = []

	args = parser.parse_args(["-c=1024","-r=LRU"])
	arg_arr.append(args)
	data.append(main(args))

	args = parser.parse_args(["-c=1024","-r=random"])
	arg_arr.append(args)
	data.append(main(args))

	args = parser.parse_args(["-c=1024","-r=FIFO"])
	arg_arr.append(args)
	data.append(main(args))

	generate_graph(data, arg_arr)


	#Different Replacement Policy
	data = []
	arg_arr = []

	args = parser.parse_args(["-c=1024","-b=8"])
	arg_arr.append(args)
	data.append(main(args))

	args = parser.parse_args(["-c=1024","-b=16"])
	arg_arr.append(args)
	data.append(main(args))

	args = parser.parse_args(["-c=1024","-b=64"])
	arg_arr.append(args)
	data.append(main(args))

	args = parser.parse_args(["-c=1024","-b=256"])
	arg_arr.append(args)
	data.append(main(args))

	generate_graph(data, arg_arr)
	

	#Different Replacement Policy
	data = []
	arg_arr = []

	args = parser.parse_args(["-c=256"])
	arg_arr.append(args)
	data.append(main(args))

	args = parser.parse_args(["-c=512"])
	arg_arr.append(args)
	data.append(main(args))

	args = parser.parse_args(["-c=1024"])
	arg_arr.append(args)
	data.append(main(args))

	args = parser.parse_args(["-c=2048"])
	arg_arr.append(args)
	data.append(main(args))

	generate_graph(data, arg_arr)
	




	### MXM_Blocks Algorithm
	#Fixed Cache Size: 1024, Block Size: 64

	data = []
	arg_arr = []

	args = parser.parse_args(["-c=1024","-n=1","-a=mxm_block"])
	arg_arr.append(args)
	data.append(main(args))

	args = parser.parse_args(["-c=1024","-n=2","-a=mxm_block"])
	arg_arr.append(args)
	data.append(main(args))

	args = parser.parse_args(["-c=1024","-n=4","-a=mxm_block"])
	arg_arr.append(args)
	data.append(main(args))

	args = parser.parse_args(["-c=1024","-n=8","-a=mxm_block"])
	arg_arr.append(args)
	data.append(main(args))

	generate_graph(data, arg_arr)

	

	#Different Replacement Policy
	data = []
	arg_arr = []

	args = parser.parse_args(["-c=1024","-r=LRU","-a=mxm_block"])
	arg_arr.append(args)
	data.append(main(args))

	args = parser.parse_args(["-c=1024","-r=random","-a=mxm_block"])
	arg_arr.append(args)
	data.append(main(args))

	args = parser.parse_args(["-c=1024","-r=FIFO","-a=mxm_block"])
	arg_arr.append(args)
	data.append(main(args))

	generate_graph(data, arg_arr)


	#Different Replacement Policy
	data = []
	arg_arr = []

	args = parser.parse_args(["-c=1024","-b=8","-a=mxm_block"])
	arg_arr.append(args)
	data.append(main(args))

	args = parser.parse_args(["-c=1024","-b=16","-a=mxm_block"])
	arg_arr.append(args)
	data.append(main(args))

	args = parser.parse_args(["-c=1024","-b=64","-a=mxm_block"])
	arg_arr.append(args)
	data.append(main(args))

	args = parser.parse_args(["-c=1024","-b=256","-a=mxm_block"])
	arg_arr.append(args)
	data.append(main(args))

	generate_graph(data, arg_arr)
	

	#Different Replacement Policy
	data = []
	arg_arr = []

	args = parser.parse_args(["-c=256","-a=mxm_block"])
	arg_arr.append(args)
	data.append(main(args))

	args = parser.parse_args(["-c=512","-a=mxm_block"])
	arg_arr.append(args)
	data.append(main(args))

	args = parser.parse_args(["-c=1024","-a=mxm_block"])
	arg_arr.append(args)
	data.append(main(args))

	args = parser.parse_args(["-c=2048","-a=mxm_block"])
	arg_arr.append(args)
	data.append(main(args))

	generate_graph(data, arg_arr)



	#Debug
	#main(parser.parse_args(["-c=32","-b=8","-n=2","-r=FIFO","-a=dot"]))

	pass