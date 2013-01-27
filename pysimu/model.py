from random import Random
import types

class Model(object):
    """
    A simulation model. The `trial' attribute of the model, which
    should take an instance of random.Random as an argument, should
    perform a single simulation. The `simulate' method will perform
    this simulation a number of times, specified by the `ntrials'
    attribute.

    Example:

      >>> m = Model()
      >>> m.trial = lambda model, r: r.random() > .5
      >>> m.ntrials = 3
      >>> m.simulate()
      >>> print m.results # The results shown are arbitrary
      [True, False, True]

      
    """

    def __init__(self, name=None, **kwds):
        self.name = name

        self.ntrials = kwds.pop("ntrials", None)
        self.trial = kwds.pop("trial", self.trial)
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

            result = self.trial(rand)
            self.process_result(result)
            self.results.append(result)

    def trial(self, rand):
        """
        Simulate a single trial of the model. `rand' will be an
        instance of random.Random; this instance will already be
        seeded, and so rand.seed, rand.jumpahead, etc. should not be
        called.

        """
        
        raise NotImplementedError()

    def process_result(self, *args, **kwds):
        """
        This method is called to process the results of each call to
        `trial'. This method can be used to perform calculations and
        store relevant data. Raw results are always stored in
        self.results (in particular, this method should _not_ write to
        self.results).
        
        """
        
        pass

    def __setattr__(self, name, val):
        """
        We want to treat certain attributes specially; namely, we want
        to ensure that `trial' and `process_result' are added as bound
        methods.

        """
        
        if name in ("trial", "process_result"):
            self.__dict__[name] = types.MethodType(val, self, self.__class__)
        else:
            self.__dict__[name] = val
