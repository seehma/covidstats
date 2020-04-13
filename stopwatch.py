#!/usr/b in/python

import time


class stopwatch:

    def __init__(self):
        self.starTime = 0

    def tic(self):
        self.startTime = time.time()

    def toc(self):
        return time.time() - self.startTime
