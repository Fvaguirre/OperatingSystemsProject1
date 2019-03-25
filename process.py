class Process(object):
  def __init__(self, pid, arrival_time, num_bursts):
      self.pid = pid
      self.arrival_time = arrival_time
      self.num_bursts = num_bursts
      self.finished = False
      self.cpu_burst_times = []
      self.io_burst_times = []
      self.remaining_time = 0
      self.curr_io_burst = 0
      self.curr_cpu_burst = 0

  def __str__(self):
      return "{Pid: " + str(self.pid) + ", arrived: " + str(self.arrival_time) + ", num_bursts: " +\
        str(self.num_bursts) + ", Finished: " + str(self.finished) + ", Rem time: " +\
        str(self.remaining_time) + ", curr_io_burst: " + str(self.curr_io_burst) + ", curr_cpu_burst: "\
        + str(self.curr_cpu_burst) + "}"
  def __repr__(self):
      return self.__str__();
