import process
class Event(object):
    def __init__(self, type, time, p, q):
        self.type = type
        self.text = ""
        self.time = time
        if type == "arrival":
          self.text = "time %dms: Process %c arrived; added to ready queue %s" %(time, p.pid, q)
        elif type == "cpu_start":
          if p.remaining_time > 0:
              self.text = "time %dms: Process %c started using the CPU with %dms remaining %s" %(time, p.pid, p.remaining_time, q)
          else:
              self.text = "time %dms: Process %c started using the CPU for %dms burst %s" %(time, p.pid , p.cpu_burst_times[p.curr_cpu_burst], q)
        elif type == "cpu_finish":
          if p.curr_cpu_burst == p.num_bursts -1:
               self.text = "time %dms: Process %c completed a CPU burst; %d burst to go %s" %(time, p.pid, p.num_bursts - p.curr_cpu_burst, q)
          else:
              self.text = "time %dms: Process %c completed a CPU burst; %d bursts to go %s" %(time, p.pid, p.num_bursts - p.curr_cpu_burst, q)
        elif type == "io_start":
           self.text = "time %dms: Process %c switching out of CPU; will block on I/O until time %dms %s" %(time, p.pid, time+p.io_burst_times[p.curr_io_burst], q)
        elif type == "io_finish":
          self.text = "time %dms: Process %c completed I/O; added to ready queue %s" %(time, p.pid, q)
        elif type == "terminated":
          self.text = "time %dms: Process %c terminated %s" % (time, p.pid, q)
        elif type == "preempted":
          self.text = "time %dms: Time slice expired; process %c preempted with %dms to go %s" % (time, p.pid, p.remaining_time, q)
        else:
          self.text = "time %dms: Time slice expired; no preemption because ready queue is empty %s" % (time, q)
    def __str__(self):
        return self.text
    def __repr__(self):
        return self.__str__()
