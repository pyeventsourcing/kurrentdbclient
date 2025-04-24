# ruff: noqa: S106, F704, PLE1142
import asyncio
import sys
from typing import Optional
from uuid import uuid4

from kurrentdbclient import (
    AsyncCatchupSubscription,
    AsyncKurrentDBClient,
    NewEvent,
    StreamState,
)
from kurrentdbclient.exceptions import ConsumerTooSlowError
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

stream_name = "MyStreamType-" + str(uuid4())

await client.append_to_stream(
    stream_name,
    events=[NewEvent(type="test-event", data=b"{}") for _ in range(5)],
    current_version=StreamState.ANY,
)


subscription: AsyncCatchupSubscription


async def handle_event(ev: RecordedEvent):
    print(f"handling event: {ev.stream_position} {ev.type}")
    await subscription.stop()


# region subscribe-to-stream
async with await client.subscribe_to_stream(stream_name) as subscription:
    async for event in subscription:
        await handle_event(event)
# endregion subscribe-to-stream


# region subscribe-to-all
async with await client.subscribe_to_all() as subscription:
    async for event in subscription:
        await handle_event(event)
# endregion subscribe-to-all


# region subscribe-to-stream-from-position
async with await client.subscribe_to_stream(
    stream_name=stream_name,
    stream_position=3,
) as subscription:
    async for event in subscription:
        await handle_event(event)
# endregion subscribe-to-stream-from-position


# region subscribe-to-all-from-position
async with await client.subscribe_to_all(
    commit_position=0,
) as subscription:
    async for event in subscription:
        await handle_event(event)
# endregion subscribe-to-all-from-position


# region subscribe-to-stream-live
async  with await client.subscribe_to_stream(
    stream_name=stream_name,
    from_end=True,
) as subscription:

    # Elsewhere, append new events...
    commit_position = await client.append_to_stream(
        stream_name,
        events=NewEvent(type="MyEventType", data=b"{}"),
        current_version=StreamState.ANY,
    )

    # Receive new events...
    async for event in subscription:
        await handle_event(event)
# endregion subscribe-to-stream-live


# region subscribe-to-all-live
async with await client.subscribe_to_all(
    from_end=True
) as subscription:

    # Elsewhere, append new events...
    commit_position = await client.append_to_stream(
        stream_name,
        events=NewEvent(type="MyEventType", data=b"{}"),
        current_version=StreamState.ANY,
    )

    # Receive new events...
    async for event in subscription:
        await handle_event(event)
# endregion subscribe-to-all-live


# Allow time for system projection to process event.
await asyncio.sleep(1)
# Check there is a "$et-MyEventType" stream by now.
events = await client.get_stream("$et-MyEventType")


# region subscribe-to-stream-resolving-linktos
async with await client.subscribe_to_stream(
    stream_name="$et-MyEventType",
    resolve_links=True,
) as subscription:
    async for event in subscription:
        await handle_event(event)
# endregion subscribe-to-stream-resolving-linktos

async def get_recorded_stream_position() -> Optional[int]:  # noqa: FA100
    return None

# region subscribe-to-stream-subscription-dropped
while True:
    async with await client.subscribe_to_stream(
        stream_name=stream_name,
        stream_position=await get_recorded_stream_position(),
    ) as subscription:
        try:
            async for event in subscription:
                # record stream position
                await handle_event(event)

        except ConsumerTooSlowError:
            # subscription was dropped
            continue
    # endregion subscribe-to-stream-subscription-dropped
    break


async def get_recorded_commit_position() -> Optional[int]:  # noqa: FA100
    return 0

# region subscribe-to-all-subscription-dropped
while True:
    async with await client.subscribe_to_all(
        commit_position=await get_recorded_commit_position(),
    ) as subscription:
        try:
            async for event in subscription:
                # record commit position
                await handle_event(event)

        except ConsumerTooSlowError:
            # subscription was dropped
            continue
    # endregion subscribe-to-all-subscription-dropped
    break


# region overriding-user-credentials
credentials = client.construct_call_credentials(
    username="admin",
    password="changeit",
)

async with await client.subscribe_to_all(
    credentials=credentials,
) as subscription:
    async for event in subscription:
        await handle_event(event)
# endregion overriding-user-credentials


# region stream-prefix-filtered-subscription
async with await client.subscribe_to_all(
    filter_include=[r"MyStreamType-.*"],
    filter_by_stream_name=True,
) as subscription:
    async for event in subscription:
        await handle_event(event)
# endregion stream-prefix-filtered-subscription

await client.close()
