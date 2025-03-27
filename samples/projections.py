# -*- coding: utf-8 -*-
# https://github.com/EventStore/EventStore-Client-NodeJS/blob/master/packages/test/src/samples/projection-management.ts
import sys
import traceback
from time import sleep
from uuid import uuid4

from kurrentdbclient import (
    KurrentDBClient,
    NewEvent,
    StreamState,
    exceptions,
)
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

# region CreateContinuous
projection_name = f"count_events_{uuid4()}"
projection_query = """fromAll()
.when({
    $init() {
        return {
            count: 0,
        };
    },
    $any(s, e) {
        s.count += 1;
    }
})
.outputState();
"""

client.create_projection(
    name=projection_name,
    query=projection_query,
)
# endregion CreateContinuous

# region CreateContinuous_Conflict
try:
    client.create_projection(
        name=projection_name,
        query=projection_query,
    )
except exceptions.AlreadyExists:
    pass
else:
    raise Exception("Projection didn't already exist")

# endregion CreateContinuous_Conflict

# region Enable
client.enable_projection(name=projection_name)
# endregion Enable

# region EnableNotFound
try:
    client.enable_projection(name="does-not-exist")
except exceptions.NotFound:
    pass
else:
    raise Exception("Projection exists")
# endregion EnableNotFound

client.append_event(
    stream_name=str(uuid4()),
    event=NewEvent(type="SampleEvent", data=b"{}"),
    current_version=StreamState.NO_STREAM,
)
sleep(0.5)

# region GetStatus
statistics = client.get_projection_statistics(name=projection_name)
print("Projection name:", statistics.name)
print("Projection status:", statistics.status)
print("Projection checkpoint status", statistics.checkpoint_status)
print("Projection mode:", statistics.mode)
print("Projection progress:", statistics.progress)
# endregion GetStatus

try:
    # region ListAll
    list_of_statistics = client.list_all_projection_statistics()
    # endregion ListAll
    print(list_of_statistics)
except exceptions.ExceptionThrownByHandler:
    sys.stderr.write(
        f"Exception thrown by list_all_projection_statistics() handler:"
        f" {traceback.format_exc()}\n"
    )
    sys.stderr.flush()
    pass

try:
    # region ListContinuous
    list_of_statistics = (
        client.list_continuous_projection_statistics()
    )
    # endregion ListContinuous
    print(list_of_statistics)
except exceptions.ExceptionThrownByHandler:
    sys.stderr.write(
        f"Exception thrown by list_continuous_projection_statistics() handler: "
        f"{traceback.format_exc()}\n"
    )
    sys.stderr.flush()
    pass


# region GetState
state = client.get_projection_state(name=projection_name)
print(f"Counted {state.value['count']} events")
# endregion GetState

# region GetResult
# There's no difference between "projection state" and "projection result"
state = client.get_projection_state(name=projection_name)
print(f"Counted {state.value['count']} events")
# endregion GetResult


# region Disable
client.disable_projection(name=projection_name)
# endregion Disable

# region DisableNotFound
try:
    client.disable_projection(name="does-not-exist")
except exceptions.NotFound:
    pass
else:
    raise Exception("Projection exists")
# endregion DisableNotFound

# region Abort
client.abort_projection(name=projection_name)
# endregion Abort

# region Abort_NotFound
try:
    client.abort_projection(name="does-not-exist")
except exceptions.NotFound:
    pass
else:
    raise Exception("Projection exists")
# endregion Abort_NotFound

# region Reset
client.reset_projection(name=projection_name)
# endregion Reset

# region Reset_NotFound
try:
    client.reset_projection(name="does-not-exist")
except exceptions.NotFound:
    pass
else:
    raise Exception("Projection exists")
# endregion Reset_NotFound

# region Update
projection_query = """fromAll()
.when({
    $init() {
        return {
            count: 0,
        };
    },
    $any(s, e) {
        s.count += 1;
    }
})
.outputState();
"""

client.update_projection(
    name=projection_name,
    query=projection_query,
)
# endregion Update

# region Update_NotFound
try:
    client.update_projection(
        name="does-not-exist",
        query=projection_query,
    )
except exceptions.NotFound:
    pass
else:
    raise Exception("Projection exists")
# endregion Update_NotFound

# region Delete
# A projection must be disabled before it can be deleted.
client.disable_projection(name=projection_name)

# The projection can now be deleted
client.delete_projection(name=projection_name)
# endregion Delete

# region DeleteNotFound
try:
    client.delete_projection(name="does-not-exist")
except exceptions.NotFound:
    pass
else:
    raise Exception("Projection exists")
# endregion DeleteNotFound


# region RestartSubSystem
client.restart_projections_subsystem()
# endregion RestartSubSystem
