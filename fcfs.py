import process
import scheduler

def readyJobs(p_scheduler, global_time):
    rc = 0
    if p_scheduler.processes.empty():
        return rc
    else:
        while not p_scheduler.processes.empty() and p_scheduler.processes.queue[0][2].arrival_time <= global_time:
            current_node = p_scheduler.processes.get()
            p_scheduler.ready_queue.put((current_node[0], current_node[1], current_node[2]))
            rc += 1
        return rc
#returns -1 nothing in running; returns 0 if job moved to running; returns 1 if curr running job ticks for 1 sec
def runJob(p_scheduler):
    if p_scheduler.running is None:
        if not p_scheduler.ready_queue.empty():
            current_node = p_scheduler.ready_queue.get()
            current_process = current_node[2]
            #Edit the processes remaining time
            current_process.remaining_time = current_process.cpu_burst_times[current_process.curr_cpu_burst]
            p_scheduler.running = current_process
            return 0
        return -1
    else:
        p_scheduler.running.remaining_time -= 1
        return 1
#Returns -1 if no job is running; 1 if curr running job is done; 0 if curr_running job is not done
def checkRunningJobState(p_scheduler):
    if p_scheduler.running is None:
        return -1
    else:
        if p_scheduler.running.remaining_time <= 0:
            p_scheduler.running.remaining_time = 0
            # p_scheduler.running.finished = True
            #Check if this is the last available cpu_burst
            if p_scheduler.running.curr_cpu_burst == p_scheduler.running.num_bursts - 1:
                p_scheduler.running.finished = True
            else:
                p_scheduler.running.curr_cpu_burst += 1
            return 1
        else:
            return 0
def moveRunningToBlocking(p_scheduler):
    p_scheduler.running.remaining_time = p_scheduler.running.io_burst_times[p_scheduler.running.curr_io_burst]
    p_scheduler.blocking.append(p_scheduler.running)
    p_scheduler.running = None

def runIO(p_scheduler):
    finished = []
    if len(p_scheduler.blocking) == 0:
        return finished
    else:
        index = 0
        for process in p_scheduler.blocking:
            process.remaining_time -= 1
            if process.remaining_time == 0:
                if process.curr_io_burst < process.num_bursts - 2:
                    process.curr_io_burst += 1

                finished.append(process)
                del p_scheduler.blocking[index]
                continue
            index += 1
        return finished

def runFCFS(processes, num_processes, context_switch_time):
    jobs_completed = 0
    global_time = 0

    p_scheduler = scheduler.Scheduler(processes)
    # global_time += 1
    # rc = readyJobs(p_scheduler, global_time)
    # print("RC: %d" % rc)
    print()

    while jobs_completed < num_processes:
        # if global_time == 50:
        #     break
        print("GLOBAL TIME: %d" % global_time)
        jobs_readied = readyJobs(p_scheduler, global_time)
        # print("At time: %d, %d jobs readied" % (global_time, jobs_readied))
        print(p_scheduler)
        print()
        run_job_rc = runJob(p_scheduler)
        print(p_scheduler)
        print()
        # print("At time: %d, %d job rc" % (global_time, run_job_rc))
        running_state = checkRunningJobState(p_scheduler)
        print(p_scheduler)
        print()

        if running_state == 1:
            if p_scheduler.running.finished == True:
                jobs_completed += 1
                p_scheduler.running = None
            else:
                moveRunningToBlocking(p_scheduler)
        print(p_scheduler)
        print()
        jobs_ready = runIO(p_scheduler)
        print(p_scheduler)
        #might have to move to ready directly instead of processes
        if len(jobs_ready) > 0:
            print("Jobs ready:")
            print(jobs_ready)
            for p in jobs_ready:
                p_scheduler.processes.put((global_time, p.pid, p))
            jobs_ready = []
        global_time += 1
        print("========================================================")
