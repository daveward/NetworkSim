from collections import deque
from typing import Optional, Deque

class EventListManager:
    """
    Manages the future event list for the simulation, ensuring events are processed
    in chronological order. This class follows the singleton pattern so that
    the entire simulation shares the same event list.
    """

    _instance: Optional['EventListManager'] = None

    def __init__(self) -> None:
        if EventListManager._instance is not None:
            raise Exception("Use EventListManager.get_instance() to get the singleton instance.")
        self.event_list: Deque['Event'] = deque()

    @classmethod
    def get_instance(cls) -> 'EventListManager':
        """
        Return the singleton instance of EventListManager.
        """
        if cls._instance is None:
            cls._instance = EventListManager()
        return cls._instance

    def insert_event(self, event: 'Event') -> None:
        """
        Insert an event into the event list in chronological order.
        """
        if self.is_empty():
            self.event_list.append(event)
            return

        inserted = False
        for i, existing_event in enumerate(self.event_list):
            if event.get_event_clock() <= existing_event.get_event_clock():
                self.event_list.insert(i, event)
                inserted = True
                break

        if not inserted:
            self.event_list.append(event)

    def poll(self) -> Optional['Event']:
        """
        Pop and return the earliest event from the list.
        Returns None if the list is empty.
        """
        if self.event_list:
            return self.event_list.popleft()
        return None

    def is_empty(self) -> bool:
        """
        Check if the event list is empty.
        """
        return len(self.event_list) == 0

    def print_future_events(self) -> None:
        """
        Print all events currently in the event list.
        If no events remain, we state that none are scheduled.
        """
        if self.is_empty():
            print("No future events scheduled.")
            return

        print("Future Events in the System:")
        for evt in self.event_list:
            print(evt)
