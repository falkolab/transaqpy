# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: connect.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\rconnect.proto\x12\x10transaqConnector\"\r\n\x0b\x44\x61taRequest\"\x1f\n\x0c\x44\x61taResponse\x12\x0f\n\x07message\x18\x01 \x01(\t\"%\n\x12SendCommandRequest\x12\x0f\n\x07message\x18\x01 \x01(\t\"&\n\x13SendCommandResponse\x12\x0f\n\x07message\x18\x01 \x01(\t2\xc6\x01\n\x0e\x43onnectService\x12V\n\x11\x46\x65tchResponseData\x12\x1d.transaqConnector.DataRequest\x1a\x1e.transaqConnector.DataResponse\"\x00\x30\x01\x12\\\n\x0bSendCommand\x12$.transaqConnector.SendCommandRequest\x1a%.transaqConnector.SendCommandResponse\"\x00\x62\x06proto3')



_DATAREQUEST = DESCRIPTOR.message_types_by_name['DataRequest']
_DATARESPONSE = DESCRIPTOR.message_types_by_name['DataResponse']
_SENDCOMMANDREQUEST = DESCRIPTOR.message_types_by_name['SendCommandRequest']
_SENDCOMMANDRESPONSE = DESCRIPTOR.message_types_by_name['SendCommandResponse']
DataRequest = _reflection.GeneratedProtocolMessageType('DataRequest', (_message.Message,), {
  'DESCRIPTOR' : _DATAREQUEST,
  '__module__' : 'connect_pb2'
  # @@protoc_insertion_point(class_scope:transaqConnector.DataRequest)
  })
_sym_db.RegisterMessage(DataRequest)

DataResponse = _reflection.GeneratedProtocolMessageType('DataResponse', (_message.Message,), {
  'DESCRIPTOR' : _DATARESPONSE,
  '__module__' : 'connect_pb2'
  # @@protoc_insertion_point(class_scope:transaqConnector.DataResponse)
  })
_sym_db.RegisterMessage(DataResponse)

SendCommandRequest = _reflection.GeneratedProtocolMessageType('SendCommandRequest', (_message.Message,), {
  'DESCRIPTOR' : _SENDCOMMANDREQUEST,
  '__module__' : 'connect_pb2'
  # @@protoc_insertion_point(class_scope:transaqConnector.SendCommandRequest)
  })
_sym_db.RegisterMessage(SendCommandRequest)

SendCommandResponse = _reflection.GeneratedProtocolMessageType('SendCommandResponse', (_message.Message,), {
  'DESCRIPTOR' : _SENDCOMMANDRESPONSE,
  '__module__' : 'connect_pb2'
  # @@protoc_insertion_point(class_scope:transaqConnector.SendCommandResponse)
  })
_sym_db.RegisterMessage(SendCommandResponse)

_CONNECTSERVICE = DESCRIPTOR.services_by_name['ConnectService']
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _DATAREQUEST._serialized_start=35
  _DATAREQUEST._serialized_end=48
  _DATARESPONSE._serialized_start=50
  _DATARESPONSE._serialized_end=81
  _SENDCOMMANDREQUEST._serialized_start=83
  _SENDCOMMANDREQUEST._serialized_end=120
  _SENDCOMMANDRESPONSE._serialized_start=122
  _SENDCOMMANDRESPONSE._serialized_end=160
  _CONNECTSERVICE._serialized_start=163
  _CONNECTSERVICE._serialized_end=361
# @@protoc_insertion_point(module_scope)
