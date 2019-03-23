#ifndef CPU_SCHEDULER_FCFS_H
  #define CPU_SCHEDULER_FCFS_H

#include "cpu_scheduler_common.h"

double calcFCFSPriority(process p, int type);
void populateReadyQueue(scheduler* proc_scheduler, int curr_time);
int checkProcState(process* proc, int curr_time);
void populateBlockingQueue(scheduler* proc_scheduler);
scheduler* runFCFS(process* processes, int num_processes, int context_switch_time);
void incrementProcessTimes(scheduler* proc_scheduler);
void checkIOBurstStates(scheduler* proc_scheduler,int curr_time);
int readyQueuetoRunning(scheduler* proc_scheduler);


#endif
