import os
import sys
import grpc
from concurrent import futures
from google.protobuf.empty_pb2 import Empty

current_dir = os.path.dirname(os.path.abspath(__file__))
gen_python_path = os.path.join(current_dir, '..', 'proto_files')
sys.path.append(gen_python_path)

import grpc
import slam_service_pb2_grpc
import google.protobuf.empty_pb2

def run():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = slam_service_pb2_grpc.SlamServiceStub(channel)
        response_iterator = stub.GetPointCloud(google.protobuf.empty_pb2.Empty())
        print("Réception des points depuis le serveur...")
        for point_cloud in response_iterator:
            print(f"Reçu un PointCloud avec {len(point_cloud.points)} points.")
            for point in point_cloud.points:
                print(f"Point(x={point.x}, y={point.y}, z={point.z})")

if __name__ == '__main__':
    run()
