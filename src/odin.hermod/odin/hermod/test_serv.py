from os.path import isdir
from pyinotify import WatchManager,ProcessEvent, ThreadedNotifier, IN_ISDIR, IN_CREATE, IN_CLOSE_WRITE, IN_MOVED_TO
from time import sleep
import threading
import Queue

from pkg_resources import resource_filename
import logging
from odin.config.environment import set_hermod_logging


class EventHandler(ProcessEvent):
    def __init__(self):
        self.logger = logging.getLogger('filesystem list')
    def process_IN_CREATE(self, event):
        if isdir(event.pathname):
            self.logger.info("Detected new directory: {0}".format(event.pathname))
            wm.add_watch(event.pathname,IN_CREATE|IN_MOVED_TO, rec=True)
        else:
            self.logger.info('Adding to processing queue: {0}'.format(event.pathname))
            queue.put(event.pathname)

    def process_IN_MOVED_TO(self, event):
        self.logger.info('Adding to processing queue: {0}'.format(event.pathname))
        queue.put(event.pathname)

class Worker(threading.Thread):
    def __init__(self,queue):
        self.logger = logging.getLogger('worker process')
        self.queue = queue
        threading.Thread.__init__(self)
        self.logger.debug('started worker')

    def run(self):
        while 1:
            f = self.queue.get()
            
            self.logger.info('processing file {0}'.format(f))
            self.queue.task_done()

if __name__=='__main__':
    set_hermod_logging()
    logger = logging.getLogger('hermod_filewatcher')
    logger.info('starting testserver')
    queue = Queue.Queue()
    worker = Worker(queue)
    worker.daemon = True
    worker.start()
    wm = WatchManager()
    handler = EventHandler()
    notifier = ThreadedNotifier(wm, handler)
    directory = '/misc/pearl/odin/level1b'
    wdd = wm.add_watch(directory, IN_CREATE | IN_MOVED_TO, rec=True)
    logger.info('watching {0}'.format(directory))
    notifier.start()
    while 1:
        try:
            sleep(60)
            logger.debug('mark - active processes {}'.format(threading.active_count()))
        except KeyboardInterrupt:
            logger.warn('C-c pressed exiting')
            break
    logger.info('Waiting for worker to finish')
    queue.join()
    notifier.stop()
    logger.info('all jobs done.  normal exit')

