from __future__ import annotations

from typing import Any
from unittest import TestCase
from uuid import uuid4

from grpc import RpcError, StatusCode
from grpc._channel import _MultiThreadedRendezvous, _RPCState
from grpc._cython.cygrpc import IntegratedCall

from kurrentdbclient import StreamState
from kurrentdbclient.common import handle_rpc_error
from kurrentdbclient.exceptions import (
    AbortedByServerError,
    AccessDeniedError,
    CancelledByClientError,
    CancelledError,
    ConsistencyChecksFailedError,
    ConsumerTooSlowError,
    ExceptionThrownByHandlerError,
    FailedPreconditionError,
    GrpcDeadlineExceededError,
    GrpcError,
    KurrentDBClientError,
    MultiAppendToSameStreamError,
    NodeIsNotLeaderError,
    NotFoundError,
    RecordMaxSizeExceededError,
    ServiceUnavailableError,
    StreamIsDeletedError,
    StreamTombstonedError,
    TransactionMaxSizeExceededError,
    UnknownError,
    WrongCurrentVersionError,
)
from kurrentdbclient.streams import handle_streams_rpc_error
from tests.test_unpack_error_status import (
    status_with_append_consistency_violation_error_details_v2,
    status_with_append_record_size_exceeded_error_details_v2,
    status_with_append_transaction_size_exceeded_error_details_v2,
    status_with_not_leader_node_error_details_v2,
    status_with_some_unsupported_error_details_v2,
    status_with_stream_already_in_append_session_error_details_v2,
    status_with_stream_revision_conflict_error_details_v2,
    status_with_stream_tombstoned_error_details_v2,
)


