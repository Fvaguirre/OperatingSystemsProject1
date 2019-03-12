
#include <time.h>

#include "cpu_scheduler_common.h"

#define MAX_NUM_PROCS 26


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

int main(int argc, char** argv){
  int seed, upper_bound, num_processes;
  int context_switch_time, rr_time_slice;
  char* rr_queue_type;
  double lambda, alpha;

  seed = atoi(argv[1]);
  lambda = atof(argv[2]);
  upper_bound = atoi(argv[3]);
  num_processes = atoi(argv[4]);
  context_switch_time = atoi(argv[5]);
  alpha = atof(argv[6]);
  rr_time_slice = atoi(argv[7]);
  rr_queue_type = argv[8];

  process* processes = initProcesses(num_processes, upper_bound, seed, lambda);
  for (int i = 0; i < num_processes; i++){
    printf("PROC %d: has %d num_bursts\n",processes[i].pid, processes[i].num_bursts);
  }
}
