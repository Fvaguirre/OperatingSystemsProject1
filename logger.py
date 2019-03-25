class Logger(object):
    def __init__(self):
        self.cpu_time = 0
        self.wait_time = 0
        self.turnaround = 0
        self.num_context_switches = 0
        self.num_premptions = 0
