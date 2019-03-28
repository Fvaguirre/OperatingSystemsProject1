import process
import scheduler
import logger
import math

'''
	fillReadyQueue
	fills the ready queue based on priority (tau)
	params: 
		p_scheduler: the process scheduler
		global_time: the current time in the simulation
		l: lambda
		alpha: alpha used for tau calculations
		context_switch_time: the time it takes for a full context switch
	returns an updated global_time
'''
def fillReadyQueue(p_scheduler, global_time, l, alpha, context_switch_time):
	#check if there are no more processes
	if not p_scheduler.processes.empty():
		#there are more processes
		while not p_scheduler.processes.empty() and p_scheduler.processes.queue[0][2].arrival_time <= global_time:
			#this get removes this node from p_scheduler.processes
			current_node = p_scheduler.processes.get()
			#put is a tuple, where (1,2,3) 1 is how the queue is ordered, 2 is the tie breaker
			#current_node[0] = tau
			#current_node[1] = pid
			#current_node[2] = Process object
			if (current_node[2].tau == 0):
				current_node[2].tau = math.ceil(1/l)
			else:
				#tau(i+1) = (alpha * t(i)) + ((1-alpha) * tau(i))
				current_node[2].tau = math.ceil((alpha * current_node[2].cpu_burst_times[current_node[2].curr_cpu_burst]) + ((1-alpha) * current_node[2].tau))
			#put the process in the ready queue by tau priority
			p_scheduler.ready_queue.put((current_node[2].tau, current_node[1], current_node[2]))
			r_q = p_scheduler.returnPrintableReadyQueue()
			print("time %dms: Process %c (tau %dms) arrived; added to ready queue [Q %s]" %(global_time, current_node[1], current_node[2].tau, r_q))
	return global_time


'''
	incrementWaitTime
	increments the wait time in the logger (used for final calculations)
	params:
		p_scheduler: the process scheduler
'''
def incrementWaitTime(p_scheduler):
	if not p_scheduler.ready_queue.empty():
		for proc in p_scheduler.ready_queue.queue:
			p_scheduler.logger[proc[2].pid].wait_time += 1


'''
	runContextSwitch
	runs the context switch
	during a context switch we should: 
		fill the ready queue with any processes that arrive
		continue to run the i/o bursts in the blocking queue
		increment wait time
		increment global time
	params:
		p_scheduler: the process scheduler
		global_time: the time in the simulation
		context_switch_time: the time it takes for one full context switch
		alpha: alpha, needed for tau calculations
		l: lambda
	returns:
		the updated global time, and True (true that there was a context switch)
'''
def runContextSwitch(p_scheduler, global_time, context_switch_time, alpha, l):
	#get the running process
	run_proc = p_scheduler.running
	#and set it to none so that there are no preemptions while running a context switch
	p_scheduler.running = None
	cs_time = 0
	#only run half of the context switch time when loading process into running or taking it out
	while cs_time < .5*context_switch_time:
		#can do ready queue things
		fillReadyQueue(p_scheduler, global_time, l, alpha, context_switch_time)
		#increment io time and blocking things
		checkBlockingQueue(p_scheduler, global_time, alpha, context_switch_time, l)
		#increment global time (and wait time?)
		global_time += 1
		#incrementWaitTime(p_scheduler)
		cs_time += 1
	return global_time, True


