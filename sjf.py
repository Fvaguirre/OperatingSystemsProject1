import process
import scheduler
import math
import event

def tau_calc(p_scheduler, process, global_time, curr_tau, curr_burst, alpha):
	new_tau = math.ceil(alpha * curr_burst + (1-alpha)*curr_tau)
	r_q = p_scheduler.returnPrintableReadyQueue()
	#print(process)
	output = event.Event("tau_recalc", global_time, process, r_q, new_tau, None)
	p_scheduler.addEvent(output)
	return new_tau

def readyJobs(p_scheduler, global_time, lam):
	rc = 0
	if p_scheduler.processes.empty():
		return rc
	else:
		while not p_scheduler.processes.empty() and p_scheduler.processes.queue[0][2].arrival_time <= global_time:
			current_node = p_scheduler.processes.get()
			current_node[2].tau = 1/lam
			p_scheduler.ready_queue.put((current_node[2].tau, current_node[1], current_node[2]))
			r_q = p_scheduler.returnPrintableReadyQueue()
			output = event.Event("arrival", global_time, current_node[2], r_q, 1/lam, None)
			p_scheduler.addEvent(output)
			rc += 1
		return rc

def checkRunningJobState(p_scheduler, global_time):
	if p_scheduler.running is None:
		return -1
	else:
		if p_scheduler.running.remaining_time <= 0:
			#print(global_time)
			p_scheduler.running.remaining_time = 0
			if p_scheduler.running.curr_cpu_burst == p_scheduler.running.num_bursts-1:
				p_scheduler.running.finished = True
				r_q = p_scheduler.returnPrintableReadyQueue()
				output = event.Event("terminated", global_time, p_scheduler.running, r_q, None, None)
				p_scheduler.addEvent(output)
			else:
				p_scheduler.running.curr_cpu_burst += 1
				r_q = p_scheduler.returnPrintableReadyQueue()
				output = event.Event("cpu_finish", global_time, p_scheduler.running, r_q, p_scheduler.running.tau, None)
				p_scheduler.addEvent(output)
			return 1
		else:
			return 0

def runJob(p_scheduler, global_time):
	if p_scheduler.running is None:
		if not p_scheduler.ready_queue.empty():
			# current_node = p_scheduler.ready_queue.get()
			# current_process = current_node[2]
			# if current_process.remaining_time == -1 or current_process.remaining_time == 0:
			# 	current_process.remaining_time = current_process.cpu_burst_times[current_process.curr_cpu_burst]
			# p_scheduler.running = current_process
			return 0
		return -1
	else:
		p_scheduler.running.remaining_time -= 1
		p_scheduler.logger[p_scheduler.running.pid].cpu_time += 1
		return 1

def moveRunningToBlocking(p_scheduler, global_time, alpha):
	p_scheduler.running.remaining_time = p_scheduler.running.io_burst_times[p_scheduler.running.curr_io_burst]
	#print(p_scheduler.running.io_burst_times[p_scheduler.running.curr_io_burst])
	p_scheduler.blocking.append(p_scheduler.running)
	p_scheduler.running = None

def runIO(p_scheduler, global_time,num_processes):
	finished = []
	if len(p_scheduler.blocking) == 0:
		return finished
	else:
		index = 0
		while index < len(p_scheduler.blocking):
			p_scheduler.blocking[index].remaining_time -= 1
			if p_scheduler.blocking[index].remaining_time + 1 <= 0:
				#print(global_time)
				p_scheduler.blocking[index].remaining_time = 0
				if p_scheduler.blocking[index].curr_io_burst < p_scheduler.blocking[index].num_bursts - 2:
					p_scheduler.blocking[index].curr_io_burst += 1
				finished.append(p_scheduler.blocking[index])
				p_scheduler.blocking.remove(p_scheduler.blocking[index])
				continue
			index += 1
		return finished
		# for process in p_scheduler.blocking:
		# 	process.remaining_time -= 1
		# 	if process.remaining_time = 0:
		# 		process.remaining_time = 0;
		# 		if process.curr_io_burst < process.num_bursts - 2:
		# 			process.curr_io_burst += 1
		# 		finished.append(process)
		# 		p_scheduler.blocking.remove(process)
		# 	index += 1
		# return finished

