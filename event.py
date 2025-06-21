
from dataclasses import dataclass

EVENT_LIST_FILE_PATH = 'event_list/SAMPLE_EVENT_LIST.json'

@dataclass
class Event:
    script: list[str]
    sprite_intro_file_location: str = None
    sprite_idle_file_location: str = None
    sprite_outro_file_location: str = None
    text_box_file_location: str = None
    background_file_location: str = None


@dataclass
class EventList:
    events: list[Event]
