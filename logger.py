class Logger(object):
    def __init__(self):
        self.avg_cpu_time = 0
        self.avg_wait_time = 0
        self.avg_turnaround = 0
        self.num_context_switches = 0
        self.num_premptions = 0
