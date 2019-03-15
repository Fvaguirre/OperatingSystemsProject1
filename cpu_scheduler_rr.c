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

scheduler* runRoundRobin(process* processes, int num_processes, char* rr_queue_type, int rr_time_slice, int context_switch_time){
  int RR_type = parseRRQueueType(rr_queue_type);
  // if (RR_type == 1){
  //
  // }
  // else{
  //
  // }
  scheduler* proc_scheduler = initScheduler(processes, num_processes);
  //init proc_scheduler readyQueue
  proc_scheduler.readyQueue = newNode(peek(&proc_scheduler->processes),
  //Here is where we run the actual algorithm
  while (!isEmpty(&proc_scheduler->readyQueue) && proc_scheduler->running != NULL && blockingQueue != NULL ){
    
  }

  return proc_scheduler;
}