def requeueBlocking(p_scheduler, jobs, global_time):
	if len(jobs) > 0:
		for p in jobs:
			#print("this ran 1")
			p_scheduler.ready_queue.put((p.tau, p.pid, p))
			r_c = p_scheduler.returnPrintableReadyQueue()
			output = event.Event("io_finish", global_time, p, r_c, None, None)
			p_scheduler.addEvent(output)


def tickWaitTime(p_scheduler):
	if not p_scheduler.ready_queue.empty():
		for p in p_scheduler.ready_queue.queue:
			p_scheduler.logger[p[2].pid].wait_time += 1

def runContextSwitch(p_scheduler, global_time, context_switch_time, lam, alpha, num_processes):
	c_s_time = 0
	while c_s_time < .5*context_switch_time:
		readyJobs(p_scheduler, global_time, lam)
		jobs_ready = runIO(p_scheduler, global_time, num_processes)
		requeueBlocking(p_scheduler, jobs_ready, global_time)
		global_time += 1
		#tickWaitTime(p_scheduler)
		c_s_time += 1
		#print(global_time)
	return global_time

def logTimes(p_scheduler):
	running_proc_logger = p_scheduler.logger[p_scheduler.running.pid]
	running_proc_logger.turnaround_times = p_scheduler.running.cpu_burst_times

def getValues(p_scheduler, context_switch_time):
	logs = p_scheduler.logger
	#print(logs)
	total_cpu_time = 0
	total_wait_time = 0
	total_switches = 0
	total_preemp = 0
	for k,v in p_scheduler.logger.items():
		total_cpu_time += v.cpu_time
		total_wait_time += v.wait_time
		total_switches += v.num_context_switches
		total_preemp += v.num_premptions
		#print(logs[i].cpu_time)
		#print(logs[i].num_context_switches)

	avg_cpu_burst = total_cpu_time/total_switches
	avg_wait_time = total_wait_time/total_switches
	avg_turn_time = avg_cpu_burst+avg_wait_time+context_switch_time

	return [avg_cpu_burst, avg_wait_time, avg_turn_time, total_switches, total_preemp]