"""
 readyQueueToRunning
    check if the readyQueue is not empty 
        if readyQueue is not empty:
            check if there is a running process
                if there is no running process:
                    peek and pop the first process in the readyQueue and set it to the running process
                else there is a running process:
                    peek at first process in readyQueue to check the remaining time
                    if the remaining time is less than the running process remaining time:
                        there is a preemption, current running process gets sent back to readyQueue, reset the running process with new process
                    else the new remaining time is greater than the running process remaining time:
                        let the current running process keep running 
    params:
    	p_scheduler: process scheduler
    	alpha: alpha used for tau
    	global_time: the global time in the simulation
    	context_switch_time: the time it takes for a full context switch
    	l: lambda used for tau
    return:
    	updated global time, and if there was a context switch (True or False) 
"""
def readyQueueToRunning(p_scheduler, alpha, global_time, context_switch_time, l):
	#if_switched is a bool to tell if there was a context switch
	if_switched = False
	if not p_scheduler.ready_queue.empty():
		#the ready queue is not empty
		if p_scheduler.running is None:
			#there is no process currently running
			current_node = p_scheduler.ready_queue.get()
			#set the remaining time of the current node if not already set
			if (current_node[2].remaining_time == -1):
				current_node[2].remaining_time = current_node[2].cpu_burst_times[current_node[2].curr_cpu_burst]
			r_q = p_scheduler.returnPrintableReadyQueue()
			#perform the context switch to load the process into running
			global_time, if_switched = runContextSwitch(p_scheduler, global_time, context_switch_time, alpha, l)
			#set the running process
			p_scheduler.running = current_node[2]
			#increment context switch count
			p_scheduler.logger[p_scheduler.running.pid].num_context_switches += 1
			#the print for if the process is running an already started burst time
			if (p_scheduler.running.remaining_time < p_scheduler.running.cpu_burst_times[p_scheduler.running.curr_cpu_burst]):
				print("time %dms: Process %c started using the CPU with %dms remaining [Q %s]" %(global_time, p_scheduler.running.pid, p_scheduler.running.remaining_time, r_q))
				p_scheduler.running.time_finished = global_time + p_scheduler.running.remaining_time
			#the print for if the process is running a new burst time
			else:
				print("time %dms: Process %c started using the CPU for %dms burst [Q %s]" %(global_time, p_scheduler.running.pid, p_scheduler.running.cpu_burst_times[p_scheduler.running.curr_cpu_burst], r_q))
				p_scheduler.running.time_finished = global_time + p_scheduler.running.cpu_burst_times[p_scheduler.running.curr_cpu_burst]
			p_scheduler.running.remaining_time += 1
		else:
			#there is currently a process running
			current_node = p_scheduler.ready_queue.get()
			#check the new node's remaining time against the currently running process remaining time
			if (current_node[2].remaining_time == -1):
				current_node[2].remaining_time = current_node[2].cpu_burst_times[current_node[2].curr_cpu_burst]
			#calculate the running process's new priority (but do not reset its tau)
			new_priority = p_scheduler.running.tau - (p_scheduler.running.cpu_burst_times[p_scheduler.running.curr_cpu_burst] - p_scheduler.running.remaining_time)
			if(current_node[2].tau < new_priority):
				#there is a preemption
				r_q = p_scheduler.returnPrintableReadyQueue()
				print("time %dms: Process %c (tau %d) will preempt %c [Q %s]" %(global_time, current_node[2].pid, current_node[2].tau, p_scheduler.running.pid, r_q))
				#increment preemption
				p_scheduler.logger[p_scheduler.running.pid].num_premptions += 1
				#put the process into the ready queue
				p_scheduler.ready_queue.put((new_priority, p_scheduler.running.pid, p_scheduler.running))
				#context switch once for removing process in there
				global_time, if_switched = runContextSwitch(p_scheduler, global_time, context_switch_time, alpha, l)
				#context switch again for putting new process in
				global_time, if_switched = runContextSwitch(p_scheduler, global_time, context_switch_time, alpha, l)
				#need to send currently running process back to the ready queue
				#dont actually recalculate tau, just update the priority
				p_scheduler.running = current_node[2]
				p_scheduler.logger[p_scheduler.running.pid].wait_time -= 1
				p_scheduler.logger[p_scheduler.running.pid].num_context_switches += 1
				r_q = p_scheduler.returnPrintableReadyQueue()
				print("time %dms: Process %c started using the CPU for %dms burst [Q %s]" %(global_time, p_scheduler.running.pid, p_scheduler.running.cpu_burst_times[p_scheduler.running.curr_cpu_burst], r_q))
				p_scheduler.running.time_finished = global_time + p_scheduler.running.cpu_burst_times[p_scheduler.running.curr_cpu_burst]
				p_scheduler.running.remaining_time += 1
			else:
				#there was no preemption
				p_scheduler.ready_queue.put((current_node[2].tau, current_node[2].pid, current_node[2]))
	return global_time, if_switched



