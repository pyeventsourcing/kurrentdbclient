# ruff: noqa: EM101, F704, PLE1142
# https://github.com/EventStore/EventStore-Client-NodeJS/blob/master/packages/test/src/samples/projection-management.ts
import sys
import traceback
from time import sleep
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

await client.create_projection(
    name=projection_name,
    query=projection_query,
)
# endregion CreateContinuous

# region CreateContinuous_Conflict
try:
    await client.create_projection(
        name=projection_name,
        query=projection_query,
    )
except exceptions.AlreadyExistsError:
    print("projection already exists")
    # endregion CreateContinuous_Conflict
else:
    raise Exception("Projection didn't already exist")


# region Enable
await client.enable_projection(name=projection_name)
# endregion Enable

# region EnableNotFound
try:
    await client.enable_projection(name="does-not-exist")
except exceptions.NotFoundError:
    print("projection not found")
    # endregion EnableNotFound
else:
    raise Exception("Projection exists")

await client.append_events(
    stream_name=str(uuid4()),
    events=[NewEvent(type="SampleEvent", data=b"{}")],
    current_version=StreamState.NO_STREAM,
)
sleep(0.5)

# region GetStatus
statistics = await client.get_projection_statistics(name=projection_name)
print("Projection name:", statistics.name)
print("Projection status:", statistics.status)
print("Projection checkpoint status", statistics.checkpoint_status)
print("Projection mode:", statistics.mode)
print("Projection progress:", statistics.progress)
# endregion GetStatus

try:
    # region ListAll
    list_of_statistics = await client.list_all_projection_statistics()
    # endregion ListAll
    print(list_of_statistics)
except exceptions.ExceptionThrownByHandlerError:
    sys.stderr.write(
        f"Exception thrown by list_all_projection_statistics() handler:"
        f" {traceback.format_exc()}\n"
    )
    sys.stderr.flush()

try:
    # region ListContinuous
    list_of_statistics = (
        await client.list_continuous_projection_statistics()
    )
    # endregion ListContinuous
    print(list_of_statistics)
except exceptions.ExceptionThrownByHandlerError:
    sys.stderr.write(
        f"Exception thrown by list_continuous_projection_statistics() handler: "
        f"{traceback.format_exc()}\n"
    )
    sys.stderr.flush()


# region GetState
state = await client.get_projection_state(name=projection_name)
print(f"Counted {state.value['count']} events")
# endregion GetState

# region GetResult
state = await client.get_projection_state(name=projection_name)
print(f"Counted {state.value['count']} events")
# endregion GetResult


# region Disable
await client.disable_projection(name=projection_name)
# endregion Disable

# region DisableNotFound
try:
    await client.disable_projection(name="does-not-exist")
except exceptions.NotFoundError:
    print("projection not found")
    # endregion DisableNotFound
else:
    raise Exception("Projection exists")

# region Abort
await client.abort_projection(name=projection_name)
# endregion Abort

# region Abort_NotFound
try:
    await client.abort_projection(name="does-not-exist")
except exceptions.NotFoundError:
    print("projection not found")
    # endregion Abort_NotFound
else:
    raise Exception("Projection exists")

# region Reset
await client.reset_projection(name=projection_name)
# endregion Reset

# region Reset_NotFound
try:
    await client.reset_projection(name="does-not-exist")
except exceptions.NotFoundError:
    print("projection not found")
    # endregion Reset_NotFound
else:
    raise Exception("Projection exists")

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

await client.update_projection(
    name=projection_name,
    query=projection_query,
)
# endregion Update

# region Update_NotFound
try:
    await client.update_projection(
        name="does-not-exist",
        query=projection_query,
    )
except exceptions.NotFoundError:
    print("projection not found")
    # endregion Update_NotFound
else:
    raise Exception("Projection exists")

# region Delete
# A projection must be disabled before it can be deleted.
await client.disable_projection(name=projection_name)

# The projection can now be deleted
await client.delete_projection(name=projection_name)
# endregion Delete

# region DeleteNotFound
try:
    await client.delete_projection(name="does-not-exist")
except exceptions.NotFoundError:
    print("projection not found")
    # endregion DeleteNotFound
else:
    raise Exception("Projection exists")


# region RestartSubSystem
await client.restart_projections_subsystem()
# endregion RestartSubSystem

await client.close()
