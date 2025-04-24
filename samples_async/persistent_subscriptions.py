# ruff: noqa: PERF203, F704, PLE1142
import sys
from uuid import uuid4

from kurrentdbclient import (
    AsyncKurrentDBClient,
    AsyncPersistentSubscription,
    NewEvent,
    RecordedEvent,
    StreamState,
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

subscription: AsyncPersistentSubscription


async def handle_event(ev: RecordedEvent):
    print(f"handling event: {ev.ack_id} {ev.stream_position} {ev.type}")
    await subscription.stop()


stream_name = "user-" + str(uuid4())

event_data = NewEvent(
    type="some-event",
    data=b"{}",
)

await client.append_to_stream(
    stream_name=stream_name,
    current_version=StreamState.ANY,
    events=event_data,
)

group_name = str(uuid4())

# region create-persistent-subscription-to-stream
await client.create_subscription_to_stream(
    group_name=group_name,
    stream_name=stream_name,
)
# endregion create-persistent-subscription-to-stream


# region subscribe-to-persistent-subscription-to-stream
async with await client.read_subscription_to_stream(
    group_name=group_name,
    stream_name=stream_name,
) as subscription:
    async for event in subscription:
        try:
            await handle_event(event)
        except Exception:
            await subscription.nack(event, action="park")
        else:
            await subscription.ack(event)
# endregion subscribe-to-persistent-subscription-to-stream

# Delete the subscription and make a new one.
await client.delete_subscription(
    group_name=group_name,
    stream_name=stream_name,
)

group_name = str(uuid4())

await client.create_subscription_to_stream(
    group_name=group_name,
    stream_name=stream_name,
)

# region subscribe-to-persistent-subscription-with-manual-acks
async with await client.read_subscription_to_stream(
    group_name=group_name,
    stream_name=stream_name,
) as subscription:
    async for event in subscription:
        try:
            await handle_event(event)
        except Exception:
            if event.retry_count < 5:
                await subscription.nack(event, action="retry")
            else:
                await subscription.nack(event, action="park")
        else:
            await subscription.ack(event)
# endregion subscribe-to-persistent-subscription-with-manual-acks


# region update-persistent-subscription
await client.update_subscription_to_stream(
    group_name=group_name,
    stream_name=stream_name,
    resolve_links=True,
)
# endregion update-persistent-subscription


# region delete-persistent-subscription
await client.delete_subscription(
    group_name=group_name,
    stream_name=stream_name,
)
# endregion delete-persistent-subscription


# region create-persistent-subscription-to-all
await client.create_subscription_to_all(
    group_name=group_name,
    filter_by_stream_name=True,
    filter_include=[r"user-.*"],
)
# endregion create-persistent-subscription-to-all


# region subscribe-to-persistent-subscription-to-all
async with await client.read_subscription_to_all(
    group_name=group_name,
) as subscription:
    async for event in subscription:
        try:
            await handle_event(event)
        except Exception:
            await subscription.nack(event, action="park")
        else:
            await subscription.ack(event)
# endregion subscribe-to-persistent-subscription-to-all

await client.close()
