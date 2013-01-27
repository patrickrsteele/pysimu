from random import Random

class Model(object):
    """
    A simulation model.

    """

    def __init__(self, name=None, **kwds):
        self.name = name

        self.ntrials = kwds.pop("ntrials", None)
        self.trial = kwds.pop("trial", None)
        self.seed = kwds.pop("seed", None)

        if len(kwds) > 0:
            msg = "Unknown keyword arguments: %s" % str(kwds.keys())[1:-1]
            raise TypeError(msg)

    def simulate(self):
        if self.ntrials is None:
            msg = "Model attribute 'ntrials' must be specified"
            raise ValueError(msg)
        if self.trial is None:
            msg = "Model attribute 'trial' must be specified"
            raise ValueError(msg)

        self.results = []
        
        for n in xrange(0, self.ntrials):
            rand = Random()
            rand.seed(self.seed)
            rand.jumpahead(n)

            self.results.append(self.trial(rand))