class TestHandleRpcError(TestCase):
    def test_handle_exception_thrown_by_handler(self) -> None:
        with self.assertRaises(ExceptionThrownByHandlerError):
            raise handle_rpc_error(FakeExceptionThrownByHandlerError()) from None

    def test_handle_deadline_exceeded_error(self) -> None:
        with self.assertRaises(GrpcDeadlineExceededError):
            raise handle_rpc_error(FakeDeadlineExceededRpcError()) from None

    def test_handle_unavailable_error(self) -> None:
        with self.assertRaises(ServiceUnavailableError):
            raise handle_rpc_error(FakeUnavailableRpcError()) from None

    def test_handle_not_leader_node_error(self) -> None:
        with self.assertRaises(NodeIsNotLeaderError) as cm:
            raise handle_rpc_error(FakeNotLeaderNodeRpcError()) from None

        # Check the trailing metadata is parsed correctly.
        self.assertEqual(cm.exception.host, "127.0.0.1")
        self.assertEqual(cm.exception.port, 2111)
        self.assertIsNone(cm.exception.node_id)

    def test_handle_not_leader_node_v2_error(self) -> None:
        leader_host = "127.0.0.1"
        leader_port = 2111
        node_id = str(uuid4())
        with self.assertRaises(NodeIsNotLeaderError) as cm:
            raise handle_rpc_error(
                FakeNotLeaderNodeV2RpcError(
                    host=leader_host,
                    port=leader_port,
                    node_id=node_id,
                )
            ) from None

        # Check the status details are unpacked correctly.
        self.assertEqual(cm.exception.host, leader_host)
        self.assertEqual(cm.exception.port, leader_port)
        self.assertEqual(cm.exception.node_id, node_id)

    def test_handle_stream_revision_conflict_error_v2(self) -> None:
        stream_name = str(uuid4())
        with self.assertRaises(WrongCurrentVersionError) as cm:
            raise handle_rpc_error(
                FakeStreamRevisionConflictV2RpcError(
                    stream_name,
                    expected_revision=0,
                    actual_revision=(-1),
                )
            ) from None

        self.assertEqual(stream_name, cm.exception.stream_name)
        self.assertEqual(0, cm.exception.expected_version)
        self.assertEqual(StreamState.NO_STREAM, cm.exception.actual_version)

    def test_handle_stream_already_in_append_session_error_v2(self) -> None:
        stream_name = str(uuid4())
        with self.assertRaises(MultiAppendToSameStreamError) as cm:
            raise handle_rpc_error(
                FakeStreamAlreadyInAppendSessionV2RpcError(
                    stream_name,
                )
            ) from None

        self.assertEqual(stream_name, cm.exception.stream_name)

    def test_handle_stream_tombstoned_error_v2(self) -> None:
        stream_name = str(uuid4())
        with self.assertRaises(StreamTombstonedError) as cm:
            raise handle_rpc_error(
                FakeStreamTombstonedV2RpcError(stream=stream_name)
            ) from None

        self.assertEqual(stream_name, cm.exception.stream_name)

    def test_handle_append_record_size_exceeded_error_v2(self) -> None:
        stream_name = str(uuid4())
        event_id = uuid4()
        size = 100
        max_size = 50
        with self.assertRaises(RecordMaxSizeExceededError) as cm:
            raise handle_rpc_error(
                FakeAppendRecordSizeExceededV2RpcError(
                    stream=stream_name,
                    record_id=str(event_id),
                    size=size,
                    max_size=max_size,
                )
            ) from None

        self.assertEqual(stream_name, cm.exception.stream_name)
        self.assertEqual(event_id, cm.exception.event_id)
        self.assertEqual(size, cm.exception.size)
        self.assertEqual(max_size, cm.exception.max_size)

    def test_handle_append_transaction_size_exceeded_error_v2(self) -> None:
        size = 100
        max_size = 50
        with self.assertRaises(TransactionMaxSizeExceededError) as cm:
            raise handle_rpc_error(
                FakeAppendTransactionSizeExceededV2RpcError(
                    size=size, max_size=max_size
                )
            ) from None

        self.assertEqual(size, cm.exception.size)
        self.assertEqual(max_size, cm.exception.max_size)

    def test_handle_append_consistency_violation_error_v2(self) -> None:
        stream_name = str(uuid4())
        with self.assertRaises(ConsistencyChecksFailedError) as cm:
            raise handle_rpc_error(
                FakeAppendConsistencyViolationV2RpcError(
                    stream_name,
                )
            ) from None

        self.assertEqual(len(cm.exception.failures), 1)
        failure = cm.exception.failures[0]
        self.assertEqual(failure.check_index, 0)
        stream_state_failure = failure.stream_state_failure
        assert stream_state_failure is not None
        self.assertEqual(stream_state_failure.stream_name, stream_name)
        self.assertEqual(stream_state_failure.expected_state, -4)
        self.assertEqual(stream_state_failure.actual_state, -1)

    def test_handle_consumer_too_slow_error(self) -> None:
        with self.assertRaises(ConsumerTooSlowError):
            raise handle_rpc_error(FakeConsumerTooSlowError()) from None

    def test_handle_aborted_by_server_error(self) -> None:
        with self.assertRaises(AbortedByServerError):
            raise handle_rpc_error(FakeAbortedByServerError()) from None

    def test_handle_unknown_error(self) -> None:
        with self.assertRaises(UnknownError) as cm:
            raise handle_rpc_error(FakeUnknownRpcError()) from None
        self.assertEqual(UnknownError, cm.exception.__class__)

    def test_handle_non_call_rpc_error(self) -> None:
        # Check non-Call errors are handled.
        class MyRpcError(RpcError):
            pass

        my_rpc_error = MyRpcError("some non-Call error")
        with self.assertRaises(GrpcError) as cm:
            raise handle_rpc_error(my_rpc_error) from None
        self.assertEqual(cm.exception.__class__, GrpcError)
        self.assertEqual(cm.exception.args[0], str(my_rpc_error))

    def test_streams_unknown_error(self) -> None:
        with self.assertRaises(UnknownError):
            raise handle_streams_rpc_error(FakeUnknownRpcError()) from None

    def test_stream_not_found_error(self) -> None:
        with self.assertRaises(NotFoundError):
            raise handle_streams_rpc_error(
                FakeWrongExpectedVersionActuallyMinusOneError()
            ) from None

    def test_stream_wrong_version_error(self) -> None:
        with self.assertRaises(WrongCurrentVersionError):
            raise handle_streams_rpc_error(
                FakeWrongExpectedVersionActuallyPlusOneError()
            ) from None

    def test_stream_deleted_error(self) -> None:
        with self.assertRaises(StreamIsDeletedError):
            raise handle_streams_rpc_error(FakeStreamIsDeletedError()) from None

    def test_stream_other_failed_precondition_error(self) -> None:
        with self.assertRaises(FailedPreconditionError):
            raise handle_streams_rpc_error(FakeFailedPreconditionRpcError()) from None

    def test_handle_unsupported_v2_error(self) -> None:
        with self.assertRaises(KurrentDBClientError) as cm:
            raise handle_rpc_error(FakeUnsupportedV2RpcError()) from None
        self.assertEqual(KurrentDBClientError, cm.exception.__class__)
        self.assertEqual("Actually OK", cm.exception.args[0])

    def test_access_denied_error(self) -> None:
        with self.assertRaises(AccessDeniedError):
            raise handle_rpc_error(FakeAccessDeniedError()) from None

    def test_cancelled_error(self) -> None:
        with self.assertRaises(CancelledError) as cm:
            raise handle_rpc_error(FakeCancelledError()) from None
        self.assertNotIsInstance(cm.exception, CancelledByClientError)

    def test_cancelled_by_client_error(self) -> None:
        with self.assertRaises(CancelledByClientError):
            raise handle_rpc_error(
                FakeCancelledError("Locally cancelled by application!")
            ) from None


