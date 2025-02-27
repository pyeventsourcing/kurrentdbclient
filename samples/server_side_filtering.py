# -*- coding: utf-8 -*-
from uuid import uuid4

from kurrentdbclient import (
    KDB_SYSTEM_EVENTS_REGEX,
    Checkpoint,
    KurrentDBClient,
    NewEvent,
    StreamState,
)
from kurrentdbclient.exceptions import ConsumerTooSlow
from kurrentdbclient.streams import CatchupSubscription, RecordedEvent
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

subscription: CatchupSubscription


def handle_event(ev: RecordedEvent):
    print(f"handling event: {ev.stream_position} {ev.type}")
    global subscription
    subscription.stop()


stream_name = str(uuid4())

event_data = NewEvent(
    type="customer-one",
    data=b'{"id": "1", "important_data": "some value"}',
)

client.append_to_stream(
    stream_name=stream_name,
    current_version=StreamState.ANY,
    events=event_data,
)

print("region exclude-system")
# region exclude-system
subscription = client.subscribe_to_all(
    filter_exclude=[KDB_SYSTEM_EVENTS_REGEX]
)

for event in subscription:
    print("Received event:", event.stream_position, event.type)
    break
# endregion exclude-system
subscription.stop()

print("region event-type-prefix")
# region event-type-prefix
subscription = client.subscribe_to_all(
    filter_include=[r"customer-.*"],
)

for event in subscription:
    print(f"received event: {event.stream_position} {event.type}")

    # do something with the event
    handle_event(event)
# endregion event-type-prefix

event_data_one = NewEvent(
    type="user-one",
    data=b'{"id": "1", "important_data": "some value"}',
)
event_data_two = NewEvent(
    type="company-one",
    data=b'{"id": "1", "important_data": "some value"}',
)

client.append_to_stream(
    stream_name=stream_name,
    current_version=StreamState.ANY,
    events=event_data_one,
)
client.append_to_stream(
    stream_name=stream_name,
    current_version=StreamState.ANY,
    events=event_data_two,
)

print("region event-type-regex")
# region event-type-regex
subscription = client.subscribe_to_all(
    filter_by_stream_name=False,
    filter_include=["user.*", "company.*"],
)

for event in subscription:
    print(f"received event: {event.stream_position} {event.type}")

    # do something with the event
    handle_event(event)
# endregion event-type-regex

event_data = NewEvent(
    type="test-event",
    data=b'{"id": "1", "important_data": "some value"}',
)

client.append_to_stream(
    stream_name="user-" + str(uuid4()),
    current_version=StreamState.ANY,
    events=event_data,
)

print("region stream-prefix")
# region stream-prefix
subscription = client.subscribe_to_all(
    filter_by_stream_name=True,
    filter_include=[r"user-.*"],
)
for event in subscription:
    print(f"received event: {event.stream_position} {event.type}")

    # do something with the event
    handle_event(event)
# endregion stream-prefix

client.append_to_stream(
    stream_name="account-stream",
    current_version=StreamState.ANY,
    events=event_data,
)


print("region stream-regex")
# region stream-regex
subscription = client.subscribe_to_all(
    filter_by_stream_name=True,
    filter_include=["account.*", "savings.*"],
)
for event in subscription:
    # do something with the event
    handle_event(event)
# endregion stream-regex

print("region checkpoint")
# region checkpoint
# get last recorded commit position
last_commit_position = 0

while True:
    subscription = client.subscribe_to_all(
        commit_position=last_commit_position,
        filter_by_stream_name=True,
        filter_include=["account.*", "savings.*"],
        include_checkpoints=True,
    )
    try:
        for received in subscription:
            last_commit_position = received.commit_position

            # checkpoints are like events but only have a commit position
            if isinstance(received, Checkpoint):
                print("We got a checkpoint!")
            else:
                print("We got an event!")

            # record commit position
            handle_event(received)

    except ConsumerTooSlow:
        # subscription was dropped
        continue
    # endregion checkpoint
    break


print("region checkpoint-with-interval")
# region checkpoint-with-interval
subscription = client.subscribe_to_all(
    commit_position=last_commit_position,
    include_checkpoints=True,
    checkpoint_interval_multiplier=5,
)
# endregion checkpoint-with-interval

client.close()
