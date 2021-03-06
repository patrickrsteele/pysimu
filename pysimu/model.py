from random import Random
import types
import multiprocessing
import time
import logging

from pysimu.server import server

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
        self.debug = kwds.pop("debug", False)
        self.multiprocess = kwds.pop("multiprocess", False)
        
        if len(kwds) > 0:
            msg = "Unknown keyword arguments: %s" % str(kwds.keys())[1:-1]
            raise TypeError(msg)

        self._setup_logging()

    def _setup_logging(self):
        """
        Configure self.logger for logging

        """

        self.logger = logging.getLogger(__name__)

        fmtstr = "[%%(levelname)s] %s: %%(message)s" % __name__
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(fmt=fmtstr))
        self.logger.addHandler(console_handler)
        if self.debug:
            self.logger.setLevel(logging.INFO)
        else:
            self.logger.setLevel(logging.WARNING)

    def simulate(self):
        if self.ntrials is None:
            msg = "Model attribute 'ntrials' must be specified"
            raise ValueError(msg)
        if self.trial is None:
            msg = "Model attribute 'trial' must be specified"
            raise ValueError(msg)

        t1 = time.time()
        self.results = []
        if self.multiprocess:
            self.logger.info("starting simulations: multiprocessing")

            ncpus = multiprocessing.cpu_count()

            # Create and start each Server
            server_processes = []
            server_connections = []
            for n in xrange(0, ncpus):
                (parent_conn, child_conn) = multiprocessing.Pipe()
                proc = multiprocessing.Process(target=server,
                                               args=(self.trial, parent_conn, child_conn))
                proc.start()
                server_processes.append(proc)
                server_connections.append(parent_conn)
                child_conn.close() # We don't use this end

            # Send initial data to each Server
            n = 0
            for conn in server_connections:
                if n < self.ntrials:
                    self.logger.debug("dispatching %i" % n)
                    conn.send((n, self._get_rand(n),))
                    n += 1
                else:
                    break

            # Dispatch all trials
            finished = []
            while True:
                for conn in server_connections:
                    if conn.poll():
                        result = conn.recv()
                        self.process_result(result)
                        self.results.append(result)

                        # Dispatch the next trial, or mark the connection for closure
                        if n < self.ntrials:
                            self.logger.debug("dispatching %i" % n)
                            conn.send((n, self._get_rand(n),))
                            n += 1
                        else:
                            finished.append(conn)

                if n == self.ntrials and len(finished) == ncpus:
                    break

            # Cleanup servers
            self.logger.debug("dispatching done, cleaning up")
            for conn in server_connections:
                conn.close()
            for proc in server_processes:
                proc.join()

        else:
            self.logger.info("starting simulations: sequential")
            for n in xrange(0, self.ntrials):
                rand = Random()
                rand.seed(self.seed)
                rand.jumpahead(n)
                result = self.trial(rand)
                self.process_result(result)
                self.results.append(result)

        t2 = time.time()
        self.logger.info("simulations took %.3fs" % (t2 - t1))

    def _get_rand(self, n):
        """
        Return the nth offset of the random number generator seeded by
        self.seed.

        """

        rand = Random()
        rand.seed(self.seed)
        rand.jumpahead(n)
        return rand

    def dispatch(self, conn, rand):
        """
        Dispatch a child process to run self.trial using the provided
        instance of random.Random, rand. Communicate results with the
        pipe conn.

        """

        result = self.trial(rand)
        conn.send(result)
        conn.close()


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
