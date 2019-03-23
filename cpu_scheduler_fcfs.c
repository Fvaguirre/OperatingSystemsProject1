#include "cpu_scheduler_fcfs.h"
//If type == 0, then calc with arrival else calc with rem_time
double calcFCFSPriority(process p, int type){
  int metric = p.remaining_time;
  if (type == 0){
    metric = p.arrival_time;
  }
  if (p.pid == 0){
    return metric - 1.0/.9;
  }
  else{
    return metric - 1.0/p.pid;
  }
}
void populateReadyQueue(scheduler* proc_scheduler, int curr_time){
  process curr_proc = peek(&proc_scheduler->processes);
  int curr_proc_arrival = curr_proc.arrival_time;
  // fprintf(stderr, "IM HERE %d\n", curr_proc_arrival );

  double curr_proc_priority;
  // fprintf(stderr, "IM HERE\n" );

  while (curr_proc_arrival <= curr_time){
    curr_proc_priority = calcFCFSPriority(curr_proc, 0);
    fprintf(stderr, "curr_proc pid: %d , curr_proc arrival: %d \n", curr_proc.pid, curr_proc.arrival_time );


    if (isEmpty(&proc_scheduler->readyQueue)){
      proc_scheduler->readyQueue = newNode(curr_proc, curr_proc_priority);
    }
    else{
      push(&proc_scheduler->readyQueue, curr_proc, curr_proc_priority);
    }
    //Finally pop from the processes list
    pop(&proc_scheduler->processes);
    //Update curr_proc and curr_proc arrival to continue while loop
    curr_proc = peek(&proc_scheduler->processes);
    curr_proc_arrival = curr_proc.arrival_time;
  }
}
int checkProcState(process* proc, int curr_time){
  int ret_state;
  if (proc->remaining_time == 0){
    //Processes is done so return 1
    ret_state = 1;
  }
  else{
    ret_state = 0;
  }

  return ret_state;
}
void populateBlockingQueue(scheduler* proc_scheduler){
  process curr_proc = *(proc_scheduler->running);
  double blocking_priority = calcFCFSPriority(curr_proc, 1);
  printf("IM HERE\n" );
  //Set remaining time to remaining io burst time
  curr_proc.curr_io_burst++;
  curr_proc.remaining_time = curr_proc.io_burst_times[curr_proc.curr_io_burst-1];
  if (isEmpty(&proc_scheduler->blockingQueue)){
    proc_scheduler->blockingQueue = newNode(curr_proc, blocking_priority);
  }
  else{
    push(&proc_scheduler->blockingQueue, curr_proc, blocking_priority);
  }
}

int readyQueuetoRunning(scheduler* proc_scheduler){
  process* proc = (process*)calloc(1, sizeof(process));
  process p;
  if (isEmpty(&proc_scheduler->readyQueue)){
    return 1;
  }
  else{
    p = peek(&proc_scheduler->readyQueue);
    proc = &p;
    //Set remaining cpu burst time
    proc->curr_cpu_burst ++;
    proc->remaining_time = proc->cpu_burst_times[proc->curr_cpu_burst-1];

    proc_scheduler->running = proc;
    pop(&proc_scheduler->readyQueue);
    return 0;
  }
}

void checkIOBurstStates(scheduler* proc_scheduler,int curr_time){
  process curr_process;
  int rem_time;
  if (!isEmpty(&proc_scheduler->blockingQueue)){
    curr_process = peek(&proc_scheduler->blockingQueue);
    rem_time = curr_process.remaining_time;
    while (rem_time == 0){
      pop(&proc_scheduler->blockingQueue);
      //Add curr_proc to readyQueue
      if (isEmpty(&proc_scheduler->readyQueue)){
        proc_scheduler->readyQueue = newNode(curr_process, curr_time);
      }
      else{
        push(&proc_scheduler->readyQueue, curr_process, curr_time);
      }
      //update curr_proc and rem time
      if (!isEmpty(&proc_scheduler->blockingQueue)){
        curr_process = peek(&proc_scheduler->blockingQueue);
        rem_time = curr_process.remaining_time;
      }
      else{
        proc_scheduler->blockingQueue = NULL;
      }
    }
  }
}

