from typing import List, Tuple
from simulation.EventListManager import EventListManager
from simulation.Event import Event
from simulation.Queue import Queue
from simulation.Source import Source


class NetworkSimulation:
    """
    Manages a network simulation consisting of multiple routers (queues) and sources.
    Processes events in chronological order until the desired number of arrivals is met.
    """

    def __init__(self, max_arrivals: int = 10000) -> None:
        """
        Initialize the NetworkSimulation.
        """
        self.global_time: float = 0.0
        self.packets_arrived: int = 0
        self.max_arrivals: int = max_arrivals
        self.e_list: 'EventListManager' = EventListManager.get_instance()

        # Keep track of all events processed for logging
        # Each entry: (time, action, event_string)
        self.processed_events: List[Tuple[float, str, str]] = []

        # Define source parameters as (erlangs, destination)
        # 4 sources going into different points in the network
        source_params: List[Tuple[float, int]] = [
            (0.5, Queue.ONE_A),  # Source 0 -> Q0
            (0.3, Queue.ONE_A),  # Source 1 also -> Q0
            (0.4, Queue.ONE_B),  # Source 2 -> Q1
            (0.2, Queue.TWO_A),  # Source 3 -> Q2
        ]
        self.sources: List['Source'] = [Source(erlangs, dest) for erlangs, dest in source_params]

        # Topology definition for queues
        queue_params = {
            # Queue constant: ( [list_of_next_queue_constants], "Queue_Name", max queue size )
            # List of next queue constants: specifies which queues packets move on to
            # Router Qn: This is the human readable name of the queue"
            # Integer: This is the maximum size of the queue buffer
            Queue.ONE_A: ([Queue.ONE_B, Queue.TWO_A], "Router Q0", 10),
            Queue.ONE_B: ([Queue.TWO_B], "Router Q1", 10),
            Queue.TWO_A: ([Queue.THREE_A, Queue.THREE_B], "Router Q2", 10),
            Queue.TWO_B: ([Queue.THREE_C], "Router Q3", 10),
            Queue.THREE_A: ([], "Router Q4", 10),
            Queue.THREE_B: ([Queue.FOUR_A], "Router Q5", 10),
            Queue.THREE_C: ([], "Router Q6", 10),
            Queue.FOUR_A: ([], "Router Q7", 10),
        }

        max_queue_index = max(queue_params.keys())
        self.queues: List['Queue'] = [None] * (max_queue_index + 1)
        for q_const, (next_queues, q_name, q_cap) in queue_params.items():
            self.queues[q_const] = Queue(next_queues, q_name, q_cap)

    def gen_init_packets(self) -> None:
        """
        Generate initial arrival events from each source at the start of the simulation.
        """
        for i, source in enumerate(self.sources):
            arrival_event: 'Event' = source.gen_arrival(self.global_time, i)
            self.e_list.insert_event(arrival_event)
            self.packets_arrived += 1

    def print_all_processed_events(self) -> None:
        """
        Print all processed events (including arrivals, departures, and drops).
        """
        print("All Processed Events (including arrivals, departures, and drops):")
        for event_time, action, evt_str in self.processed_events:
            print("[Time={:.5f}] {}: {}".format(event_time, action, evt_str))

    def run(self) -> None:
        """
        Run the simulation until the specified number of arrivals is reached or no events remain.
        """
        self.gen_init_packets()

        while self.packets_arrived < self.max_arrivals:
            event: 'Event' = self.e_list.poll()
            if event is None:
                break

            # Log the event as processed / departed
            self.processed_events.append((self.global_time, "POLLED", str(event)))

            self.global_time = event.get_event_clock()

            if event.type == Event.ARRIVAL:
                return_time: float = self.queues[event.destination].add_packet(event, self.global_time)
                if return_time > -1:
                    departure_time: float = self.global_time + return_time
                    origin: str = self.queues[event.destination].name
                    dep_event: 'Event' = Event(departure_time, Event.DEPARTURE, event.destination, origin)
                    self.e_list.insert_event(dep_event)
                    self.processed_events.append((self.global_time, "SCHEDULED", str(dep_event)))

                # If it's an arrival from a source, schedule next arrival
                if "Source" in event.origin:
                    source_num: int = int(event.origin.split()[1])
                    new_arrival: 'Event' = self.sources[source_num].gen_arrival(self.global_time, source_num)
                    self.e_list.insert_event(new_arrival)
                    self.packets_arrived += 1
                    self.processed_events.append((self.global_time, "SCHEDULED", str(new_arrival)))

            elif event.type == Event.DEPARTURE:
                return_time: float = self.queues[event.destination].remove_packet(self.global_time)
                if return_time > -1:
                    departure_time: float = self.global_time + return_time
                    origin: str = self.queues[event.destination].name
                    dep_event: 'Event' = Event(departure_time, Event.DEPARTURE, event.destination, origin)
                    self.e_list.insert_event(dep_event)
                    self.processed_events.append((self.global_time, "SCHEDULED", str(dep_event)))

                # Schedule arrivals for next queues if any
                for nq in self.queues[event.destination].next_queues:
                    if nq != Queue.NO_DESTINATION:
                        origin: str = self.queues[event.destination].name
                        arr_event: 'Event' = Event(self.global_time, Event.ARRIVAL, nq, origin)
                        self.e_list.insert_event(arr_event)
                        self.processed_events.append((self.global_time, "SCHEDULED", str(arr_event)))

        # Print final queue stats
        for q in self.queues:
            q.print_details()

        # Print the future event list - this produces a LOT of text
        self.print_all_processed_events()
