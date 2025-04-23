from __future__ import annotations

import grpc


class KurrentDBClientError(Exception):
    """
    Base class for exceptions raised by the client.
    """


class ProgrammingError(Exception):
    """
    Raised when programming errors are encountered.
    """


class GrpcError(KurrentDBClientError):
    """
    Base class for exceptions raised by gRPC.
    """


class ExceptionThrownByHandlerError(GrpcError):
    """
    Raised when gRPC service returns RpcError with status
    code "UNKNOWN" and details "Exception was thrown by handler.".
    """


class ServiceUnavailableError(GrpcError):
    """
    Raised when gRPC service is unavailable.
    """


class SSLError(ServiceUnavailableError):
    """
    Raised when gRPC service is unavailable due to SSL error.
    """


class DeadlineExceededError(KurrentDBClientError):
    """
    Base class for exceptions involving deadlines being exceeded.
    """


class GrpcDeadlineExceededError(GrpcError, DeadlineExceededError):
    """
    Raised when gRPC operation times out.
    """


class CancelledByClientError(KurrentDBClientError):
    """
    Raised when gRPC operation is cancelled.
    """


class AbortedByServerError(GrpcError):
    """
    Raised when gRPC operation is aborted.
    """


class ConsumerTooSlowError(AbortedByServerError):
    """
    Raised when buffer is overloaded.
    """


class NodeIsNotLeaderError(KurrentDBClientError):
    """
    Raised when client attempts to write to a node that is not a leader.
    """

    @property
    def leader_grpc_target(self) -> str | None:
        if (
            self.args
            and isinstance(self.args[0], (grpc.Call, grpc.aio.AioRpcError))
            and self.args[0].code() == grpc.StatusCode.NOT_FOUND
            and self.args[0].details() == "Leader info available"
        ):
            # The typing of trailing_metadata is a mess.
            rpc_error = self.args[0]
            trailing_metadata: dict[str, str | bytes]
            if isinstance(rpc_error, grpc.Call):
                trailing_metadata = {
                    m.key: m.value for m in rpc_error.trailing_metadata()  # type: ignore[attr-defined]
                }
            else:
                assert isinstance(rpc_error, grpc.aio.AioRpcError)
                trailing_metadata = rpc_error.trailing_metadata()  # type: ignore[assignment]

            host = trailing_metadata["leader-endpoint-host"]
            port = trailing_metadata["leader-endpoint-port"]
            if isinstance(host, bytes):
                host = host.decode("utf-8")  # pragma: no cover
            if isinstance(port, bytes):
                port = port.decode("utf-8")  # pragma: no cover
            return f"{host}:{port}"
        return None


class NotFoundError(KurrentDBClientError):
    """
    Raised when stream or subscription or projection is not found.
    """


class AlreadyExistsError(KurrentDBClientError):
    """
    Raised when creating something, e.g. a persistent subscription, that already exists.
    """


class SubscriptionConfirmationError(KurrentDBClientError):
    """
    Raised when subscription confirmation fails.
    """


class WrongCurrentVersionError(KurrentDBClientError):
    """
    Raised when expected position does not match the
    stream position of the last event in a stream.
    """


class AccessDeniedError(KurrentDBClientError):
    """
    Raised when access is denied by the server.
    """


class StreamIsDeletedError(KurrentDBClientError):
    """
    Raised when reading from or appending to a stream that has been
    tombstoned, and when deleting a stream that has been deleted
    whilst expecting the stream exists, and when getting or setting
    metadata for a stream that has been tombstoned, and when deleting
    a stream that has been tombstoned, and when tombstoning a stream
    that has been tombstoned.
    """


class AppendDeadlineExceededError(DeadlineExceededError):
    """
    Raised when append operation is timed out by the server.
    """


class UnknownError(KurrentDBClientError):
    """
    Raised when append operation fails with an "unknown" error.
    """


class InvalidTransactionError(KurrentDBClientError):
    """
    Raised when append operation fails with an "invalid transaction" error.
    """


class OperationFailedError(GrpcError):
    """
    Raised when an operation fails (e.g. deleting a projection that isn't disabled).
    """


class MaximumAppendSizeExceededError(KurrentDBClientError):
    """
    Raised when append operation fails with a "maximum append size exceeded" error.
    """


class BadRequestError(KurrentDBClientError):
    """
    Raised when append operation fails with a "bad request" error.
    """


class DiscoveryFailedError(KurrentDBClientError):
    """
    Raised when client fails to satisfy node preference using gossip cluster info.
    """


class LeaderNotFoundError(DiscoveryFailedError):
    """
    Raised when NodePreference is 'follower' but the cluster has no such nodes.
    """


class FollowerNotFoundError(DiscoveryFailedError):
    """
    Raised when NodePreference is 'follower' but the cluster has no such nodes.
    """


class ReadOnlyReplicaNotFoundError(DiscoveryFailedError):
    """
    Raised when NodePreference is 'readonlyreplica' but the cluster has no such nodes.
    """


class ExceptionIteratingRequestsError(KurrentDBClientError):
    """
    Raised when a persistent subscription errors whilst iterating requests.

    This helps debugging because otherwise we just get a gRPC error
    that says "Exception iterating requests!"
    """


class FailedPreconditionError(KurrentDBClientError):
    """
    Raised when a "failed precondition" status error is encountered.
    """


class MaximumSubscriptionsReachedError(FailedPreconditionError):
    """
    Raised when trying to read from a persistent subscription that
    is already being read by the maximum number of subscribers.
    """


class InternalError(GrpcError):
    """
    Raised when a grpc INTERNAL error is encountered.
    """
