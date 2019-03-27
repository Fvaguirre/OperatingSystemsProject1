import math
import process
import rand48
import event

def exponentialAvgFunc(rand_num, l):
    return (-1*math.log(rand_num) / l)

def verifyRandomNum(rand_num, upper_bound, l, r):
    while rand_num > upper_bound:
        rand_num = r.drand()
        rand_num = exponentialAvgFunc(rand_num, l)
    return rand_num

def initProcesses(num_processes, upper_bound, seed, l):
    processes = []
    #Seed random num generator
    r = rand48.Rand48(0)
    r.srand(seed)

    count = 0
    # Loop through alphabet for pids
    for pid in range( ord('A'), ord('Z') + 1):
        # If already generated num_processes stop looping through
        if count == num_processes:
            break
        #Generate arrival time
        curr_arrival_time = r.drand()
        curr_arrival_time = exponentialAvgFunc(curr_arrival_time, l)
        curr_arrival_time = verifyRandomNum(curr_arrival_time, upper_bound, l, r)
        curr_arrival_time = math.floor(curr_arrival_time)
        #Generate num of cpu bursts
        curr_num_bursts = r.drand()
        curr_num_bursts = math.trunc((curr_num_bursts*100)) + 1
        p = process.Process(chr(pid), curr_arrival_time, curr_num_bursts)

        # print("Pid: %d with arrival time %d, num_bursts %d has been created!" % (pid, curr_arrival_time, curr_num_bursts))

        #Generate cpu burst times
        for cpu_burst in range(0, curr_num_bursts):
            #Generating burst
            curr_burst_time = r.drand()
            curr_burst_time = exponentialAvgFunc(curr_burst_time, l)
            curr_burst_time = verifyRandomNum(curr_burst_time, upper_bound, l, r)
            curr_burst_time = math.ceil(curr_burst_time)
            #Append it
            p.cpu_burst_times.append(curr_burst_time)
            #Dont generate an io burst time for last cpu burst
            if cpu_burst < curr_num_bursts -1:
                curr_io_burst_time = r.drand()
                curr_io_burst_time = exponentialAvgFunc(curr_io_burst_time, l)
                curr_io_burst_time = verifyRandomNum(curr_io_burst_time, upper_bound, l, r)
                curr_io_burst_time = math.ceil(curr_io_burst_time)
                #Append it
                p.io_burst_times.append(curr_io_burst_time)

        count += 1
        processes.append(p)
        print(p)
    return processes


# def genEvent(type, p, time, q):
#     ret_str = ""
#     if type == "arrival":
#         ret_str = "time %dms: Process %c arrived; added to ready queue %s" %(time, p.pid, q)
#     elif type == "cpu_start":
#         if p.remaining_time > 0:
#             ret_str = "time %dms: Process %c started using the CPU with %dms remaining %s" %(time, process.name, p.remaining_time, q)
#         else:
#             ret_str = "time %dms: Process %c started using the CPU for %dms burst %s" %(time, p.pid , p.cpu_burst_times[p.curr_cpu_burst], q)
#     elif type == "cpu_finish":
#         if p.curr_cpu_burst == p.num_bursts -1:
#              ret_str = "time %dms: Process %c completed a CPU burst; %d burst to go %s" %(time, p.pid, p.num_bursts - p.curr_cpu_burst, q)
#         else:
#             ret_str = "time %dms: Process %c completed a CPU burst; %d bursts to go %s" %(time, p.pid, p.num_bursts - p.curr_cpu_burst, q)
#     elif type == "io_start":
#          ret_str = "time %dms: Process %c switching out of CPU; will block on I/O until time %dms %s" %(time, p.pid, time+p.io_burst_times[p.curr_io_burst_time], q)
#     elif type == "io_finish":
#         ret_str = "time %dms: Process %c completed I/O; added to ready queue %s" %(time, p.pid, q)
#     elif type == "terminated":
#         ret_str = "time %dms: Process %c terminated %s" % (time, p.pid, q)
#     elif type == "preempted":
#         ret_str = "time %dms: Time slice expired; process %c preempted with %dms to go %s" % (time, p.pid, p.remaining_time, q)
#     else:
#         ret_str = "time %dms: Time slice expired; no preemption because ready queue is empty %s" % (time, q)