'''
	decrementRunning
	a function that decrements the count of the running process
	also checks if it is completed its cpu burst
	and if so will move it to blocking to begin its io bursts
	params:
		p_scheduler: process scheduler
    	global_time: the global time in the simulation
    	alpha: alpha used for tau
    	context_switch_time: the time it takes for a full context switch
    	l: lambda used for tau
    returns:
    	updated global time, and if there was a context switch (True or False) 
'''
def decrementRunning(p_scheduler, global_time, alpha, context_switch_time, l):
	#variable for if there was a context switch initally set to false
	if_switched = False

	if not p_scheduler.running is None:
		p_scheduler.running.remaining_time -= 1
		p_scheduler.logger[p_scheduler.running.pid].cpu_time += 1
		#process is leaving running
		#if (p_scheduler.running.remaining_time == -1):
		if (global_time == p_scheduler.running.time_finished):
			#increment the current cpu burst
			p_scheduler.running.curr_cpu_burst += 1
			if (p_scheduler.running.curr_cpu_burst != p_scheduler.running.num_bursts):
				r_q = p_scheduler.returnPrintableReadyQueue()
				print("time %dms: Process %c completed a CPU burst; %d bursts to go [Q %s]" %(global_time, p_scheduler.running.pid, (p_scheduler.running.num_bursts-p_scheduler.running.curr_cpu_burst), r_q))
			
			#CHECK IF PROCESS HAS ANY MORE IO BURSTS BEFORE MOVING TO BLOCKING
			if (p_scheduler.running.curr_io_burst == len(p_scheduler.running.io_burst_times)):
				#the process has run all its bursts
				p_scheduler.running.finished = True
				logTimes(p_scheduler)
				r_q = p_scheduler.returnPrintableReadyQueue()
				print("time %dms: Process %c terminated [Q %s]" %(global_time, p_scheduler.running.pid, r_q))
				global_time += 1
				p_scheduler.running = None
			#else there are more bursts
			else:
				#SET REMAINING TIME TO IO BURST TIME
				p_scheduler.running.remaining_time = p_scheduler.running.io_burst_times[p_scheduler.running.curr_io_burst]
				
				p_scheduler.running.tau = math.ceil((alpha * p_scheduler.running.cpu_burst_times[p_scheduler.running.curr_cpu_burst-1]) + ((1-alpha) * p_scheduler.running.tau))
				r_q = p_scheduler.returnPrintableReadyQueue()
				print("time %dms: Recalculated tau = %dms for process %c [Q %s]" %(global_time, p_scheduler.running.tau, p_scheduler.running.pid, r_q))
				print("time %dms: Process %c switching out of CPU; will block on I/O until time %dms [Q %s]" %(global_time, p_scheduler.running.pid, (p_scheduler.running.io_burst_times[p_scheduler.running.curr_io_burst] + global_time + .5*context_switch_time), r_q))
				p_scheduler.running.time_finished = (p_scheduler.running.io_burst_times[p_scheduler.running.curr_io_burst] + global_time + .5*context_switch_time)
				run_proc = p_scheduler.running
				global_time, if_switched = runContextSwitch(p_scheduler, global_time, context_switch_time, alpha, l)
				p_scheduler.running = run_proc
				#print("                  time is %d : IO burst is %d long " %(global_time, p_scheduler.running.io_burst_times[p_scheduler.running.curr_io_burst]))
				p_scheduler.running.remaining_time += 1
				#print("process %c started performing io" %p_scheduler.running.pid)
				
				
				#print("                       GLOBAL TIME 2: %d" %global_time)
				
				#global_time += 1
				
				#need to move the process to the blocking queue
				p_scheduler.blocking.append(p_scheduler.running)
				p_scheduler.running = None
	return global_time, if_switched







def checkIO(proc, alpha, p_scheduler, global_time, context_switch_time, l):
	preempt = 0
	flagged = False
	#check if the time is finished time
	#print("    this shit: %d" %(proc.time_finished))
	if (global_time == proc.time_finished):
		#incrememnt the current io burst
		proc.curr_io_burst += 1
		#reset the remaining time to next cpu burst
		proc.remaining_time = proc.cpu_burst_times[proc.curr_cpu_burst]
		#the io burst is completed, need to recalculate tau and move back to ready queue
		#proc.tau = math.ceil((alpha * proc.cpu_burst_times[proc.curr_cpu_burst-1]) + ((1-alpha) * proc.tau))
		#check if there is a current running process
		if p_scheduler.running != None:
			#check if this process will preempt current running process
			running_priority = p_scheduler.running.tau - (p_scheduler.running.cpu_burst_times[p_scheduler.running.curr_cpu_burst] - p_scheduler.running.remaining_time)
		else:
			running_priority = -100
		#process gets added back to the ready queue
		if (p_scheduler.ready_queue.empty()):
				flagged = True
		p_scheduler.ready_queue.put((proc.tau, proc.pid, proc))
		r_q = p_scheduler.returnPrintableReadyQueue()
		if (running_priority < proc.tau):
			#no preemption
			print("time %dms: Process %c (tau %dms) completed I/O; added to ready queue [Q %s]" %(global_time, proc.pid, proc.tau, r_q))
			p_scheduler.logger[proc.pid].wait_time -= 1
			if flagged:
				global_time -= 1
		else:
			#preemption
			print("time %dms: Process %c (tau %dms) completed I/O and will preempt %c [Q %s]" %(global_time, proc.pid, proc.tau, p_scheduler.running.pid, r_q))
			p_scheduler.logger[p_scheduler.running.pid].num_premptions += 1
			p_scheduler.logger[proc.pid].wait_time -= 1
			p_scheduler.running.remaining_time += 1
			p_scheduler.ready_queue.put((p_scheduler.running.tau, p_scheduler.running.pid, p_scheduler.running))
			preempt = 1
		p_scheduler.blocking.remove(proc)
	return preempt, global_time




