# ruff: noqa: F704, PLE1142
import sys
from uuid import uuid4

from kurrentdbclient import AsyncKurrentDBClient, NewEvent, StreamState
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


"""
# region createClient
client = AsyncKurrentDBClient(
    uri=connection_string
)
await client.connect()
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
await client.append_to_stream(
    stream_name=stream_name,
    events=[new_event],
    current_version=StreamState.ANY,
)
# endregion appendEvents


# region readStream
events = await client.read_stream(stream_name)
# endregion readStream

await client.close()
