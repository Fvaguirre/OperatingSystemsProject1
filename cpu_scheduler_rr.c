#include "cpu_scheduler_rr.h"
// #include "cpu_scheduler_common.h"

int parseRRQueueType(char* type){
  if (strcmp(type, "BEGINNING") == 0){
    return 0;
  }
  else if (strcmp(type, "END") == 0){
    return 1;
  }
  else{
    return -1;
  }
}
// double calcRRPriority(process proc){
//   if (proc.pid == 0){
//     return proc.arrival_time - 1.0/.9;
//   }
//   else{
//     return proc.arrival_time - 1.0/proc.pid;
//   }
// }
// void populateReadyQueue(scheduler* proc_scheduler, int curr_time){
//   process next_proc = peek(&proc_scheduler->processes);
//   int next_arrival_time = next_proc.arrival_time;
//   //ReadyQueue priority priority_metric
//   double next_readyQ_priority;
//
//   while (curr_time <= next_arrival_time){
//     next_readyQ_priority = calcRRPriority(next_proc);
//     //Case that readyQueue is is empty
//     if (isEmpty(&proc_scheduler->readyQueue)){
//       proc_scheduler->readyQueue = newNode(next_proc, next_readyQ_priority);
//     }
//     else{
//       push(&proc_scheduler->readyQueue, next_proc, next, readyQ_priority);
//     }
//     //Print out that something was added to readyQueue
//   }
// }
// void resetCurrentRuntime(scheduler* proc_scheduler){
//   proc_scheduler->curr_runtime = 0;
//
// }
// void stopRunningProcess(scheduler* proc_scheduler{
//   process* prev_proc = proc_scheduler->running;
//   double priority_metric = calcRRPriority(prev_proc);
//   //if the prev process finished at the last second of its time rr_time_slice
//   if (prev_proc->cpu_burst_times[curr_cpu_burst] == 0){
//     //
//   }
//   //Check if process will go back to readyQueue or to blockingQueue
//   //If the curr_cpu_burst > 0 that means a preemption occured!
//   if (prev_proc->cpu_burst_times[curr_cpu_burst] > 0){
//     //Check if readyQueue is isEmpty
//     if (isEmpty(proc_scheduler->readyQueue)){
//       //Reinit readyQueue using newNode()
//       proc_scheduler
//     }
//   }
// }
// void runNextProcess(scheduler* proc_scheduler, int rr_time_slice, int *rem_time, int curr_time){
//   process next_proc;
//   //If rem_time equals rr_time_slice that means that the rem_time was reset
//   if (*rem_time == rr_time_slice){
//     //So go ahead and remove whatever proc was running before and add the next proc to run
//     //Check if running process is not NULL
//     if (proc_scheduler->running != NULL){
//       //if not null remove previously running process
//       prev_proc = proc_scheduler->running;
//       stopRunningProcess(proc_scheduler, RR_type);
//     }
//     //there are no active processes running
//     else{
//       //So peek at process with highest priority in readyQueue and add it to running
//       proc_scheduler->running =
//       next_proc = peek(&proc_scheduler->readyQueue);
//       //Now remove it from readyQueue
//       pop(&proc_scheduler->readyQueue);
//     }
//   }
// }
scheduler* runRoundRobin(process* processes, int num_processes, char* rr_queue_type, int rr_time_slice, int context_switch_time){
  int RR_type = parseRRQueueType(rr_queue_type);
  // if (RR_type == 1){
  //
  // }
  // else{
  //
  // }
  // Generate process scheduler
  scheduler* proc_scheduler = initScheduler(processes, num_processes);

  //Init curr time slice counter
  // int rem_time = rr_time_slice;
  // //Init curr_time counter
  // int curr_time = 0;
  // //Init temp proc
  // process curr_process = peek(&proc_scheduler->processes);
  // //Init temp arrival_time holder
  // int curr_arrival_time = curr_process.arrival_time;
  // //ReadyQueue priority priority_metric
  // double readyQ_priority = curr_arrival_time - 1.0/.9;
  //
  //
  // //init proc_scheduler readyQueue
  // proc_scheduler.readyQueue = newNode(curr_process, readyQ_priority);
  //
  // //Here is where we run the actual algorithm
  // while (!isEmpty(&proc_scheduler->processes) || !isEmpty(&proc_scheduler->readyQueue) || !isEmpty(&proc_scheduler->blockingQueue)){
  //   //Check process list against curr_time!
  //   populateReadyQueue(proc_scheduler, curr_time);
  //   runNextProcess(proc_scheduler, curr_time, &curr_time_slice);
  //   //Increment time
  //   curr_time++;
  // }

  return proc_scheduler;
}
