# coding:utf-8


from multiprocessing import pool
import os, random, time


def run_task(name):
    print 'Task %s (pid = %s) is running...' % (name, os.getpid())
    time.sleep(random.random()*3)
    print 'Task %s end.' % name

if __name__ == '__main__':
    print 'Current process %s.' % os.getpid()
    p = pool(processes=3)
    for i in range(5):
        p.apply_async(target=run_task, args=(i,))
    print 'waiting for all subprocesses done...'
    p.close()
    p.join()
    print 'All subprocesses done.'
