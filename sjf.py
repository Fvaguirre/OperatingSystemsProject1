import process
import scheduler
import math
import event

def tau_calc(p_scheduler, process, global_time, curr_tau, curr_burst, alpha):
	new_tau = math.ceil(alpha * curr_burst + (1-alpha)*curr_tau)
	r_q = p_scheduler.returnPrintableReadyQueue()
	#print(process)
	output = event.Event("tau_recalc", global_time, process, r_q, new_tau)
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
			output = event.Event("arrival", global_time, current_node[2], r_q, 1/lam)
			p_scheduler.addEvent(output)
			rc += 1
		return rc

def checkRunningJobState(p_scheduler, global_time):
	if p_scheduler.running is None:
		return -1
	else:
		if p_scheduler.running.remaining_time <= 0:
			p_scheduler.running.remaining_time = 0
			if p_scheduler.running.curr_cpu_burst == p_scheduler.running.num_bursts-1:
				p_scheduler.running.finished = True
			else:
				p_scheduler.running.curr_cpu_burst += 1
				r_q = p_scheduler.returnPrintableReadyQueue()
				output = event.Event("cpu_finish", global_time, p_scheduler.running, r_q, p_scheduler.running.tau)
				p_scheduler.addEvent(output)
			return 1
		else:
			return 0

def runJob(p_scheduler, global_time):
	if p_scheduler.running is None:
		if not p_scheduler.ready_queue.empty():
			current_node = p_scheduler.ready_queue.get()
			current_process = current_node[2]
			if current_process.remaining_time == -1 or current_process.remaining_time == 0:
				current_process.remaining_time = current_process.cpu_burst_times[current_process.curr_cpu_burst]
			p_scheduler.running = current_process
			r_q = p_scheduler.returnPrintableReadyQueue()
			output = event.Event("cpu_start", global_time, p_scheduler.running, r_q, None)
			p_scheduler.addEvent(output)
			return 0
		return -1
	else:
		p_scheduler.running.remaining_time -= 1
		p_scheduler.logger[p_scheduler.running.pid].cpu_time += 1
		return 1

def moveRunningToBlocking(p_scheduler, global_time):
	p_scheduler.running.remaining_time = p_scheduler.running.io_burst_times[p_scheduler.running.curr_io_burst]
	p_scheduler.blocking.append(p_scheduler.running)
	r_q = p_scheduler.returnPrintableReadyQueue()
	output = event.Event("io_start", global_time, p_scheduler.running, r_q, None)
	p_scheduler.addEvent(output)
	p_scheduler.running = None

def runIO(p_scheduler):
	finished = []
	if len(p_scheduler.blocking) == 0:
		return finished
	else:
		index = 0
		for process in p_scheduler.blocking:
			process.remaining_time -= 1
			if process.remaining_time <= 0:
				process.remaining_time = 0;
				if process.curr_io_burst < process.num_bursts - 2:
					process.curr_io_burst += 1
				finished.append(process)
				p_scheduler.blocking.remove(process)
			index += 1
		return finished

def requeueBlocking(p_scheduler, jobs, global_time, alpha):
	if len(jobs) > 0:
		for p in jobs:
			#print("this ran 1")
			c_burst = p.cpu_burst_times[p.curr_cpu_burst]
			c_tau = p.tau
			next_tau = tau_calc(p_scheduler, p, global_time, c_tau, c_burst, alpha)
			p.tau = next_tau
			p_scheduler.ready_queue.put((p.tau, p.pid, p))


def tickWaitTime(p_scheduler):
	if not p_scheduler.ready_queue.empty():
		for p in p_scheduler.ready_queue.queue:
			p_scheduler.logger[p[2].pid].wait_time += 1

def runContextSwitch(p_scheduler, global_time, context_switch_time, lam, alpha):
	c_s_time = 0
	while c_s_time < .5*context_switch_time:
		readyJobs(p_scheduler, global_time, lam)
		jobs_ready = runIO(p_scheduler)
		requeueBlocking(p_scheduler, jobs_ready, global_time, alpha)
		global_time += 1
		tickWaitTime(p_scheduler)
		c_s_time += 1
	return global_time

def logTimes(p_scheduler):
	running_proc_logger = p_scheduler.logger[p_scheduler.running.pid]
	running_proc_logger.turnaround_times = p_scheduler.running.cpu_burst_times

def runSJF(processes, num_processes, context_switch_time, l, alpha):
	jobs_completed = 0;
	global_time = 0
	p_scheduler = scheduler.Scheduler(processes);
	r_q = p_scheduler.returnPrintableReadyQueue()
	print("time %dms: Simulator started for SJF %s"%(global_time, r_q))

	while jobs_completed < num_processes:

		#print("GLOBAL TIME: %d" % global_time)
		#print("before ready jobs: " + str(p_scheduler))
		jobs_readied = readyJobs(p_scheduler, global_time, l)
		#print("after ready jobs: " + str(p_scheduler))

		#print("here5")
		jobs_ready = runIO(p_scheduler)

		#print("here6")
		requeueBlocking(p_scheduler, jobs_ready, global_time, alpha)

		#if global_time == 445:
		#	print(p_scheduler.running)
		#	print(p_scheduler.ready_queue.queue)

		run_job_rc = runJob(p_scheduler, global_time)

		if run_job_rc == 0:
			p_scheduler.logger[p_scheduler.running.pid].num_context_switches += 1
			global_time = runContextSwitch(p_scheduler, global_time, context_switch_time, l, alpha)

		#print("here3")
		running_state = checkRunningJobState(p_scheduler, global_time)

		#print("here4")
		if running_state == 1:
			if p_scheduler.running.finished == True:
				jobs_completed += 1
				logTimes(p_scheduler)
				p_scheduler.running = None
			else:
				moveRunningToBlocking(p_scheduler, global_time)
				global_time = runContextSwitch(p_scheduler, global_time, context_switch_time, l, alpha)

		#print("here7")
		tickWaitTime(p_scheduler)

		#print(p_scheduler.logger[0].wait_time)
		#print(p_scheduler.ready_queue.queue)
		global_time += 1
		#print("========================================================")
	logs = p_scheduler.logger
	#print(logs)
	total_cpu_time = 0
	total_wait_time = 0
	total_switches = 0
	p_scheduler.printEvents()
	#for i in range(num_processes):
	#	total_cpu_time += logs[i].cpu_time
	#	total_wait_time += logs[i].wait_time
	#	total_switches += logs[i].num_context_switches
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