class FakeRpcError(_MultiThreadedRendezvous):
    def __init__(
        self,
        status_code: StatusCode,
        details: str = "",
        trailing_metadata: list[tuple[str, str | bytes]] | None = None,
    ) -> None:
        super().__init__(
            state=_RPCState(
                due=[],
                initial_metadata=None,
                trailing_metadata=trailing_metadata,
                code=status_code,
                details=details,
            ),
            call=IntegratedCall(None, None),
            response_deserializer=lambda x: x,
            deadline=None,
        )

    def trailing_metadata(self) -> Any:
        return self._state.trailing_metadata


class FakeExceptionThrownByHandlerError(FakeRpcError):
    def __init__(self) -> None:
        super().__init__(
            status_code=StatusCode.UNKNOWN, details="Exception was thrown by handler."
        )


class FakeDeadlineExceededRpcError(FakeRpcError):
    def __init__(self) -> None:
        super().__init__(status_code=StatusCode.DEADLINE_EXCEEDED)


class FakeUnavailableRpcError(FakeRpcError):
    def __init__(self) -> None:
        super().__init__(status_code=StatusCode.UNAVAILABLE)


class FakeNotLeaderNodeRpcError(FakeRpcError):
    def __init__(self) -> None:
        super().__init__(
            status_code=StatusCode.NOT_FOUND,
            details="Leader info available",
            trailing_metadata=[
                ("leader-endpoint-host", "127.0.0.1"),
                ("leader-endpoint-port", "2111"),
            ],
        )


class FakeNotLeaderNodeV2RpcError(FakeRpcError):
    def __init__(self, host: str, port: int, node_id: str) -> None:
        message = (
            "The server is not the leader node and cannot handle "
            "the request. Please retry your request against the "
            f"leader node directly at {host}:{port}"
        )
        super().__init__(
            status_code=StatusCode.FAILED_PRECONDITION,
            details=message,
            trailing_metadata=[
                (
                    "grpc-status-details-bin",
                    status_with_not_leader_node_error_details_v2(
                        message=message,
                        host="127.0.0.1",
                        port=2111,
                        node_id=node_id,
                    ).SerializeToString(),
                ),
            ],
        )


class FakeStreamRevisionConflictV2RpcError(FakeRpcError):
    def __init__(
        self, stream: str, expected_revision: int, actual_revision: int
    ) -> None:
        message = (
            f"Append failed due to a revision conflict on stream '{stream}'."
            f" Expected revision: {expected_revision}."
            f" Actual revision: {actual_revision}."
        )
        super().__init__(
            status_code=StatusCode.FAILED_PRECONDITION,
            details=message,
            trailing_metadata=[
                (
                    "grpc-status-details-bin",
                    status_with_stream_revision_conflict_error_details_v2(
                        message=message,
                        stream=stream,
                        expected_revision=expected_revision,
                        actual_revision=actual_revision,
                    ).SerializeToString(),
                ),
            ],
        )


class FakeStreamAlreadyInAppendSessionV2RpcError(FakeRpcError):
    def __init__(self, stream: str) -> None:
        message = (
            f"Stream '{stream}' is already part of this append session."
            f" Appending to the same stream multiple times is currently"
            f" not supported."
        )
        super().__init__(
            status_code=StatusCode.ABORTED,
            details=message,
            trailing_metadata=[
                (
                    "grpc-status-details-bin",
                    status_with_stream_already_in_append_session_error_details_v2(
                        message=message,
                        stream=stream,
                    ).SerializeToString(),
                ),
            ],
        )


class FakeStreamTombstonedV2RpcError(FakeRpcError):
    def __init__(self, stream: str) -> None:
        message = (
            f"Stream '{stream}' has been tombstoned. It has been"
            f" permanently removed from the system and cannot be restored."
        )
        super().__init__(
            status_code=StatusCode.FAILED_PRECONDITION,
            details=message,
            trailing_metadata=[
                (
                    "grpc-status-details-bin",
                    status_with_stream_tombstoned_error_details_v2(
                        message=message,
                        stream=stream,
                    ).SerializeToString(),
                ),
            ],
        )


