# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings

from kurrentdbclient.protos.Grpc import persistent_pb2 as kurrentdbclient_dot_protos_dot_Grpc_dot_persistent__pb2
from kurrentdbclient.protos.Grpc import shared_pb2 as kurrentdbclient_dot_protos_dot_Grpc_dot_shared__pb2

GRPC_GENERATED_VERSION = '1.71.0'
GRPC_VERSION = grpc.__version__
_version_not_supported = False

try:
    from grpc._utilities import first_version_is_lower
    _version_not_supported = first_version_is_lower(GRPC_VERSION, GRPC_GENERATED_VERSION)
except ImportError:
    _version_not_supported = True

if _version_not_supported:
    raise RuntimeError(
        f'The grpc package installed is at version {GRPC_VERSION},'
        + f' but the generated code in kurrentdbclient/protos/Grpc/persistent_pb2_grpc.py depends on'
        + f' grpcio>={GRPC_GENERATED_VERSION}.'
        + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}'
        + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'
    )


class PersistentSubscriptionsStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.Create = channel.unary_unary(
                '/event_store.client.persistent_subscriptions.PersistentSubscriptions/Create',
                request_serializer=kurrentdbclient_dot_protos_dot_Grpc_dot_persistent__pb2.CreateReq.SerializeToString,
                response_deserializer=kurrentdbclient_dot_protos_dot_Grpc_dot_persistent__pb2.CreateResp.FromString,
                _registered_method=True)
        self.Update = channel.unary_unary(
                '/event_store.client.persistent_subscriptions.PersistentSubscriptions/Update',
                request_serializer=kurrentdbclient_dot_protos_dot_Grpc_dot_persistent__pb2.UpdateReq.SerializeToString,
                response_deserializer=kurrentdbclient_dot_protos_dot_Grpc_dot_persistent__pb2.UpdateResp.FromString,
                _registered_method=True)
        self.Delete = channel.unary_unary(
                '/event_store.client.persistent_subscriptions.PersistentSubscriptions/Delete',
                request_serializer=kurrentdbclient_dot_protos_dot_Grpc_dot_persistent__pb2.DeleteReq.SerializeToString,
                response_deserializer=kurrentdbclient_dot_protos_dot_Grpc_dot_persistent__pb2.DeleteResp.FromString,
                _registered_method=True)
        self.Read = channel.stream_stream(
                '/event_store.client.persistent_subscriptions.PersistentSubscriptions/Read',
                request_serializer=kurrentdbclient_dot_protos_dot_Grpc_dot_persistent__pb2.ReadReq.SerializeToString,
                response_deserializer=kurrentdbclient_dot_protos_dot_Grpc_dot_persistent__pb2.ReadResp.FromString,
                _registered_method=True)
        self.GetInfo = channel.unary_unary(
                '/event_store.client.persistent_subscriptions.PersistentSubscriptions/GetInfo',
                request_serializer=kurrentdbclient_dot_protos_dot_Grpc_dot_persistent__pb2.GetInfoReq.SerializeToString,
                response_deserializer=kurrentdbclient_dot_protos_dot_Grpc_dot_persistent__pb2.GetInfoResp.FromString,
                _registered_method=True)
        self.ReplayParked = channel.unary_unary(
                '/event_store.client.persistent_subscriptions.PersistentSubscriptions/ReplayParked',
                request_serializer=kurrentdbclient_dot_protos_dot_Grpc_dot_persistent__pb2.ReplayParkedReq.SerializeToString,
                response_deserializer=kurrentdbclient_dot_protos_dot_Grpc_dot_persistent__pb2.ReplayParkedResp.FromString,
                _registered_method=True)
        self.List = channel.unary_unary(
                '/event_store.client.persistent_subscriptions.PersistentSubscriptions/List',
                request_serializer=kurrentdbclient_dot_protos_dot_Grpc_dot_persistent__pb2.ListReq.SerializeToString,
                response_deserializer=kurrentdbclient_dot_protos_dot_Grpc_dot_persistent__pb2.ListResp.FromString,
                _registered_method=True)
        self.RestartSubsystem = channel.unary_unary(
                '/event_store.client.persistent_subscriptions.PersistentSubscriptions/RestartSubsystem',
                request_serializer=kurrentdbclient_dot_protos_dot_Grpc_dot_shared__pb2.Empty.SerializeToString,
                response_deserializer=kurrentdbclient_dot_protos_dot_Grpc_dot_shared__pb2.Empty.FromString,
                _registered_method=True)


