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


# slam service rpc implementation des services RPC
class SlamServiceServicer(slam_service_pb2_grpc.SlamServiceServicer):
    # constructor
    def __init__(self):
        self.point_clouds = []  # Stocker les points reçus

    # RPC ConnectPointCloud service pour recevoir le pcd du client 1
    def ConnectPointCloud(self, request_iterator, context):
        print("Réception des points du client 1...")
        for point_cloud in request_iterator:
            print(f"Reçu un PointCloud avec {len(point_cloud.points)} points.")
            self.point_clouds.append(point_cloud)  # Ajouter les points reçus
            #print("point_clouds stored : ", self.point_clouds)
        print("--------- fin de reception --------")
        return Empty()  # Réponse vide pour confirmer

    # # RPC GetPointCloud pour envoyer le pcd au client 2
    # def GetPointCloud(self, request, context):
    #     print("Envoi des points au client 2...")
    #     for point_cloud in self.point_clouds:
    #         yield point_cloud  # Envoyer les nuages de points stockés un par un

    # RPC GetPointCloud pour envoyer le pcd au client 2
    def GetPointCloud(self, request, context):
        print("Envoi des points au client 2...")
        try:
            while True:  # Boucle infinie pour envoyer les points en continu
                # Envoyer les points déjà reçus
                if self.point_clouds:
                    # for point_cloud in self.point_clouds:
                    #     # Limiter les points envoyés à 10
                    #     limited_points = pointcloud_pb2.PointCloud(
                    #         points=point_cloud.points[:10]  # Envoyer uniquement les 10 premiers points
                    #     )
                    #     yield limited_points
                    for point_cloud in self.point_clouds:
                        print(f"Envoie un PointCloud avec {len(point_cloud.points)} points.")
                        yield point_cloud  # Envoi des points stockés

                    print("clean pointcloud deja envoye")
                    # on supprime
                    self.point_clouds = []
                    # Vous pouvez aussi ajouter un petit délai entre les envois pour éviter de trop solliciter le réseau
                    time.sleep(0.1)  # Un délai de 1 seconde avant de renvoyer les points
                else:
                    # Attendre un peu avant de vérifier s'il y a de nouveaux points si aucun n'est encore reçu
                    print("wait for new points")
                    time.sleep(0.1)
        except grpc.RpcError as e:
            print(f"Erreur RPC : {e.code()}, message : {e.details()}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details("Erreur lors de l'envoi des points.")




# definition du serveur
def serve():
    # creation instance grpc serveur pool de 10 threads avec chaque thread qui peut gerer une requete RPC distincte
    #server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10),
        options=[
            ('grpc.max_receive_message_length', 50 * 1024 * 1024),  # 50 Mo
            ('grpc.max_send_message_length', 50 * 1024 * 1024),     # 50 Mo
        ]
    )

    # ajoute implementation SlamService au serveur definie ci dessus
    slam_service_pb2_grpc.add_SlamServiceServicer_to_server(SlamServiceServicer(), server)
    # ajoute port de connexion au serveur
    server.add_insecure_port('[::]:50051')
    print("Le serveur est en cours d'exécution sur le port 50051...")
    # lance le serveur
    server.start()
    # attend une commande pour stopper le serveur
    server.wait_for_termination()

# lancement app
if __name__ == '__main__':
    serve()
