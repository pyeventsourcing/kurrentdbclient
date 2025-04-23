from __future__ import annotations

import os
import ssl
import sys
from typing import cast
from uuid import uuid4

from kurrentdbclient import (
    Checkpoint,
    KurrentDBClient,
    NewEvent,
    RecordedEvent,
    StreamState,
)
from kurrentdbclient.exceptions import GrpcDeadlineExceededError

KDB_TARGET = "localhost:2114"
KDB_TLS = True


def demo_extra_checkpoint_bug() -> None:
    with construct_esdb_client() as client:
        for i in range(1000):
            print("Trying to reveal extra checkpoint bug, attempt", i)
            failmsg = append_and_subscribe(client)
            if failmsg:
                sys.stderr.write(failmsg + "\n")
                break
        else:
            print("Checkpoint bug wasn't found")


def append_and_subscribe(client: KurrentDBClient) -> str:

    # Append new events.
    event1 = NewEvent(type="OrderCreated", data=random_data())
    event2 = NewEvent(type="OrderUpdated", data=random_data())
    event3 = NewEvent(type="OrderDeleted", data=random_data())
    stream_name1 = str(uuid4())
    first_append_commit_position = client.append_events(
        stream_name1,
        current_version=StreamState.NO_STREAM,
        events=[event1, event2, event3],
    )

    def get_event_at_commit_position(
        commit_position: int,
    ) -> RecordedEvent | None:
        read_response = client.read_all(
            commit_position=commit_position,
            # backwards=True,
            filter_exclude=[],
            limit=1,
        )
        events = tuple(read_response)
        if len(events) == 1:
            event = events[0]
            assert event.commit_position == commit_position, event
            return event
        return None

    event = get_event_at_commit_position(first_append_commit_position)
    assert event is not None
    assert event.id == event3.id
    assert event.commit_position == first_append_commit_position
    current_commit_position = client.get_commit_position(filter_exclude=[])
    assert event.commit_position == current_commit_position

    # Subscribe excluding all events, with large window.
    subscription1 = client.subscribe_to_all(
        # filter_exclude=[".*"],
        include_checkpoints=True,
        window_size=10000,
        checkpoint_interval_multiplier=500,
        timeout=1,
    )

    # We shouldn't get an extra checkpoint at the end (bug with <v23.10),
    # that has a commit position greater than the current commit position (v24.2).
    checkpoint_commit_position: int | None = None
    try:
        for event in subscription1:
            if isinstance(event, Checkpoint):
                checkpoint_commit_position = event.commit_position
                # break
    except GrpcDeadlineExceededError:
        pass

    fail_msg = ""

    if (
        checkpoint_commit_position is not None
        and checkpoint_commit_position > current_commit_position
    ):
        fail_msg = (
            f"Checkpoint commit position: {checkpoint_commit_position}."
            f" Current commit position: {current_commit_position}."
        )

    if fail_msg:
        assert checkpoint_commit_position is not None
        event_at_checkpoint_commit_position = get_event_at_commit_position(
            checkpoint_commit_position
        )
        if event_at_checkpoint_commit_position is None:
            fail_msg += " No event found at checkpoint commit position."
        else:
            fail_msg += (
                f" Event at checkpoint commit position:"
                f" {event_at_checkpoint_commit_position}."
            )

        if event_at_checkpoint_commit_position is None:
            event4 = NewEvent(type="OrderUndeleted", data=random_data())
            second_append_commit_position = client.append_events(
                stream_name1,
                current_version=2,
                events=[event4],
            )
            if second_append_commit_position == checkpoint_commit_position:
                fail_msg += (
                    " Checkpoint commit position was used for "
                    "subsequently recorded event."
                )
            elif second_append_commit_position > checkpoint_commit_position:
                fail_msg += (
                    " Checkpoint commit position was less than "
                    "commit position of subsequently recorded event."
                )
            else:
                fail_msg += (
                    " Checkpoint commit position was greater than "
                    "commit position of subsequently recorded event."
                )

    return fail_msg


def construct_esdb_client(qs: str = "") -> KurrentDBClient:
    uri = f"kdb://admin:changeit@{KDB_TARGET}?{qs}"
    root_certificates = get_server_certificate()
    return KurrentDBClient(uri, root_certificates=root_certificates)


def get_server_certificate() -> str:
    return ssl.get_server_certificate(
        addr=cast(tuple[str, int], KDB_TARGET.split(":")),
    )


def random_data(size: int = 16) -> bytes:
    return os.urandom(size)


if __name__ == "__main__":
    demo_extra_checkpoint_bug()
