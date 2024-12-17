class Source:
    """
    Represents a traffic source that generates arrival events at a given rate (in Erlangs).
    """

    def __init__(self, erlangs: float, destination: int) -> None:
        """
        Initialize the Source.

        :param erlangs: Offered load in Erlangs.
        :param destination: The queue ID where arrivals from this source are directed.
        """
        self.erlangs: float = erlangs
        self.destination: int = destination
        self.lamda: float = 12500000 * self.erlangs
        self.expR: 'ExpRandGenerator' = ExpRandGenerator()

    def gen_arrival(self, current_time: float, source_num: int) -> 'Event':
        """
        Generate a future arrival event from this source.

        :param current_time: The current simulation time (in seconds).
        :param source_num: The identifier of this source.
        :return: An ARRIVAL event scheduled for a future time.
        """
        inter_arrival: float = self.expR.gen_random(self.lamda)
        arrival_time: float = current_time + inter_arrival
        origin: str = "Source {}".format(source_num)
        return Event(arrival_time, Event.ARRIVAL, self.destination, origin)
