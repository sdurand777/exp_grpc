# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: slam_service.proto
# Protobuf Python Version: 5.27.2
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    5,
    27,
    2,
    '',
    'slam_service.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2
import pointcloud_pb2 as pointcloud__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x12slam_service.proto\x12\x08IVM.slam\x1a\x1bgoogle/protobuf/empty.proto\x1a\x10pointcloud.proto2\xb7\x03\n\x0bSlamService\x12?\n\rGetPointCloud\x12\x16.google.protobuf.Empty\x1a\x14.IVM.slam.PointCloud0\x01\x12\x43\n\x11\x43onnectPointCloud\x12\x14.IVM.slam.PointCloud\x1a\x16.google.protobuf.Empty(\x01\x12O\n\x15GetPointCloudWithPose\x12\x16.google.protobuf.Empty\x1a\x1c.IVM.slam.PointCloudWithPose0\x01\x12S\n\x19\x43onnectPointCloudWithPose\x12\x1c.IVM.slam.PointCloudWithPose\x1a\x16.google.protobuf.Empty(\x01\x12;\n\x0bGetSlamData\x12\x16.google.protobuf.Empty\x1a\x12.IVM.slam.SlamData0\x01\x12?\n\x0f\x43onnectSlamData\x12\x12.IVM.slam.SlamData\x1a\x16.google.protobuf.Empty(\x01\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'slam_service_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_SLAMSERVICE']._serialized_start=80
  _globals['_SLAMSERVICE']._serialized_end=519
# @@protoc_insertion_point(module_scope)
