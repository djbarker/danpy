import datetime

from dataclasses import dataclass, field


@dataclass
class PerfInfo:
    """
    Stores information about performance; namely a number of events and the time taken to run them.

    :py:class:`PerfInfo` objects can be added together (& subtracted) which is useful for measuring long-running performance.
    """

    events: int = field(default=0)  #: The number of events that have been processed.
    micros: int = field(default=0)  #: The number of microseconds taken to process the events.

    @property
    def seconds(self) -> float:
        """
        The number of seconds taken to process the events.
        """
        return self.micros * 1e-6

    @property
    def rate(self) -> float:
        """
        The rate, measured in events/second.
        """
        return self.events / self.seconds

    def fmt(self, events_name: str) -> str:
        """
        A human-readable string formatted with the performance information.

        .. code-block:: python

            perf_info = PerfInfo(2500, 1_250_000)
            perf_info.fmt("frobinations") # == "2500 frobinations in 1.3 seconds => 2000.0 frobinations/sec"

        :param events_name: The plural 'name' of the events being measured, e.g. "updates" or "frames".
        """
        # TODO: time delta formatting
        return f"{self.events} {events_name} in {self.seconds:.1f} seconds => {self.rate:.1f} {events_name}/sec"

    def __str__(self) -> str:
        return self.fmt("events")

    def __add__(self, rhs: "PerfInfo") -> "PerfInfo":
        if not isinstance(rhs, PerfInfo):
            raise TypeError(f"rhs must be PerfInfo. [{rhs=!r}]")

        return PerfInfo(
            self.events + rhs.events,
            self.micros + rhs.micros,
        )

    def __sub__(self, rhs: "PerfInfo") -> "PerfInfo":
        if not isinstance(rhs, PerfInfo):
            raise TypeError(f"rhs must be PerfInfo. [{rhs=!r}]")

        return PerfInfo(
            self.events - rhs.events,
            self.micros - rhs.micros,
        )

    def __iadd__(self, rhs: "PerfInfo") -> "PerfInfo":
        if not isinstance(rhs, PerfInfo):
            raise TypeError(f"rhs must be PerfInfo. [{rhs=!r}]")

        self.events += rhs.events
        self.micros += rhs.micros

        return self


@dataclass
class PerfTimer:
    """
    Measure time and return a :py:class:`PerfInfo` object when done.

    .. code-block:: python

        timer = tick()
        do_something_expensive()
        perf = timer.tock()
    """

    start: datetime.datetime
    events: int

    @property
    def elapsed(self) -> datetime.timedelta:
        return datetime.datetime.now() - self.start

    def tock(self, *, events: int = 0) -> PerfInfo:
        """
        Return a :py:class:`PerfInfo` with the given numer of processed events & elapsed time.

        .. code-block:: python

            timer = tick()
            for _ in range(10):
                do_something()
            perf = timer.tock(events=10)

        :param events: Any additional events to add which have not already been added by calls to :py:meth:`add_events`.
        """
        self.add_events(events)
        delta = self.elapsed
        return PerfInfo(self.events, int(delta.seconds * 1e6 + delta.microseconds))

    def add_events(self, events: int) -> "PerfTimer":
        """
        Add the given number of events to the timer.

        .. code-block:: python

            timer = tick()
            for _ in range(10):
                do_something()
            timer.add_events(10)
            perf = timer.tock()

        :param events: The number of events to add.
        """
        self.events += events
        return self

    def add_event(self) -> "PerfTimer":
        """
        Add the a single event to the timer.

        .. code-block:: python

            timer = tick()
            for _ in range(10):
                do_something()
                timer.add_event()
            perf = timer.tock()
        """
        return self.add_events(1)


def tick() -> PerfTimer:
    """
    Get a new :py:class:`PerfTimer` object.
    """
    return PerfTimer(datetime.datetime.now(), 0)
