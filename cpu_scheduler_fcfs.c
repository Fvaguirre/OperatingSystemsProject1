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

void printQ(Node* q){
  if (isEmpty(&q)){
    printf("Its Empty\n");
  }
  else{
    Node* temp = q;
    while(temp != NULL){
      process p = temp->data;
      printf("Process %d, with rem_time %d -> \n", p.pid, p.remaining_time);
      temp = temp->next;
    }
  }
}

void printProc(process* p){
  if (p == NULL){
    fprintf(stderr, "No process\n" );
  }
  else{
    fprintf(stderr, "PID: %d, arrival_time: %d, rem_time: %d\n", p->pid, p->arrival_time, p->remaining_time );
  }
}

int readyJobs(scheduler* s, int global_time){
  int ret = 0;
  double curr_priority;
  if (isEmpty(&s->processes)){
    return ret;
  }
  else{
    while (!isEmpty(&s->processes) && s->processes->data.arrival_time <= global_time){
      curr_priority = calcFCFSPriority(s->processes->data, 0);
      if (isEmpty(&s->readyQueue)){
        s->readyQueue = newNode(s->processes->data, curr_priority);
      }
      else{
        push(&s->readyQueue, s->processes->data, curr_priority);
      }
      pop(&s->processes);
      ret++;
    }
    return ret;
  }
}

process runJob(scheduler* s){
  process moving;
  int curr_burst;
  if (s->running->pid == -1){
    if (!isEmpty(&s->readyQueue)){
      moving = peek(&s->readyQueue);
      curr_burst = moving.curr_cpu_burst;
      moving.remaining_time = moving.cpu_burst_times[curr_burst];
      pop(&s->readyQueue);
      // return 0;
    }
    return moving;
  }
  //Else there is already a job that is running!
  else{
    s->running->remaining_time--;
    return 1;
  }
}

int checkRunningJobState(scheduler* s){
  if (s->running->pid = -1){
    return -1;
  }
  else{
    if (s->running->remaining_time <= 0){
      s->running->remaining_time = 0;
      //Increment curr_cpu_burst
      s->running->curr_cpu_burst++;
      return 1;
    }
    else{
      return 0;
    }
  }
}

int moveJobToBlocking(scheduler* s){
  //Set rem_time to remaining i_o burst
  int curr_io = s->running->curr_io_burst;
  printProc(s->running);
  fprintf(stderr, "Curr io %d\n",curr_io );
  s->running->remaining_time = s->running->io_burst_times[curr_io];
  double blocking_priority = calcFCFSPriority(*(s->running),1);

  //If empty make newNode
  if (isEmpty(&s->blockingQueue)){
    perror("WE HERE in block");

    s->blockingQueue = newNode(*(s->running), blocking_priority);
  }
  else{
    push(&s->blockingQueue, *(s->running), blocking_priority);
  }
  s->running = NULL;

}

scheduler* runFCFS(process* processes, int num_processes, int context_switch_time){

  int jobs_completed = 0;
  scheduler* proc_scheduler = initScheduler(processes, num_processes);
  proc_scheduler->running = calloc(1, sizeof(process));
  proc_scheduler->running->pid = -1;
  int global_time = 0;
  int jobs_added = 0;
  int move_to_running = 0;
  int is_done;
  global_time = 2 ;
  jobs_added = readyJobs(proc_scheduler, global_time);
  fprintf(stderr, "Jobs added: %d\n", jobs_added );
  printQ(proc_scheduler->readyQueue);
  move_to_running = runJob(proc_scheduler);
  fprintf(stderr, "Moved ret: %d\n", move_to_running );
  printProc(proc_scheduler->running);
  printQ(proc_scheduler->readyQueue);
  move_to_running = runJob(proc_scheduler);
  move_to_running = runJob(proc_scheduler);
  move_to_running = runJob(proc_scheduler);

  printProc(proc_scheduler->running);
  printProc(proc_scheduler->running);
  printProc(proc_scheduler->running);
  // proc_scheduler->running->remaining_time = 10;
  // printProc(proc_scheduler->running);



  is_done = checkRunningJobState(proc_scheduler);
  printProc(proc_scheduler->running);
  fprintf(stderr, "LISTEN: pid: %d, rem_time: %d\n", proc_scheduler->running->pid, proc_scheduler->running->remaining_time);

  if (is_done == 1){
    fprintf(stderr, "FINISHED\n" );
    fprintf(stderr, "LISTEN: pid: %d, rem_time: %d\n", proc_scheduler->running->pid, proc_scheduler->running->remaining_time);
    //
    // printProc(proc_scheduler->running);
    // moveJobToBlocking(proc_scheduler);
    // perror("WE HERE");
    // printProc(proc_scheduler->running);

  }
  else{
    fprintf(stderr, "%d\n",is_done );
  }








  // global_time = 6;
  // jobs_added = readyJobs(proc_scheduler, global_time);
  // fprintf(stderr, "Jobs added: %d\n", jobs_added );
  // printQ(proc_scheduler->readyQueue);


  // while (jobs_complete < proc_schduler->num_jobs){
  //   jobs_added = readyJobs(proc_scheduler, global_time);
  //   fprintf(stderr, "Jobs added: %d\n", jobs_added );
  //   move_to_running = runJob(proc_scheduler);
  //   is_done = checkRunningJobState(proc_scheduler);
  //   if (is_done == 1){
  //     //Move running to blockingQueue
  //     moveJobToBlocking(proc_scheduler, global_time);
  //   }
  //
  // }
}
