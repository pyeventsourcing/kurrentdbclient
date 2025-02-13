# -*- coding: utf-8 -*-
from uuid import uuid4

from kurrentclient import KurrentDBClient, NewEvent, StreamState
from kurrentclient.streams import CatchupSubscription, RecordedEvent
from tests.test_client import get_server_certificate

DEBUG = False
_print = print


def print(*args):
    if DEBUG:
        _print(*args)


KDB_TARGET = "localhost:2114"
qs = "MaxDiscoverAttempts=2&DiscoveryInterval=100&GossipTimeout=1"

client = KurrentDBClient(
    uri=f"kdb://admin:changeit@{KDB_TARGET}?{qs}",
    root_certificates=get_server_certificate(KDB_TARGET),
)

stream_name = str(uuid4())


subscription: CatchupSubscription


def handle_event(ev: RecordedEvent):
    print(f"handling event: {ev.stream_position} {ev.type}")
    global subscription
    subscription.stop()


"""
# region createClient
client = KurrentDBClient(
    uri="{connectionString}"
)
# endregion createClient
"""

# region createEvent
new_event = NewEvent(
    id=uuid4(),
    type="TestEvent",
    data=b"I wrote my first event",
)

# endregion createEvent

# region appendEvents
client.append_to_stream(
    "some-stream",
    events=[new_event],
    current_version=StreamState.ANY,
)
# endregion appendEvents

# region readStream
events = client.get_stream("some-stream")

for event in events:
    # Doing something productive with the event
    print(event)
# endregion readStream

# region subscribeToAll
subscription = client.subscribe_to_all(from_end=True)

# Append some events
client.append_to_stream(
    stream_name,
    events=NewEvent(type="test-event", data=b""),
    current_version=StreamState.ANY,
)

for event in subscription:
    print(f"received event: {event.stream_position} {event.type}")

    # do something with the event
    handle_event(event)
# endregion subscribeToAll

client.close()
