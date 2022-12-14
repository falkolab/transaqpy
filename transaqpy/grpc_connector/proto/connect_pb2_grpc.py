# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import transaqpy.grpc_connector.proto.connect_pb2 as connect__pb2


class ConnectServiceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.FetchResponseData = channel.unary_stream(
                '/transaqConnector.ConnectService/FetchResponseData',
                request_serializer=connect__pb2.DataRequest.SerializeToString,
                response_deserializer=connect__pb2.DataResponse.FromString,
                )
        self.SendCommand = channel.unary_unary(
                '/transaqConnector.ConnectService/SendCommand',
                request_serializer=connect__pb2.SendCommandRequest.SerializeToString,
                response_deserializer=connect__pb2.SendCommandResponse.FromString,
                )


class ConnectServiceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def FetchResponseData(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def SendCommand(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_ConnectServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'FetchResponseData': grpc.unary_stream_rpc_method_handler(
                    servicer.FetchResponseData,
                    request_deserializer=connect__pb2.DataRequest.FromString,
                    response_serializer=connect__pb2.DataResponse.SerializeToString,
            ),
            'SendCommand': grpc.unary_unary_rpc_method_handler(
                    servicer.SendCommand,
                    request_deserializer=connect__pb2.SendCommandRequest.FromString,
                    response_serializer=connect__pb2.SendCommandResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'transaqConnector.ConnectService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class ConnectService(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def FetchResponseData(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(request, target, '/transaqConnector.ConnectService/FetchResponseData',
            connect__pb2.DataRequest.SerializeToString,
            connect__pb2.DataResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def SendCommand(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/transaqConnector.ConnectService/SendCommand',
            connect__pb2.SendCommandRequest.SerializeToString,
            connect__pb2.SendCommandResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
