class Logger(object):
    def __init__(self):
        self.cpu_time = 0
        self.wait_time = 0
        self.turnaround_times = []
        self.num_context_switches = 0
        self.num_premptions = 0
    def __str__(self):
        return "CPU time: " + str(self.cpu_time) + "\n" +\
        "Wait time: " + str(self.wait_time) + "\n" +\
        "Turnarounds: " + str(self.turnaround_times) + "\n" +\
        "Context Switches: " + str(self.num_context_switches) + "\n" +\
        "Premptions: " + str(self.num_premptions) + "\n"
    def __repr__(self):
        return self.__str__()
