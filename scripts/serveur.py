import os
import sys
import grpc
from concurrent import futures
from google.protobuf.empty_pb2 import Empty

current_dir = os.path.dirname(os.path.abspath(__file__))
gen_python_path = os.path.join(current_dir, '..', 'proto_files')
sys.path.append(gen_python_path)

import slam_service_pb2
import slam_service_pb2_grpc
import pointcloud_pb2
import time

class SlamServiceServicer(slam_service_pb2_grpc.SlamServiceServicer):
    def __init__(self):
        self.point_clouds = []  # Stocker les points reçus

    def ConnectPointCloud(self, request_iterator, context):
        print("Réception des points du client 1...")
        for point_cloud in request_iterator:
            print(f"Reçu un PointCloud avec {len(point_cloud.points)} points.")
            self.point_clouds.append(point_cloud)  # Ajouter les points reçus
        return Empty()  # Réponse vide pour confirmer

    def GetPointCloud(self, request, context):
        print("Envoi des points au client 2...")
        for point_cloud in self.point_clouds:
            yield point_cloud  # Envoyer les nuages de points stockés un par un

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    slam_service_pb2_grpc.add_SlamServiceServicer_to_server(SlamServiceServicer(), server)
    server.add_insecure_port('[::]:50051')
    print("Le serveur est en cours d'exécution sur le port 50051...")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
