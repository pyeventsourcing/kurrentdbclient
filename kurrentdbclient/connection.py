from __future__ import annotations

import asyncio
import contextlib
from typing import TYPE_CHECKING
from uuid import uuid4

import grpc.aio

from kurrentdbclient.common import AsyncGrpcStreamers, GrpcStreamers
from kurrentdbclient.gossip import AsyncGossipService, GossipService
from kurrentdbclient.persistent import (
    AsyncPersistentSubscriptionsService,
    PersistentSubscriptionsService,
)
from kurrentdbclient.projections import AsyncProjectionsService, ProjectionsService
from kurrentdbclient.streams import AsyncStreamsService, StreamsService
from kurrentdbclient.v2streams import AsyncV2StreamsService, V2StreamsService

if TYPE_CHECKING:
    from kurrentdbclient.connection_spec import ConnectionSpec


class BaseKurrentDBConnection:
    def __init__(self, grpc_target: str):
        self._grpc_target = grpc_target
        self.connection_id = uuid4()

    @property
    def grpc_target(self) -> str:
        return self._grpc_target


class KurrentDBConnection(BaseKurrentDBConnection):
    def __init__(
        self,
        grpc_channel: grpc.Channel,
        grpc_target: str,
        connection_spec: ConnectionSpec,
    ) -> None:
        super().__init__(grpc_target)
        self._grpc_channel = grpc_channel
        self._grpc_streamers = GrpcStreamers()
        self.gossip = GossipService(
            channel=grpc_channel,
            connection_spec=connection_spec,
            grpc_streamers=self._grpc_streamers,
        )
        self.streams = StreamsService(
            grpc_channel=grpc_channel,
            connection_spec=connection_spec,
            grpc_streamers=self._grpc_streamers,
        )
        self.v2streams = V2StreamsService(
            grpc_channel=grpc_channel,
            connection_spec=connection_spec,
            grpc_streamers=self._grpc_streamers,
        )
        self.persistent_subscriptions = PersistentSubscriptionsService(
            channel=grpc_channel,
            connection_spec=connection_spec,
            grpc_streamers=self._grpc_streamers,
        )
        self.projections = ProjectionsService(
            channel=grpc_channel,
            connection_spec=connection_spec,
            grpc_streamers=self._grpc_streamers,
        )

    def close(self) -> None:
        self._grpc_streamers.close()
        self._grpc_channel.close()


class AsyncKurrentDBConnection(BaseKurrentDBConnection):
    def __init__(
        self,
        grpc_channel: grpc.aio.Channel,
        grpc_target: str,
        connection_spec: ConnectionSpec,
    ) -> None:
        super().__init__(grpc_target)
        self._grpc_channel = grpc_channel
        self._grpc_target = grpc_target
        self._grpc_streamers = AsyncGrpcStreamers()
        self.gossip = AsyncGossipService(
            grpc_channel,
            connection_spec=connection_spec,
            grpc_streamers=self._grpc_streamers,
        )
        self.streams = AsyncStreamsService(
            grpc_channel,
            connection_spec=connection_spec,
            grpc_streamers=self._grpc_streamers,
        )
        self.persistent_subscriptions = AsyncPersistentSubscriptionsService(
            grpc_channel,
            connection_spec=connection_spec,
            grpc_streamers=self._grpc_streamers,
        )
        self.projections = AsyncProjectionsService(
            grpc_channel,
            connection_spec=connection_spec,
            grpc_streamers=self._grpc_streamers,
        )
        self.v2streams = AsyncV2StreamsService(
            grpc_channel,
            connection_spec=connection_spec,
            grpc_streamers=self._grpc_streamers,
        )

    async def close(self) -> None:
        await self._grpc_streamers.close()
        await self._grpc_channel.close(grace=5)

        # Actively wait for the gRPC channel to reach the SHUTDOWN state.
        # This guarantees the C-core has finished all teardown operations
        # and fired all its callbacks before we let the event loop close.
        async def _wait_for_shutdown() -> None:
            state = self._grpc_channel.get_state(try_to_connect=False)
            while state != grpc.ChannelConnectivity.SHUTDOWN:  # pragma: no cover
                await self._grpc_channel.wait_for_state_change(state)
                state = self._grpc_channel.get_state(try_to_connect=False)

        with contextlib.suppress(asyncio.TimeoutError, grpc.FutureTimeoutError):
            # Will exit instantly if already SHUTDOWN
            await asyncio.wait_for(_wait_for_shutdown(), timeout=2.0)
