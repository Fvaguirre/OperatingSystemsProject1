import sys
# import math
import fcfs
import rr

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

    # processes = common.initProcesses(num_processes, upper_bound, seed, l)
    ##########################################################################
    # Processes to debug with: comment out line 19 above and uncomment this section
    # processes = []
    # p = scheduler.process.Process(0, 0, 3)
    # p.cpu_burst_times.append(1)
    # p.cpu_burst_times.append(2)
    # p.cpu_burst_times.append(4)
    # p.io_burst_times.append(3)
    # p.io_burst_times.append(2)
    # # p.io_burst_times.append(1)
    # processes.append(p)
    #
    # p = scheduler.process.Process(1, 1, 3)
    # p.cpu_burst_times.append(2)
    # p.cpu_burst_times.append(2)
    # p.cpu_burst_times.append(5)
    # p.io_burst_times.append(1)
    # p.io_burst_times.append(2)
    #
    # processes.append(p)

    # fcfs.runFCFS(processes, num_processes, context_switch_time)
    print()
    print()
    ###############################################################################
    # Processes to debug with: comment out line 65 below and uncomment this section
    # processes = []
    # p = scheduler.process.Process('A', 0, 3)
    # p.cpu_burst_times.append(1)
    # p.cpu_burst_times.append(2)
    # p.cpu_burst_times.append(4)
    # p.io_burst_times.append(3)
    # p.io_burst_times.append(2)
    # # p.io_burst_times.append(1)
    # processes.append(p)
    #
    # p = scheduler.process.Process('B', 1, 3)
    # p.cpu_burst_times.append(2)
    # p.cpu_burst_times.append(2)
    # p.cpu_burst_times.append(5)
    # p.io_burst_times.append(1)
    # p.io_burst_times.append(2)
    #
    # processes.append(p)
    #
    # p = scheduler.process.Process('C', 0, 1)
    # p.cpu_burst_times.append(5)
    #
    # processes.append(p)
    #
    # p = scheduler.process.Process('D', 5, 2)
    # p.cpu_burst_times = [3, 1]
    # p.io_burst_times = [5]
    #
    # processes.append(p)
    #
    # p = scheduler.process.Process('E', 10, 3)
    # p.cpu_burst_times = [2, 2, 1]
    # p.io_burst_times = [1, 3]
    #
    # processes.append(p)
    #
    # p = scheduler.process.Process('F', 6, 10)
    # p.cpu_burst_times = [1, 2, 1, 5, 20, 10, 9, 5, 10, 13]
    # p.io_burst_times = [5, 2, 1, 12, 10, 2, 5, 6, 14]
    #
    # processes.append(p)
    # p = scheduler.process.Process('G', 0, 10)
    # p.cpu_burst_times = [10, 12, 1,2, 10, 1, 1, 1, 10, 5 ]
    # p.io_burst_times = [5, 20, 1, 1, 1, 3, 4, 1, 5]
    #
    # processes.append(p)
    #
    #
    # context_switch_time = 4
    # rr_time_slice = 6
    #
    # num_processes = 7


    # We need to reinit the processes before we run them through an algo again
    processes = common.initProcesses(num_processes, upper_bound, seed, l)

    rr.runRR(processes, num_processes, context_switch_time, rr_time_slice, rr_queue_type)
