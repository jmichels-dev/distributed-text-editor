# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: texteditor.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x10texteditor.proto\x12\x04\x63hat\"\x18\n\x08Username\x12\x0c\n\x04name\x18\x01 \x01(\t\"\x1d\n\x07Welcome\x12\x12\n\nwelcomeMsg\x18\x01 \x01(\t\".\n\x08\x44ownload\x12\x10\n\x08\x66ilename\x18\x01 \x01(\t\x12\x10\n\x08\x63ontents\x18\x03 \x01(\x0c\"3\n\x0c\x46ileResponse\x12\x11\n\terrorFlag\x18\x01 \x01(\x08\x12\x10\n\x08\x66ilename\x18\x02 \x01(\t\"\x14\n\x04\x44\x61ta\x12\x0c\n\x04\x64\x61ta\x18\x01 \x01(\x0c\"-\n\x07Unreads\x12\x11\n\terrorFlag\x18\x01 \x01(\x08\x12\x0f\n\x07unreads\x18\x02 \x01(\t\"\x16\n\x07Payload\x12\x0b\n\x03msg\x18\x01 \x01(\t\"p\n\x0bSendRequest\x12\x1e\n\x06sender\x18\x01 \x01(\x0b\x32\x0e.chat.Username\x12!\n\trecipient\x18\x02 \x01(\x0b\x32\x0e.chat.Username\x12\x1e\n\x07sentMsg\x18\x03 \x01(\x0b\x32\r.chat.Payload2\xf2\x03\n\nTextEditor\x12\x34\n\x0cSaveToServer\x12\x0e.chat.Download\x1a\x12.chat.FileResponse\"\x00\x12<\n\x10\x44\x65leteFromServer\x12\x12.chat.FileResponse\x1a\x12.chat.FileResponse\"\x00\x12\x33\n\x0bOpenNewFile\x12\x0e.chat.Download\x1a\x12.chat.FileResponse\"\x00\x12\x32\n\x10OpenExistingFile\x12\x0e.chat.Download\x1a\n.chat.Data\"\x00\x30\x01\x12\x31\n\x0eSignInExisting\x12\x0e.chat.Username\x1a\r.chat.Welcome\"\x00\x12*\n\x07\x41\x64\x64User\x12\x0e.chat.Username\x1a\r.chat.Welcome\"\x00\x12*\n\x04Send\x12\x11.chat.SendRequest\x1a\r.chat.Payload\"\x00\x12&\n\x04List\x12\r.chat.Payload\x1a\r.chat.Payload\"\x00\x12)\n\x06Logout\x12\x0e.chat.Username\x1a\r.chat.Payload\"\x00\x12)\n\x06\x44\x65lete\x12\x0e.chat.Username\x1a\r.chat.Payload\"\x00\x62\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'texteditor_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _USERNAME._serialized_start=26
  _USERNAME._serialized_end=50
  _WELCOME._serialized_start=52
  _WELCOME._serialized_end=81
  _DOWNLOAD._serialized_start=83
  _DOWNLOAD._serialized_end=129
  _FILERESPONSE._serialized_start=131
  _FILERESPONSE._serialized_end=182
  _DATA._serialized_start=184
  _DATA._serialized_end=204
  _UNREADS._serialized_start=206
  _UNREADS._serialized_end=251
  _PAYLOAD._serialized_start=253
  _PAYLOAD._serialized_end=275
  _SENDREQUEST._serialized_start=277
  _SENDREQUEST._serialized_end=389
  _TEXTEDITOR._serialized_start=392
  _TEXTEDITOR._serialized_end=890
# @@protoc_insertion_point(module_scope)
