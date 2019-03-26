import queue
import process
import logger

class Scheduler(object):
    def __init__(self, processes, rr_type = 'END'):
        self.logger = dict()

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
        str(self.blocking)