def checkBlockingQueue(p_scheduler, global_time, alpha, context_switch_time, l):
	preempt = 0
	if  len(p_scheduler.blocking) > 0:
			#the blocking array is not empty
			#print("\t           blocking is not empty")
			#go through each proccess in blocking to check if it is finished running io burst
			for proc in p_scheduler.blocking:
				#this function decrememnts the remaining time
				#also moves any finished processes back to the ready queue
				preempt, global_time = checkIO(proc, alpha, p_scheduler, global_time, context_switch_time, l)
				#preemtpt == 1 there was a preemption
				if preempt == 1:
					return preempt, global_time
	return preempt, global_time




def logTimes(p_scheduler):
    running_proc_logger = p_scheduler.logger[p_scheduler.running.pid]
    running_proc_logger.turnaround_times = p_scheduler.running.cpu_burst_times




def getValues(p_scheduler, context_switch_time, avg_cpu_burst_time):
	logs = p_scheduler.logger
	total_wait_time = 0
	total_switches = 0
	total_preemp = 0
	for k,v in p_scheduler.logger.items():
		total_wait_time += v.wait_time
		total_switches += v.num_context_switches
		total_preemp += v.num_premptions
	avg_wait_time = total_wait_time/total_switches
	avg_turnaround = avg_cpu_burst_time + avg_wait_time + context_switch_time
	return [avg_cpu_burst_time, avg_wait_time, avg_turnaround, total_switches, total_preemp]






def runSRT(processes, num_processes, context_switch_time, alpha, l):
	#print("\n\nIN RUNSRT")
	#make a count for completed jobs to use in the while loop
	jobs_completed = 0
	#make a variable for the global time to keep track of time passed
	global_time = 0
	#make the processes scheduler
	p_scheduler = scheduler.Scheduler(processes)
	#print the arrivals of the p_scheduler
	p_scheduler.printArrivals()
	#for decrementing purposes = 0
	#print the simulation start
	r_q = p_scheduler.returnPrintableReadyQueue()
	print(p_scheduler)
	print("time %dms: Simulator started for SRT [Q %s]" %(global_time, r_q))

	cpu_sum = 0
	num_bursts = 0
	for proc in p_scheduler.processes.queue:
		cpu_sum += sum(proc[2].cpu_burst_times)
		num_bursts += len(proc[2].cpu_burst_times)
	#start the simulation
	#while there are still jobs left
	while jobs_completed < num_processes:
		#print("          GLOBAL TIME %dms" %global_time)
		#if (p_scheduler.running != None):
		#	print("     beginning loop: TIME %d, process %c remaining time is %d" % (global_time, p_scheduler.running.pid, p_scheduler.running.remaining_time))
		#populate the ready queue
		global_time = fillReadyQueue(p_scheduler, global_time, l, alpha, context_switch_time)
		#print("AT TIME %d, P_SCHEDULER:" % global_time)
		#print(p_scheduler)

		#global_time = decrementRunning(p_scheduler, global_time, alpha, context_switch_time, l)
		#if (p_scheduler.running != None):
		#	print("     after decrement running: TIME %d, process %c remaining time is %d" % (global_time, p_scheduler.running.pid, p_scheduler.running.remaining_time))
		global_time, if_switched1 = readyQueueToRunning(p_scheduler, alpha, global_time, context_switch_time, l)
		#print("  if switched 1 = %s" %if_switched1)
		global_time, if_switched2 = decrementRunning(p_scheduler, global_time, alpha, context_switch_time, l)
		#print("  if switched 2 = %s" %if_switched2)
		#global_time = checkBlockingQueue(p_scheduler, global_time, alpha, context_switch_time, l)
		
		#instead of a separate function, gonna check the blocking queue here so i can
		#better deal with a preemption
		if_switched3 = False
		preempt, global_time = checkBlockingQueue(p_scheduler, global_time, alpha, context_switch_time, l)
		if (preempt == 1):
			#global_time -= 1
			#gonna try a context switch here for removing the current running process
			run_proc = p_scheduler.running
			global_time, if_switched3 = runContextSwitch(p_scheduler, global_time, context_switch_time, alpha, l)
		

		if (p_scheduler.running != None):
			p_scheduler.logger[p_scheduler.running.pid].cpu_time += 1
		incrementWaitTime(p_scheduler)

		#if there was any context switch we dont want to increment the time
		if (not if_switched1 and not if_switched2 and not if_switched3):
			global_time += 1
		if p_scheduler.processes.empty() and p_scheduler.ready_queue.empty() and (p_scheduler.running == None) and (len(p_scheduler.blocking) == 0):
			r_q = p_scheduler.returnPrintableReadyQueue()
			print("time %dms: Simulator ended for SRT [Q %s]" %(global_time, r_q))
			avg_cpu_burst_time = (cpu_sum/num_bursts)
			final_arr = getValues(p_scheduler, context_switch_time, avg_cpu_burst_time)
			return final_arr
			break
	