class FakeAppendRecordSizeExceededV2RpcError(FakeRpcError):
    def __init__(self, stream: str, record_id: str, size: int, max_size: int) -> None:
        size_mb = size / (1024 * 1014)
        max_size_mb = max_size / (1024 * 1014)
        diff_mb = size_mb - max_size_mb
        message = (
            f"'The size of record {record_id} ({size_mb:.3f} MB) exceeds the maximum"
            f" allowed size of {max_size_mb:.3f} MB bytes by {diff_mb:.3} MB'"
        )
        super().__init__(
            status_code=StatusCode.INVALID_ARGUMENT,
            details=message,
            trailing_metadata=[
                (
                    "grpc-status-details-bin",
                    status_with_append_record_size_exceeded_error_details_v2(
                        message=message,
                        stream=stream,
                        record_id=record_id,
                        size=size,
                        max_size=max_size,
                    ).SerializeToString(),
                ),
            ],
        )


class FakeAppendTransactionSizeExceededV2RpcError(FakeRpcError):
    def __init__(self, size: int, max_size: int) -> None:
        size_mb = size / (1024 * 1014)
        max_size_mb = max_size / (1024 * 1014)
        diff_mb = size_mb - max_size_mb
        message = (
            f"Transaction size ({size_mb:.3f} MB) exceeded"
            f" the maximum allowed size of {max_size_mb:.3f} MB"
            f" by {diff_mb:.3f} MB, after 26 record(s)."
        )
        super().__init__(
            status_code=StatusCode.ABORTED,
            details=message,
            trailing_metadata=[
                (
                    "grpc-status-details-bin",
                    status_with_append_transaction_size_exceeded_error_details_v2(
                        message=message,
                        size=size,
                        max_size=max_size,
                    ).SerializeToString(),
                ),
            ],
        )


class FakeUnsupportedV2RpcError(FakeRpcError):
    def __init__(self) -> None:
        message = "Actually OK"
        super().__init__(
            status_code=StatusCode.OK,
            details=message,
            trailing_metadata=[
                (
                    "grpc-status-details-bin",
                    status_with_some_unsupported_error_details_v2(
                        message=message,
                    ).SerializeToString(),
                ),
            ],
        )


class FakeAppendConsistencyViolationV2RpcError(FakeRpcError):
    def __init__(self, stream: str) -> None:
        message = "Append failed due to consistency violations....."
        super().__init__(
            status_code=StatusCode.FAILED_PRECONDITION,
            details=message,
            trailing_metadata=[
                (
                    "grpc-status-details-bin",
                    status_with_append_consistency_violation_error_details_v2(
                        message=message,
                        stream=stream,
                    ).SerializeToString(),
                ),
            ],
        )


class FakeConsumerTooSlowError(FakeRpcError):
    def __init__(self) -> None:
        super().__init__(status_code=StatusCode.ABORTED, details="Consumer too slow")


class FakeAbortedByServerError(FakeRpcError):
    def __init__(self) -> None:
        super().__init__(status_code=StatusCode.ABORTED, details="")


class FakeUnknownRpcError(FakeRpcError):
    def __init__(self) -> None:
        super().__init__(status_code=StatusCode.UNKNOWN)


class FakeFailedPreconditionRpcError(FakeRpcError):
    def __init__(self, details: str = "") -> None:
        super().__init__(status_code=StatusCode.FAILED_PRECONDITION, details=details)


class FakeWrongExpectedVersionActuallyMinusOneError(FakeFailedPreconditionRpcError):
    def __init__(self) -> None:
        super().__init__(
            details="Some WrongExpectedVersion reason. Stream: blah, "
            "Expected version: 10, Actual version: -1"
        )


class FakeWrongExpectedVersionActuallyPlusOneError(FakeFailedPreconditionRpcError):
    def __init__(self) -> None:
        super().__init__(
            details="Some WrongExpectedVersion reason. Stream: blah, "
            "Expected version: 10, Actual version: 1"
        )


class FakeStreamIsDeletedError(FakeFailedPreconditionRpcError):
    def __init__(self) -> None:
        super().__init__(details="is deleted")


class FakeAccessDeniedError(FakeRpcError):
    def __init__(self) -> None:
        super().__init__(status_code=StatusCode.PERMISSION_DENIED, details="")


class FakeCancelledError(FakeRpcError):
    def __init__(self, details: str = "") -> None:
        super().__init__(status_code=StatusCode.CANCELLED, details=details)
