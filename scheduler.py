import queue
import process
import logger, event

class Scheduler(object):
    def __init__(self, processes, rr_type = 'END'):
        self.logger = dict()
        self.events = []

        self.rr_type = rr_type
        self.processes = queue.PriorityQueue()
        self.ready_queue = queue.PriorityQueue()
        self.running = None
        self.blocking = []
        if self.rr_type == 'END':
            for p in processes:
                self.processes.put((p.arrival_time, p.pid, p))
                self.logger[p.pid] = logger.Logger()
        else:
            for p in processes:
                self.processes.put((1/(p.arrival_time + .0001), p.pid, p))
                self.logger[p.pid] = logger.Logger()

    def __str__(self):
        return "Processes Queue: \n" + str(self.processes.queue) + "\nReady Queue: \n" +\
        str(self.ready_queue.queue) + "\nRunning : \n" + str(self.running) + "\n Blocking: \n" +\
        str(self.blocking) + "\n"

    def printArrivals(self):
        temp = queue.PriorityQueue()
        while not self.processes.empty():
            curr = self.processes.get()
            print("Process %c [NEW] (arrival time %d ms) %d CPU bursts" % (curr[1], curr[2].arrival_time, curr[2].num_bursts))
            temp.put(curr)
        self.processes = temp

    def returnPrintableReadyQueue(self):
        if self.ready_queue.empty():
            return "[Q <empty>]"
        temp = queue.PriorityQueue()
        ret = "[Q "
        while not self.ready_queue.empty():
            curr = self.ready_queue.get()
            ret += curr[1]
            if not self.ready_queue.empty():
                ret += " "
            temp.put(curr)
        self.ready_queue = temp
        ret += "]"

        return ret

    def addEvent(self, e):
        self.events.append(e)
    def printEvents(self):
        for i in self.events:
            print(i)
