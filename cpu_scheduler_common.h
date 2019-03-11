#ifndef CPU_SCHEDULER_COMMON_H
  #define CPU_SCHEDULER_COMMON_H

#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <math.h>

typedef struct {
  int pid;
  double arrival_time;
  double expected_runtime;
  double remaining_time;
  int priority;
  int num_bursts;
  int* cpu_burst_times;
  int* io_burst_times;
} process;

double verifyRandomNum(int curr_rand, int upper_bound);
process* initProcesses(int num_processes, int upper_bound, int seed);

#endif