class PersistentSubscriptionsServicer(object):
    """Missing associated documentation comment in .proto file."""

    def Create(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Update(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Delete(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Read(self, request_iterator, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetInfo(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def ReplayParked(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def List(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def RestartSubsystem(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_PersistentSubscriptionsServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'Create': grpc.unary_unary_rpc_method_handler(
                    servicer.Create,
                    request_deserializer=kurrentdbclient_dot_protos_dot_Grpc_dot_persistent__pb2.CreateReq.FromString,
                    response_serializer=kurrentdbclient_dot_protos_dot_Grpc_dot_persistent__pb2.CreateResp.SerializeToString,
            ),
            'Update': grpc.unary_unary_rpc_method_handler(
                    servicer.Update,
                    request_deserializer=kurrentdbclient_dot_protos_dot_Grpc_dot_persistent__pb2.UpdateReq.FromString,
                    response_serializer=kurrentdbclient_dot_protos_dot_Grpc_dot_persistent__pb2.UpdateResp.SerializeToString,
            ),
            'Delete': grpc.unary_unary_rpc_method_handler(
                    servicer.Delete,
                    request_deserializer=kurrentdbclient_dot_protos_dot_Grpc_dot_persistent__pb2.DeleteReq.FromString,
                    response_serializer=kurrentdbclient_dot_protos_dot_Grpc_dot_persistent__pb2.DeleteResp.SerializeToString,
            ),
            'Read': grpc.stream_stream_rpc_method_handler(
                    servicer.Read,
                    request_deserializer=kurrentdbclient_dot_protos_dot_Grpc_dot_persistent__pb2.ReadReq.FromString,
                    response_serializer=kurrentdbclient_dot_protos_dot_Grpc_dot_persistent__pb2.ReadResp.SerializeToString,
            ),
            'GetInfo': grpc.unary_unary_rpc_method_handler(
                    servicer.GetInfo,
                    request_deserializer=kurrentdbclient_dot_protos_dot_Grpc_dot_persistent__pb2.GetInfoReq.FromString,
                    response_serializer=kurrentdbclient_dot_protos_dot_Grpc_dot_persistent__pb2.GetInfoResp.SerializeToString,
            ),
            'ReplayParked': grpc.unary_unary_rpc_method_handler(
                    servicer.ReplayParked,
                    request_deserializer=kurrentdbclient_dot_protos_dot_Grpc_dot_persistent__pb2.ReplayParkedReq.FromString,
                    response_serializer=kurrentdbclient_dot_protos_dot_Grpc_dot_persistent__pb2.ReplayParkedResp.SerializeToString,
            ),
            'List': grpc.unary_unary_rpc_method_handler(
                    servicer.List,
                    request_deserializer=kurrentdbclient_dot_protos_dot_Grpc_dot_persistent__pb2.ListReq.FromString,
                    response_serializer=kurrentdbclient_dot_protos_dot_Grpc_dot_persistent__pb2.ListResp.SerializeToString,
            ),
            'RestartSubsystem': grpc.unary_unary_rpc_method_handler(
                    servicer.RestartSubsystem,
                    request_deserializer=kurrentdbclient_dot_protos_dot_Grpc_dot_shared__pb2.Empty.FromString,
                    response_serializer=kurrentdbclient_dot_protos_dot_Grpc_dot_shared__pb2.Empty.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'event_store.client.persistent_subscriptions.PersistentSubscriptions', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('event_store.client.persistent_subscriptions.PersistentSubscriptions', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class PersistentSubscriptions(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def Create(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/event_store.client.persistent_subscriptions.PersistentSubscriptions/Create',
            kurrentdbclient_dot_protos_dot_Grpc_dot_persistent__pb2.CreateReq.SerializeToString,
            kurrentdbclient_dot_protos_dot_Grpc_dot_persistent__pb2.CreateResp.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def Update(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/event_store.client.persistent_subscriptions.PersistentSubscriptions/Update',
            kurrentdbclient_dot_protos_dot_Grpc_dot_persistent__pb2.UpdateReq.SerializeToString,
            kurrentdbclient_dot_protos_dot_Grpc_dot_persistent__pb2.UpdateResp.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def Delete(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/event_store.client.persistent_subscriptions.PersistentSubscriptions/Delete',
            kurrentdbclient_dot_protos_dot_Grpc_dot_persistent__pb2.DeleteReq.SerializeToString,
            kurrentdbclient_dot_protos_dot_Grpc_dot_persistent__pb2.DeleteResp.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def Read(request_iterator,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.stream_stream(
            request_iterator,
            target,
            '/event_store.client.persistent_subscriptions.PersistentSubscriptions/Read',
            kurrentdbclient_dot_protos_dot_Grpc_dot_persistent__pb2.ReadReq.SerializeToString,
            kurrentdbclient_dot_protos_dot_Grpc_dot_persistent__pb2.ReadResp.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def GetInfo(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/event_store.client.persistent_subscriptions.PersistentSubscriptions/GetInfo',
            kurrentdbclient_dot_protos_dot_Grpc_dot_persistent__pb2.GetInfoReq.SerializeToString,
            kurrentdbclient_dot_protos_dot_Grpc_dot_persistent__pb2.GetInfoResp.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def ReplayParked(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/event_store.client.persistent_subscriptions.PersistentSubscriptions/ReplayParked',
            kurrentdbclient_dot_protos_dot_Grpc_dot_persistent__pb2.ReplayParkedReq.SerializeToString,
            kurrentdbclient_dot_protos_dot_Grpc_dot_persistent__pb2.ReplayParkedResp.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def List(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/event_store.client.persistent_subscriptions.PersistentSubscriptions/List',
            kurrentdbclient_dot_protos_dot_Grpc_dot_persistent__pb2.ListReq.SerializeToString,
            kurrentdbclient_dot_protos_dot_Grpc_dot_persistent__pb2.ListResp.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def RestartSubsystem(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/event_store.client.persistent_subscriptions.PersistentSubscriptions/RestartSubsystem',
            kurrentdbclient_dot_protos_dot_Grpc_dot_shared__pb2.Empty.SerializeToString,
            kurrentdbclient_dot_protos_dot_Grpc_dot_shared__pb2.Empty.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)
