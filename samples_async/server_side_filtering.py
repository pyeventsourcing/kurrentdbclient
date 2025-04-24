# ruff: noqa: F704, PLE1142
import sys
from uuid import uuid4

from kurrentdbclient import (
    AsyncCatchupSubscription,
    AsyncKurrentDBClient,
    Checkpoint,
    NewEvent,
    StreamState,
)
from kurrentdbclient.streams import RecordedEvent
from tests.test_client import get_server_certificate

DEBUG = False

def print(*args):  # noqa: A001
    if DEBUG:
        sys.stdout.write(" ".join([repr(arg) for arg in args]) + "\n")


KDB_TARGET = "localhost:2114"
qs = "MaxDiscoverAttempts=2&DiscoveryInterval=100&GossipTimeout=1"

client = AsyncKurrentDBClient(
    uri=f"kdb://admin:changeit@{KDB_TARGET}?{qs}",
    root_certificates=get_server_certificate(KDB_TARGET),
)
await client.connect()

subscription: AsyncCatchupSubscription


async def handle_event(ev: RecordedEvent):
    print(f"handling event: {ev.stream_position} {ev.type}")
    await subscription.stop()


stream_name = str(uuid4())

event_data = NewEvent(
    type="customer-one",
    data=b'{"id": "1", "important_data": "some value"}',
)

await client.append_to_stream(
    stream_name=stream_name,
    current_version=StreamState.ANY,
    events=event_data,
)

# region exclude-system
async with await client.subscribe_to_all(
    filter_exclude=r"\$.+"
) as subscription:
    async for event in subscription:
        await handle_event(event)
# endregion exclude-system


# region event-type-prefix
async with await client.subscribe_to_all(
    filter_include=[r"customer-.*"],
) as subscription:
    async for event in subscription:
        await handle_event(event)
# endregion event-type-prefix


event_data = NewEvent(
    type="test-event",
    data=b'{"id": "1", "important_data": "some value"}',
)

await client.append_to_stream(
    stream_name="user-" + str(uuid4()),
    current_version=StreamState.ANY,
    events=event_data,
)

# region stream-prefix
async with await client.subscribe_to_all(
    filter_by_stream_name=True,
    filter_include=[r"user-.*"],
) as subscription:
    async for event in subscription:
        await handle_event(event)
# endregion stream-prefix

await client.append_to_stream(
    stream_name="account-stream",
    current_version=StreamState.ANY,
    events=event_data,
)


# region stream-regex
async with await client.subscribe_to_all(
    filter_by_stream_name=True,
    filter_include=["account.*", "savings.*"],
) as subscription:
    async for event in subscription:
        await handle_event(event)
# endregion stream-regex

# region checkpoint
# get last recorded commit position
recorded_position = 0

async with await client.subscribe_to_all(
    commit_position=recorded_position,
    filter_by_stream_name=True,
    filter_include=["account.*", "savings.*"],
    include_checkpoints=True,
) as subscription:
    async for event in subscription:

        # checkpoints have commit positions
        if isinstance(event, Checkpoint):
            print("We got a checkpoint!", event.commit_position)
        else:
            print("We got an event!", event.commit_position)

        # record commit position
        await handle_event(event)
# endregion checkpoint


print("region checkpoint-with-interval")
# region checkpoint-with-interval
async with await client.subscribe_to_all(
    commit_position=recorded_position,
    include_checkpoints=True,
    checkpoint_interval_multiplier=5,
) as subscription:
    async for event in subscription:
        await handle_event(event)
# endregion checkpoint-with-interval

await client.close()
