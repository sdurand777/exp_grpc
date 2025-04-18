// GENERATED CODE -- DO NOT EDIT!

'use strict';
var grpc = require('grpc');
var google_protobuf_empty_pb = require('google-protobuf/google/protobuf/empty_pb.js');
var pointcloud_pb = require('./pointcloud_pb.js');

function serialize_IVM_slam_PointCloud(arg) {
  if (!(arg instanceof pointcloud_pb.PointCloud)) {
    throw new Error('Expected argument of type IVM.slam.PointCloud');
  }
  return Buffer.from(arg.serializeBinary());
}

function deserialize_IVM_slam_PointCloud(buffer_arg) {
  return pointcloud_pb.PointCloud.deserializeBinary(new Uint8Array(buffer_arg));
}

function serialize_google_protobuf_Empty(arg) {
  if (!(arg instanceof google_protobuf_empty_pb.Empty)) {
    throw new Error('Expected argument of type google.protobuf.Empty');
  }
  return Buffer.from(arg.serializeBinary());
}

function deserialize_google_protobuf_Empty(buffer_arg) {
  return google_protobuf_empty_pb.Empty.deserializeBinary(new Uint8Array(buffer_arg));
}


// deux services
var SlamServiceService = exports.SlamServiceService = {
  // service pour recuperer les points du serveur
getPointCloud: {
    path: '/IVM.slam.SlamService/GetPointCloud',
    requestStream: false,
    responseStream: true,
    requestType: google_protobuf_empty_pb.Empty,
    responseType: pointcloud_pb.PointCloud,
    requestSerialize: serialize_google_protobuf_Empty,
    requestDeserialize: deserialize_google_protobuf_Empty,
    responseSerialize: serialize_IVM_slam_PointCloud,
    responseDeserialize: deserialize_IVM_slam_PointCloud,
  },
  // Utilisation correcte
// service pour envoyer les points au serveur
connectPointCloud: {
    path: '/IVM.slam.SlamService/ConnectPointCloud',
    requestStream: true,
    responseStream: false,
    requestType: pointcloud_pb.PointCloud,
    responseType: google_protobuf_empty_pb.Empty,
    requestSerialize: serialize_IVM_slam_PointCloud,
    requestDeserialize: deserialize_IVM_slam_PointCloud,
    responseSerialize: serialize_google_protobuf_Empty,
    responseDeserialize: deserialize_google_protobuf_Empty,
  },
  // Utilisation correcte
};

exports.SlamServiceClient = grpc.makeGenericClientConstructor(SlamServiceService);
