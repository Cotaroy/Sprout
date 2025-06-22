import json
from dataclasses import dataclass
from pathretriever import R

EVENT_LIST_FILE_PATH = R('event_list/SAMPLE_EVENT_LIST.json')

def load_event_list(file_path = EVENT_LIST_FILE_PATH):
    with open(file_path, 'r') as f:
        event_list = json.load(f)
    assert isinstance(event_list, list)
    return event_list
