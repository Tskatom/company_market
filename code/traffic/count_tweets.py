from threading import Thread
import Queue

class Count(Thread):
    def __init__(self, queue):
        Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            f = self.queue.get()
            with open(f) as of:
                lines = [n for n in of]
                print len(lines)
            self.queue.task_done()


import glob
files = glob.glob("/home/tskatom/workspace/data/topsy/*")
q = Queue.Queue()
for f in files:
    q.put(f)

for i in range(15):
    t = Count(q)
    t.setDaemon(True)
    t.start()

q.join()
