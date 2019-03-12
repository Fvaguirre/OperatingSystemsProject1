#include "cpu_scheduler_common.h"
double verifyRandomNum(int curr_rand, int upper_bound, double lambda){
  while (curr_rand > upper_bound){
    curr_rand = drand48();
    curr_rand = exponentialAvgFunc(curr_rand, lambda);
  }
  return curr_rand;
}
double exponentialAvgFunc(int curr_rand, double lambda){
  return -log(curr_rand) / lambda;
}
process* initProcesses(int num_processes, int upper_bound, int seed, double lambda){
  int pid, cpu_burst;
  double curr_rand;
  fprintf(stdout, "WE GET HERE\n");
  //Init processes array
  process* procs = (process*)calloc(sizeof(process), num_processes);
  //Init rand environement
  srand48(seed);
  for (pid = 0; pid < num_processes; pid++){
    //Set pid
    procs[pid].pid = pid;
    //Set arrival_time
    curr_rand = drand48();
    curr_rand = exponentialAvgFunc(curr_rand, lambda);
    curr_rand = verifyRandomNum(curr_rand, upper_bound);

    fprintf(stdout, "pid: %d\n", pid);

    procs[pid].arrival_time = floor(curr_rand);
    //Set num of cpu bursts
    curr_rand = drand48();
    curr_rand = exponentialAvgFunc(curr_rand, lambda);
    curr_rand = verifyRandomNum(curr_rand, upper_bound);

    procs[pid].num_bursts = trunc((curr_rand*100)) + 1;

    //Init cpu_burst_times && io_burst_times
    procs[pid].cpu_burst_times = (int*)calloc(sizeof(int), procs[pid].num_bursts);
    procs[pid].io_burst_times = (int*)calloc(sizeof(int), procs[pid].num_bursts - 1);

    for (cpu_burst = 0; cpu_burst < procs[pid].num_bursts; cpu_burst++){
      //Generate burst time
      curr_rand = drand48();
      curr_rand = exponentialAvgFunc(curr_rand, lambda);
      curr_rand = verifyRandomNum(curr_rand, upper_bound);

      procs[pid].cpu_burst_times[cpu_burst] = ceil(curr_rand);
      //Dont generate an io_burst_time for the last cpu_burst
      if (cpu_burst < procs[pid].num_bursts - 1){
        //Generate io time
        curr_rand = drand48();
        curr_rand = exponentialAvgFunc(curr_rand, lambda);
        curr_rand = verifyRandomNum(curr_rand, upper_bound);

        procs[pid].io_burst_times[cpu_burst] = ceil(curr_rand);
      }
    }
  }
  return procs;
}
