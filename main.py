import sys
# import math
import fcfs

import common
import scheduler

if __name__ == '__main__':
    seed = int(sys.argv[1])
    l = float(sys.argv[2])
    upper_bound = int(sys.argv[3])
    num_processes = int(sys.argv[4])
    context_switch_time = int(sys.argv[5])
    alpha = float(sys.argv[6])
    rr_time_slice = int(sys.argv[7])
    rr_queue_type = sys.argv[8]

    processes = common.initProcesses(num_processes, upper_bound, seed, l)

    # p_scheduler = scheduler.Scheduler(processes)
    fcfs.runFCFS(processes, num_processes, context_switch_time)


    # print(p_scheduler.processes.queue)
    # print(p_scheduler.processes.get())
