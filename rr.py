import process, scheduler, logger, fcfs

# Returns -1 if running is None' 1 if running process is done, 0 if running process will be
# preempted and 2 if the running process is good for another tick
def checkRunningJobState(p_scheduler, rr_time_slice, curr_elapsed):
    if p_scheduler.running is None:
        return -1

    elif p_scheduler.running.remaining_time <= 0:
        p_scheduler.running.remaining_time = 0
        # p_scheduler.running.finished = True
        #Check if this is the last available cpu_burst
        if p_scheduler.running.curr_cpu_burst == p_scheduler.running.num_bursts - 1:
            p_scheduler.running.finished = True
        else:
            p_scheduler.running.curr_cpu_burst += 1
        return 1
    elif curr_elapsed == rr_time_slice:
        return 0
    else:
        return 2

def preemptProcess(p_scheduler, rr_queue_type, global_time, context_switch_time):
    if rr_queue_type == 'END':
        priority_metric = global_time
    else:
        priority_metric = float(1.0/global_time)

    p_scheduler.ready_queue.put((priority_metric, p_scheduler.running.pid, p_scheduler.running))
    p_scheduler.running = None
    global_time = fcfs.runContextSwitch(p_scheduler, global_time, context_switch_time)
    return global_time


def runPreemption(p_scheduler, global_time, rr_queue_type, context_switch_time):
    p_scheduler.logger[p_scheduler.running.pid].num_premptions += 1
    p_scheduler.logger[p_scheduler.running.pid].num_context_switches += 1
    global_time = fcfs.runContextSwitch(p_scheduler, global_time, context_switch_time)
    global_time = preemptProcess(p_scheduler, rr_queue_type, global_time, context_switch_time)
    return global_time

def runRR(processes, num_processes, context_switch_time, rr_time_slice, rr_queue_type):
    global_time = 0
    jobs_completed = 0
    p_scheduler = scheduler.Scheduler(processes, rr_queue_type)
    time_slice = 0

    while jobs_completed < num_processes:
        print("GLOBAL TIME: %d" % global_time)
        print(p_scheduler)
        jobs_readied = fcfs.readyJobs(p_scheduler, global_time)
        print(p_scheduler)
        run_job_rc = fcfs.runJob(p_scheduler)
        if run_job_rc == 0:
             #process first half of context_switch_time
             p_scheduler.logger[p_scheduler.running.pid].num_context_switches += 1
             global_time = fcfs.runContextSwitch(p_scheduler, global_time, context_switch_time)

        running_state = checkRunningJobState(p_scheduler, rr_time_slice, time_slice)
        # time for preemption
        if running_state == 0 and not p_scheduler.ready_queue.empty():
            #reset time_slice
            time_slice = 0
            global_time = runPreemption(p_scheduler, global_time, rr_queue_type, context_switch_time)
        elif running_state == 1:
            if p_scheduler.running.finished == True:
                jobs_completed += 1
                fcfs.logTimes(p_scheduler)
                p_scheduler.running = None
            else:
                fcfs.moveRunningToBlocking(p_scheduler)
                #Process second half of context_switch_time
                global_time = fcfs.runContextSwitch(p_scheduler, global_time, context_switch_time)

        jobs_ready = fcfs.runIO(p_scheduler)
        fcfs.requeueBlocking(p_scheduler, jobs_ready, global_time)
        fcfs.tickWaitTime(p_scheduler)

        global_time += 1
        time_slice += 1
        print("========================================================")
    logs = p_scheduler.logger
    print(logs)
