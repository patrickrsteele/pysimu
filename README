pysimu
------

A simulation framework in Python. The goal of this project is to offer
a simple framework for writing simulation code in Python. pysimu
handles running multiple trials of a simulation, allocating random
number streams to each trial, aggregating the results, and
(eventually) running the trials in parallel.

A simple example
----------------

    from __future__ import division
    from pysimu import Model
    
    model = Model()
    model.trial = lambda model, rand: rand.random() > .5
    model.ntrials = 100
    model.successes = 0
    def process_result(model, result):
        if result:
            model.successes += 1
    model.process_result = process_result
    model.simulate()
    print model.successes / model.ntrials

This program would simulate flipping a fair coin 100 times, storing
the number of heads flipped in `model.successes`.
