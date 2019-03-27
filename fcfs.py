import process
import scheduler

# Adds processes from p_scheduler.processes to the readyQueue
# Returns 0 if there are no more processes in scheduler.processes;
# Else returns the integer number of processes moved from p_scheduler.processes to
# ReadyQueue
def readyJobs(p_scheduler, global_time):
    rc = 0
    # If no processes left
    if p_scheduler.processes.empty():
        return rc
    else:
        # While there are processes left in processes queue and
        # the highest priority process has arrived in comparison to global_time
        while not p_scheduler.processes.empty() and p_scheduler.processes.queue[0][2].arrival_time <= global_time:
            # Temp Node to hold tuple (arrival_time, pid, process)
            current_node = p_scheduler.processes.get()
            # Add it to the readyQueue
            p_scheduler.ready_queue.put((current_node[0], current_node[1], current_node[2]))
            # Print event
            r_q = p_scheduler.returnPrintableReadyQueue()
            print("time %dms: Process %c arrived; added to ready queue [Q %s]" % (global_time, current_node[1], r_q))
            rc += 1
        return rc

# Runs through the readyQueue and adds a ms tick to every processes' wait_time Logger
# member
def tickWaitTime(p_scheduler):
    # If the readyQueue is not empty
    if not p_scheduler.ready_queue.empty():
        # Run through all the processes in the queue
        for p in p_scheduler.ready_queue.queue:
            # Find the logger within the scheduler dict and increment it
            p_scheduler.logger[p[2].pid].wait_time += 1

# Returns -1 nothing in running; returns 0 if job moved to running;
# returns 1 if curr running job ticks for 1 sec
def runJob(p_scheduler):
    # If no processes are running
    if p_scheduler.running is None:
        if not p_scheduler.ready_queue.empty():
            current_node = p_scheduler.ready_queue.get()
            current_process = current_node[2]
            #Edit the processes remaining time
            if current_process.remaining_time == -1 or current_process.remaining_time == 0:
                current_process.remaining_time = current_process.cpu_burst_times[current_process.curr_cpu_burst]
            # else:
            #     current_process.remainin
            p_scheduler.running = current_process
            return 0
        return -1
    else:
        p_scheduler.running.remaining_time -= 1
        p_scheduler.logger[p_scheduler.running.pid].cpu_time += 1
        return 1

# Returns -1 if no job is running; 1 if curr running job is done;
# 0 if curr_running job is not done
def checkRunningJobState(p_scheduler):
    if p_scheduler.running is None:
        return -1
    else:
        if p_scheduler.running.remaining_time <= 0:
            p_scheduler.running.remaining_time = 0
            if p_scheduler.running.curr_cpu_burst == p_scheduler.running.num_bursts - 1:
                p_scheduler.running.finished = True
            else:
                p_scheduler.running.curr_cpu_burst += 1
            return 1
        else:
            return 0

# Assumes Running is not None
# Moves the running process to the blocking queue and sets running to None
# Sets moved process' remaing time to the next io_burst
def moveRunningToBlocking(p_scheduler):
    p_scheduler.running.remaining_time = p_scheduler.running.io_burst_times[p_scheduler.running.curr_io_burst]
    p_scheduler.blocking.append(p_scheduler.running)
    p_scheduler.running = None

# Subtracts 1 tick from each process in the blocking array and returns the list
# (if any) of all process done with their current io burst
def runIO(p_scheduler):
    finished = []
    # If blocking is empty return empty list
    if len(p_scheduler.blocking) == 0:
        return finished
    else:
        index = 0
        for process in p_scheduler.blocking:
            # Remove one tick from remaining io burst time
            process.remaining_time -= 1
            # If given process is done with io
            if process.remaining_time <= 0:
                process.remaining_time = 0
                # If given process is not at its final io burst
                if process.curr_io_burst < process.num_bursts - 2:
                    # Increment the current io burst
                    process.curr_io_burst += 1
                # Add finished process to return list
                finished.append(process)
                # Delete it from the blocking array
                del p_scheduler.blocking[index]
                continue
            index += 1
        return finished

def requeueBlocking(p_scheduler, jobs, global_time):
    if len(jobs) > 0:
        for p in jobs:
            p_scheduler.processes.put((global_time, p.pid, p))


def runContextSwitch(p_scheduler, global_time, context_switch_time):
    c_s_time = 0
    while c_s_time < .5*context_switch_time:
         readyJobs(p_scheduler, global_time)
         jobs_ready = runIO(p_scheduler)
         requeueBlocking(p_scheduler, jobs_ready, global_time)
         global_time += 1
         tickWaitTime(p_scheduler)
         c_s_time += 1
    return global_time

def logTimes(p_scheduler):
    running_proc_logger = p_scheduler.logger[p_scheduler.running.pid]
    running_proc_logger.turnaround_times = p_scheduler.running.cpu_burst_times


def runFCFS(processes, num_processes, context_switch_time):
    jobs_completed = 0
    global_time = 0
    # Print arrivals
    p_scheduler = scheduler.Scheduler(processes)
    p_scheduler.printArrivals()
    # Print simulation start
    r_q = p_scheduler.returnPrintableReadyQueue()
    print("time %dms: Simulator started for FCFS [Q %s]" % (global_time, r_q))

    # Run FCFS simulation
    while jobs_completed < num_processes:
        # if global_time == 50:
        #     break
        print("GLOBAL TIME: %d" % global_time)
        jobs_readied = readyJobs(p_scheduler, global_time)
        # print("At time: %d, %d jobs readied" % (global_time, jobs_readied))
        # print(p_scheduler)
        # print()

        # tickWaitTime(p_scheduler)

        run_job_rc = runJob(p_scheduler)
        # if curr job was just moved to running
        if run_job_rc == 0:
             #process first half of context_switch_time
             p_scheduler.logger[p_scheduler.running.pid].num_context_switches += 1
             global_time = runContextSwitch(p_scheduler, global_time, context_switch_time)

             # in_context_switch = True
             # c_s_time += .5* conte

        # print(p_scheduler)
        # print()
        # print("At time: %d, %d job rc" % (global_time, run_job_rc))
        running_state = checkRunningJobState(p_scheduler)
        # print(p_scheduler)
        # print()

        if running_state == 1:
            if p_scheduler.running.finished == True:
                jobs_completed += 1
                logTimes(p_scheduler)
                p_scheduler.running = None
            else:
                moveRunningToBlocking(p_scheduler)
                #Process second half of context_switch_time
                global_time = runContextSwitch(p_scheduler, global_time, context_switch_time)
        # print(p_scheduler)
        # print()
        jobs_ready = runIO(p_scheduler)
        # print(p_scheduler)
        #might have to move to ready directly instead of processes
        requeueBlocking(p_scheduler, jobs_ready, global_time)
        # if len(jobs_ready) > 0:
        #     # print("Jobs ready:")
        #     # print(jobs_ready)
        #     for p in jobs_ready:
        #         p_scheduler.processes.put((global_time, p.pid, p))
        # jobs_ready = []
        tickWaitTime(p_scheduler)

        global_time += 1
        print("========================================================")
    logs = p_scheduler.logger
    print(logs)
