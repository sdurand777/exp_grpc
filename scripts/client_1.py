import os
import sys
import grpc
from concurrent import futures
from google.protobuf.empty_pb2 import Empty

current_dir = os.path.dirname(os.path.abspath(__file__))
gen_python_path = os.path.join(current_dir, '..', 'proto_files')
sys.path.append(gen_python_path)

import grpc
import pointcloud_pb2
import slam_service_pb2_grpc

def generate_point_clouds():
    for i in range(3):  # Envoyer 3 nuages de points
        point_cloud = pointcloud_pb2.PointCloud(
            points=[
                pointcloud_pb2.Point(x=i, y=i * 2, z=i * 3),
                pointcloud_pb2.Point(x=i + 1, y=i * 2 + 1, z=i * 3 + 1),
            ]
        )
        print(f"Envoi d'un PointCloud avec {len(point_cloud.points)} points.")
        yield point_cloud  # Générer les nuages de points un par un

def run():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = slam_service_pb2_grpc.SlamServiceStub(channel)
        response = stub.ConnectPointCloud(generate_point_clouds())
        print("Stream terminé, réponse du serveur :", response)

if __name__ == '__main__':
    run()
