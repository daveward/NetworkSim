class Event:
    ARRIVAL = 1
    DEPARTURE = 2
    PACKET_DROP = 3

    def __init__(self, event_time, event_type, destination, origin):
        """
        :param event_time: The time this event will occur.
        :param event_type: The type of event (ARRIVAL, DEPARTURE, PACKET_DROP).
        :param destination: The queue ID of the queue this event affects.
        :param origin: A string describing where this packet originated (e.g. "Source 0", "Router Q1", "System").
        """
        self.event_time = event_time
        self.type = event_type
        self.destination = destination
        self.origin = origin

    def get_event_clock(self):
        return self.event_time

    def set_event_clock(self, new_time):
        self.event_time = new_time

    def __str__(self):
        # Common template for known event types
        template = "{event_type} Event at {time:.5f}s, Destination Queue: {dest}, Origin: {orig}"

        if self.type == Event.ARRIVAL:
            return template.format(
                event_type="Arrival",
                time=self.event_time,
                dest=self.destination,
                orig=self.origin
            )
        elif self.type == Event.DEPARTURE:
            return template.format(
                event_type="Departure",
                time=self.event_time,
                dest=self.destination,
                orig=self.origin
            )
        elif self.type == Event.PACKET_DROP:
            return template.format(
                event_type="Packet Drop",
                time=self.event_time,
                dest=self.destination,
                orig=self.origin
            )
        else:
            return "Unknown Event at {:.5f}s".format(self.event_time)
