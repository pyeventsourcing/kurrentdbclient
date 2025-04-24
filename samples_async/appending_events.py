# ruff: noqa: EM101, S106, F704, PLE1142
import sys
from uuid import uuid4

from kurrentdbclient import (
    AsyncKurrentDBClient,
    NewEvent,
    StreamState,
    exceptions,
)
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

stream_name = str(uuid4())

# region append-to-stream
event1 = NewEvent(
    type="some-event",
    data=b'{"important_data": "some value"}',
)

commit_position = await client.append_to_stream(
    stream_name=stream_name,
    current_version=StreamState.NO_STREAM,
    events=[event1],
)
# endregion append-to-stream

stream_name = str(uuid4())

# region append-duplicate-event
event = NewEvent(
    id=uuid4(),
    type="some-event",
    data=b'{"important_data": "some value"}',
    metadata=b"{}",
    content_type="application/json",
)

await client.append_to_stream(
    stream_name=stream_name,
    current_version=StreamState.ANY,
    events=event,
)

await client.append_to_stream(
    stream_name=stream_name,
    current_version=StreamState.ANY,
    events=event,
)
# endregion append-duplicate-event
assert len(await client.get_stream(stream_name)) == 1

# region append-with-no-stream
event1 = NewEvent(
    type="some-event",
    data=b'{"important_data": "some value"}',
)

stream_name = str(uuid4())

await client.append_to_stream(
    stream_name=stream_name,
    current_version=StreamState.NO_STREAM,
    events=event1,
)

event2 = NewEvent(
    type="some-event",
    data=b'{"important_data": "some other value"}',
)

try:
    # attempt to append the same event again
    await client.append_to_stream(
        stream_name=stream_name,
        current_version=StreamState.NO_STREAM,
        events=event2,
    )
except exceptions.WrongCurrentVersionError:
    print("Error appending second event")
    # endregion append-with-no-stream
else:
    raise Exception("Exception not raised")

stream_name = str(uuid4())

await client.append_to_stream(
    stream_name=stream_name,
    current_version=StreamState.ANY,
    events=NewEvent(
        type="some-event",
        data=b'{"id": "1", "value": "some value"}',
    ),
)

# region append-with-concurrency-check

original_version = StreamState.NO_STREAM

async for event in await client.read_stream(stream_name):
    original_version = event.stream_position


event1 = NewEvent(
    type="some-event",
    data=b'{"important_data": "some value"}',
)

await client.append_to_stream(
    stream_name=stream_name,
    current_version=original_version,
    events=event1,
)

event2 = NewEvent(
    type="some-event",
    data=b'{"important_data": "some other value"}',
)

try:
    await client.append_to_stream(
        stream_name=stream_name,
        current_version=original_version,
        events=event2,
    )
except exceptions.WrongCurrentVersionError:
    print("Error appending event2")
    # endregion append-with-concurrency-check
else:
    raise Exception("Exception not raised")

stream_name = str(uuid4())

event = NewEvent(
    type="some-event",
    data=b'{"id": "1", "important_data": "some value"}',
)

# region overriding-user-credentials
credentials = client.construct_call_credentials(
    username="admin",
    password="changeit",
)

await client.append_to_stream(
    stream_name=stream_name,
    current_version=StreamState.ANY,
    events=event,
    credentials=credentials,
)
# endregion overriding-user-credentials

await client.close()
