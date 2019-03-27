import process, scheduler, logger, fcfs, event

# Returns -1 if running is None' 1 if running process is done, 0 if running process will be
# preempted and 2 if the running process is good for another tick
def checkRunningJobState(p_scheduler, rr_time_slice, curr_elapsed, global_time):
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
            r_q = p_scheduler.returnPrintableReadyQueue()
            output = event.Event("cpu_finish", global_time, p_scheduler.running, r_q)
            p_scheduler.addEvent(output)

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
    p_scheduler.logger[p_scheduler.running.pid].num_context_switches += 1
    p_scheduler.running = None
    global_time = fcfs.runContextSwitch(p_scheduler, global_time, context_switch_time)
    return global_time


def runPreemption(p_scheduler, global_time, rr_queue_type, context_switch_time):
    p_scheduler.logger[p_scheduler.running.pid].num_premptions += 1
    global_time = fcfs.runContextSwitch(p_scheduler, global_time, context_switch_time)
    global_time = preemptProcess(p_scheduler, rr_queue_type, global_time, context_switch_time)
    return global_time
def preemption(p_scheduler, global_time, rr_queue_type):
    if rr_queue_type == 'END':
        priority_metric = global_time
    else:
        priority_metric = float(1.0/global_time)
    p_scheduler.logger[p_scheduler.running.pid].num_premptions += 1

    r_q = p_scheduler.returnPrintableReadyQueue()
    output = event.Event("preempted", global_time, p_scheduler.running, r_q)
    p_scheduler.addEvent(output)

    p_scheduler.ready_queue.put((priority_metric, p_scheduler.running.pid, p_scheduler.running))
    p_scheduler.logger[p_scheduler.running.pid].num_context_switches += 1
    p_scheduler.running = None


def runRR(processes, num_processes, context_switch_time, rr_time_slice, rr_queue_type):
    global_time = 0
    jobs_completed = 0
    p_scheduler = scheduler.Scheduler(processes, rr_queue_type)
    time_slice = 0
    in_context_switch = False
    context_switch_counter = 0
    just_moved = False


    while jobs_completed < num_processes:

        # if in_context_switch:
        #     p_scheduler.events.append("IN CONTEXT SWITCH!!!")
        #     p_scheduler.events.append("Context switch counter: %d" % context_switch_counter)

        if context_switch_counter == .5*context_switch_time:
            in_context_switch = False
            context_switch_counter = 0
            just_moved = False
        # print("GLOBAL TIME: %d" % global_time)
        # print("Time_slice: %d" % time_slice)
        # print("Before readyJobs:")
        # print(p_scheduler)

        jobs_readied = fcfs.readyJobs(p_scheduler, global_time)
        if jobs_readied > 0 and p_scheduler.running is None:
            in_context_switch = True

        if not in_context_switch:

            run_job_rc = fcfs.runJob(p_scheduler, global_time)

            if run_job_rc == 0:
                 #process first half of context_switch_time
                 p_scheduler.logger[p_scheduler.running.pid].num_context_switches += 1
                 time_slice = 0
                 in_context_switch = True

            running_state = checkRunningJobState(p_scheduler, rr_time_slice, time_slice, global_time)

            # time for preemption
            if running_state == 0 and not p_scheduler.ready_queue.empty():
                #reset time_slice
                time_slice = 0
                # global_time = runPreemption(p_scheduler, global_time, rr_queue_type, context_switch_time)
                p_scheduler.logger[p_scheduler.running.pid].num_premptions += 1
                in_context_switch = True
                preemption(p_scheduler, global_time, rr_queue_type)

            elif running_state == 1:
                if p_scheduler.running.finished == True:
                    jobs_completed += 1
                    time_slice = 0
                    fcfs.logTimes(p_scheduler)
                    p_scheduler.running = None
                else:
                    fcfs.moveRunningToBlocking(p_scheduler, global_time)
                    in_context_switch = True
                    just_moved = True

        if in_context_switch and just_moved:
            # Tick time from all but last process
            p = None
            if len(p_scheduler.blocking) > 0:
                p = p_scheduler.blocking[-1]
            jobs_ready = fcfs.runIO(p_scheduler, p)
        else:
            jobs_ready = fcfs.runIO(p_scheduler)

        fcfs.requeuefromBlocking(p_scheduler, jobs_ready, global_time)

        fcfs.tickWaitTime(p_scheduler)
        if in_context_switch:
            context_switch_counter += 1

        global_time += 1
        if not in_context_switch and p_scheduler.running is not None:
            time_slice += 1

    logs = p_scheduler.logger
    print(logs)
    all_bursts = 0
    all_times = 0
    for p in processes:
        all_bursts += p.num_bursts
        all_times += sum(p.cpu_burst_times)
    c_s = 0
    preemptions = 0
    for key, val in logs.items():
        c_s += val.num_context_switches
        preemptions += val.num_premptions
    p_scheduler.printEvents()
    print("Average CPU burst:")
    print(all_times/all_bursts)
    print("Context Switches: %d" % c_s)
    print("Preemptions: %d" % preemptions)
