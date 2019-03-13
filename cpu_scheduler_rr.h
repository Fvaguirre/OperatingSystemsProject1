#ifndef CPU_SCHEDULER_RR_H
  #define CPU_SCHEDULER_RR_H

#include "cpu_scheduler_common.h"

int parseRRQueueType(char* type);
scheduler* runRoundRobin(process* processes, int num_processes, char* rr_queue_type, int rr_time_slice, int context_switch_time);
#endif
