from collections import deque
from typing import Deque, List, Optional

class Queue:
    """
    Represents a single queue in the network simulation. The queue handles
    incoming packets (arrivals) and processes them (departures) based on
    a service discipline and capacity limits.
    """

    # Queue identifiers
    ONE_A = 0
    ONE_B = 1
    TWO_A = 2
    TWO_B = 3
    THREE_A = 4
    THREE_B = 5
    THREE_C = 6
    FOUR_A = 7
    NO_DESTINATION = -1

    MU = 12500000  # Transmission rate

    def __init__(self, next_queues: List[int], name: str, size_limit: int) -> None:
        """
        Initialize the queue with its next destination, name, and size limit.

        :param next_queues: The next queue IDs to which packets may be forwarded.
        :param name: Name of the queue, for identification.
        :param size_limit: Maximum number of packets the queue can hold.
        """
        self.next_queues: List[int] = next_queues
        self.name: str = name
        self.size_limit: int = size_limit

        # Statistics and counters
        self.total_waiting_time: float = 0.0
        self.total_transmission_time: float = 0.0
        self.total_batch_time: float = 0.0
        self.total_time: float = 0.0
        self.packets_offered: int = 0
        self.packets_dropped: int = 0
        self.packets_dropped_per_batch: int = 0
        self.packets_transmitted: int = 0

        # Data structures
        self.packets: Deque[tuple['Event', float]] = deque()  # Stores (event, arrival_time)
        self.batch_means: Deque[float] = deque()
        self.loss_ratios: Deque[float] = deque()

        # Random generator for exponential service times
        self.expR: 'ExpRandGenerator' = ExpRandGenerator()

        # Indicates if the server (queue) is busy
        self.is_busy: bool = False

    def add_packet(self, event: 'Event', current_time: float) -> float:
        """
        Handle the arrival of a packet to the queue.

        :param event: The arrival event containing packet info.
        :param current_time: The current simulation time (in seconds).
        :return: The transmission time if the packet is processed immediately,
                 otherwise -1 if it waits in the queue.
        """
        self.packets_offered += 1

        # Calculate loss ratio every 5000 offered packets
        if self.packets_offered % 5000 == 0:
            self.calc_loss_ratio()

        # If the queue is full, drop the packet
        if len(self.packets) == self.size_limit:
            self.packets_dropped += 1
            self.packets_dropped_per_batch += 1
            return -1.0

        # If not busy, start transmitting immediately
        if not self.is_busy:
            self.is_busy = True
            transmission_time = self.expR.gen_random(self.MU)
            self.total_transmission_time += transmission_time
            self.total_batch_time += transmission_time
            return transmission_time

        # Otherwise, enqueue the packet
        self.packets.append((event, event.get_event_clock()))
        return -1.0

    def remove_packet(self, current_time: float) -> float:
        """
        Handle the departure of a packet from the queue.

        :param current_time: The current simulation time (in seconds).
        :return: The transmission time for the next packet if any, else -1.
        """
        self.packets_transmitted += 1

        # Calculate batch times every 5000 transmitted packets
        if self.packets_transmitted % 5000 == 0:
            self.calc_batch_times()

        # If no packets are waiting, the server becomes idle
        if not self.packets:
            self.is_busy = False
            return -1.0

        # Process the next packet in the queue
        event, arrival_time = self.packets.popleft()
        waiting_time = current_time - arrival_time
        if waiting_time < 0:
            # Should not occur if events are processed in order.
            waiting_time = 0.0

        self.total_waiting_time += waiting_time
        transmission_time = self.expR.gen_random(self.MU)
        self.total_transmission_time += transmission_time
        self.total_batch_time += (waiting_time + transmission_time)
        return transmission_time

    def calc_batch_times(self) -> None:
        """
        Calculate and store the mean batch time for the last 5000 transmitted packets.
        """
        if self.packets_transmitted > 0:
            self.batch_means.append(self.total_batch_time / 5000)
            self.total_batch_time = 0.0

    def calc_loss_ratio(self) -> None:
        """
        Calculate and store the loss ratio for the last 5000 offered packets.
        """
        if self.packets_offered > 0:
            self.loss_ratios.append(self.packets_dropped_per_batch / 5000)
            self.packets_dropped_per_batch = 0

    def print_details(self) -> None:
        """
        Print detailed statistics about this queue's performance.
        Times are converted to milliseconds for better readability.
        """
        if self.packets_transmitted > 0:
            self.total_time = self.total_waiting_time + self.total_transmission_time
            avg_trans_time_s = self.total_time / self.packets_transmitted
        else:
            avg_trans_time_s = 0.0

        avg_trans_time_ms = avg_trans_time_s * 1000  # Convert seconds to milliseconds
        drop_ratio = (self.packets_dropped / self.packets_offered) if self.packets_offered > 0 else 0.0

        print("------------- {} -------------".format(self.name))
        print("Packets Transmitted: {}".format(self.packets_transmitted))
        print("Packets dropped ratio: {:.5f}".format(drop_ratio))
        print("Packets dropped: {}".format(self.packets_dropped))
        print("Average Transmission time (ms): {:.5f}".format(avg_trans_time_ms))

    def print_batch_details(self) -> None:
        """
        Print the batch means and loss ratios collected every 5000 packets.
        """
        print("----------------- {} --------------".format(self.name))
        print("Batch means per 5000 transmitted packets (in s):")
        print("===========================================")
        while self.batch_means:
            # Format the batch mean with 5 decimal places
            print("{:.5f}".format(self.batch_means.popleft()))
        print("===========================================")
        print("Lost packet ratio per 5000 offered packets:")
        print("===========================================")
        while self.loss_ratios:
            # Format the loss ratio with 5 decimal places
            print("{:.5f}".format(self.loss_ratios.popleft()))
        print("===========================================")