void incrementProcessTimes(scheduler* proc_scheduler){
  Node* temp = NULL;
  if (proc_scheduler->running != NULL){
    perror("Before decrement");
    (proc_scheduler->running->remaining_time)--;
    perror("After decrement");
    if (proc_scheduler->running->remaining_time < 0){
      proc_scheduler->running->remaining_time = 0;
    }
  }


  if (!isEmpty(&proc_scheduler->blockingQueue)){
    process p = peek(&proc_scheduler->blockingQueue);
    p.remaining_time--;
    temp = newNode(p, proc_scheduler->blockingQueue->priority);
    while (!isEmpty(&proc_scheduler->blockingQueue)){
      pop(&proc_scheduler->blockingQueue);
      p = peek(&proc_scheduler->blockingQueue);
      p.remaining_time--;
      push(&temp, p, calcFCFSPriority(p, 1));
    }
  }
  proc_scheduler->blockingQueue = temp;
}

void printQ(Node* q){
  if (isEmpty(&q)){
    printf("Its Empty\n");
  }
  else{
    while(!isEmpty(&q)){
      process p = peek(&q);
      printf("Process %d, with rem_time %d -> \n", p.pid, p.remaining_time);
      pop(&q);
    }
  }
}

scheduler* runFCFS(process* processes, int num_processes, int context_switch_time){
  // fprintf(stderr, "IM HERE\n" );

  scheduler* proc_scheduler = initScheduler(processes, num_processes);


  int curr_time = 0;

  int curr_running_proc_state = 0;
  int rc;

  while (!isEmpty(&proc_scheduler->readyQueue) || proc_scheduler->running != NULL || !isEmpty(&proc_scheduler->blockingQueue) || !isEmpty(&proc_scheduler->processes)){
    //Check if you can move processes from processes queue to readyqueue
    if (!isEmpty(&proc_scheduler->processes)){
      perror("Before populate queue");
      populateReadyQueue(proc_scheduler, curr_time);

      printQ(proc_scheduler->readyQueue);

    }
    //Check the state of the current processes at curr_time
    // curr_running_proc_state = checkProcState(proc_scheduler->running, curr_time);
    if (proc_scheduler->running == NULL){
      perror("CABBAGE");
      //Then add highest priority proc from ready queue
      rc = readyQueuetoRunning(proc_scheduler);
      if (rc == 1){
        // perror("READY is empty @ time %d\n", curr_time);
      fprintf(stderr, "READY is empty @ time %d\n",curr_time );      fprintf(stderr, "PID: %d has arrival time %d and rem_time %d\n", proc_scheduler->running->pid, proc_scheduler->running->arrival_time, proc_scheduler->running->remaining_time );

      }
      else{
        fprintf(stderr, "PID: %d has arrival time %d and rem_time %d\n", proc_scheduler->running->pid, proc_scheduler->running->arrival_time, proc_scheduler->running->remaining_time );
      }
    }
    else{
      //Check the state of the current processes at curr_time
      if (proc_scheduler->running != NULL){
        curr_running_proc_state = checkProcState(proc_scheduler->running, curr_time);
      }
      //If curr running process finished
      if (curr_running_proc_state == 1){
        //Move running to blocking
        populateBlockingQueue(proc_scheduler);
      }
      //Else keep running the current process;f
    }

    //Check blocking queue io bursts at curr_time
    if (!isEmpty(&proc_scheduler->blockingQueue)){
      checkIOBurstStates(proc_scheduler, curr_time);
    }
    perror("AT THE END");
    incrementProcessTimes(proc_scheduler);
    perror("==================================================");








    //
    curr_time++;
  }
}
