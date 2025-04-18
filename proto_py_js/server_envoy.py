
import grpc
from concurrent import futures
import time
import pointcloud_pb2
import pointcloud_pb2_grpc
import slam_service_pb2
import slam_service_pb2_grpc
import subprocess

# Lancer Envoy en arrière-plan avec subprocess
def start_envoy():
    envoy_command = [
        'envoy', 
        '--config-path', 'envoy.yaml'  # Spécifiez le chemin vers votre fichier de configuration envoy.yaml
    ]
    # Lancer Envoy en tant que processus séparé
    subprocess.Popen(envoy_command)
    print("Envoy proxy lancé")

class SlamServiceServicer(slam_service_pb2_grpc.SlamServiceServicer):
    def GetPointCloud(self, request, context):
        # Envoi de points de manière continue
        for i in range(10):  # Par exemple, envoyons 10 points
            point = pointcloud_pb2.Point(x=i, y=i*2, z=i*3)
            point_cloud = pointcloud_pb2.PointCloud(points=[point])
            yield point_cloud  # Envoi d'un PointCloud à chaque itération

            time.sleep(1)

    def ConnectPointCloud(self, request_iterator, context):
        # Traitement de la réception des points (si nécessaire)
        for point_cloud in request_iterator:
            print(f"Reçu {len(point_cloud.points)} points")
        return pointcloud_pb2.Empty()

def serve():
    # Lancer Envoy en parallèle avant de démarrer le serveur gRPC
    start_envoy()
    
    # Lancer le serveur gRPC
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    slam_service_pb2_grpc.add_SlamServiceServicer_to_server(SlamServiceServicer(), server)
    server.add_insecure_port('[::]:50051')
    print("Serveur gRPC en écoute sur le port 50051")
    server.start()

    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    serve()