def runSJF(processes, num_processes, context_switch_time, l, alpha):
	jobs_completed = 0;
	global_time = 0
	p_scheduler = scheduler.Scheduler(processes);
	r_q = p_scheduler.returnPrintableReadyQueue()
	print("time %dms: Simulator started for SJF %s"%(global_time, r_q))
	in_context_switch = False
	skip_io = False

	while jobs_completed < num_processes:

		#print("GLOBAL TIME: %d" % global_time)
		#print("before ready jobs: " + str(p_scheduler))
		jobs_readied = readyJobs(p_scheduler, global_time, l)
		#print("after ready jobs: " + str(p_scheduler))

		#print("here5")
		jobs_ready = runIO(p_scheduler, global_time, num_processes)

		#print("here6")
		

		#if global_time == 445:
		#	print(p_scheduler.running)
		#	print(p_scheduler.ready_queue.queue)

		running_state = checkRunningJobState(p_scheduler, global_time)

		#print("here4")
		if running_state == 1:
			if p_scheduler.running.finished == True:
				jobs_completed += 1
				logTimes(p_scheduler)
				p_scheduler.running = None
				global_time = runContextSwitch(p_scheduler, global_time, context_switch_time, l, alpha, num_processes)
				in_context_switch = True
			else:
				r_q = p_scheduler.returnPrintableReadyQueue()
				output = event.Event("io_start", global_time, p_scheduler.running, r_q, None, context_switch_time)
				p_scheduler.addEvent(output)
				c_burst = p_scheduler.running.cpu_burst_times[p_scheduler.running.curr_cpu_burst-1]
				c_tau = p_scheduler.running.tau
				next_tau = tau_calc(p_scheduler, p_scheduler.running, global_time, c_tau, c_burst, alpha)
				p_scheduler.running.tau = next_tau
				#print(global_time)
				global_time = runContextSwitch(p_scheduler, global_time, context_switch_time, l, alpha, num_processes)
				#print(global_time)
				in_context_switch = True
				moveRunningToBlocking(p_scheduler, global_time, alpha)

		run_job_rc = runJob(p_scheduler, global_time)

		if run_job_rc == 0:
			#print(global_time)
			global_time = runContextSwitch(p_scheduler, global_time, context_switch_time, l, alpha, num_processes)
			current_node = p_scheduler.ready_queue.get()
			current_process = current_node[2]
			if current_process.remaining_time == -1 or current_process.remaining_time == 0:
				current_process.remaining_time = current_process.cpu_burst_times[current_process.curr_cpu_burst]
			p_scheduler.running = current_process
			p_scheduler.logger[p_scheduler.running.pid].num_context_switches += 1
			r_q = p_scheduler.returnPrintableReadyQueue()
			output = event.Event("cpu_start", global_time, p_scheduler.running, r_q, None, None)
			p_scheduler.addEvent(output)
			in_context_switch = True
			#print(global_time)

		#print(global_time)
		#print("here3")
		requeueBlocking(p_scheduler, jobs_ready, global_time)

		if p_scheduler.running is None:
			if not p_scheduler.ready_queue.empty():
				global_time = runContextSwitch(p_scheduler, global_time, context_switch_time, l , alpha, num_processes)
				current_node = p_scheduler.ready_queue.get()
				current_process = current_node[2]
				if current_process.remaining_time == -1 or current_process.remaining_time == 0:
					current_process.remaining_time = current_process.cpu_burst_times[current_process.curr_cpu_burst]
				p_scheduler.running = current_process
				p_scheduler.logger[p_scheduler.running.pid].num_context_switches += 1
				r_q = p_scheduler.returnPrintableReadyQueue()
				output = event.Event("cpu_start", global_time, p_scheduler.running, r_q, None, None)
				p_scheduler.addEvent(output)
				in_context_switch = True

		#print("here7")f
		tickWaitTime(p_scheduler)

		#print(p_scheduler.blocking)
		#print(p_scheduler.returnPrintableReadyQueue())
		#print(p_scheduler.running)
		#print(p_scheduler.returnPrintableReadyQueue())
		#print(p_scheduler.logger[0].wait_time)
		#print(p_scheduler.ready_queue.queue)
		if not in_context_switch:
			global_time += 1
		else:
			in_context_switch = False
			skip_io = True
		#print("========================================================")
	logs = p_scheduler.logger
	#print(logs)
	total_cpu_time = 0
	total_wait_time = 0
	total_switches = 0
	p_scheduler.printEvents()
	r_q = p_scheduler.returnPrintableReadyQueue()
	print("time %dms: Simulator ended for SJF %s" % (global_time, r_q))
	print(getValues(p_scheduler, context_switch_time))
	#r_q = p_scheduler.returnPrintableReadyQueue()
	#print("time %dms: Simulator ended for SJF %s" % (global_time, r_q))
	#for k,v in p_scheduler.logger.items():
	#	total_cpu_time += v.cpu_time
	#	total_wait_time += v.wait_time
	#	total_switches += v.num_context_switches
		#print(logs[i].cpu_time)
		#print(logs[i].num_context_switches)

	#avg_cpu_burst = total_cpu_time/total_switches
	#avg_wait_time = total_wait_time/total_switches

	#print(avg_cpu_burst)
	#print(avg_wait_time)
	#print(total_switches)

	#print(processes[4].cpu_burst_times)
	#print(context_switch_time)
	#for process in processes:
	#	print(process)