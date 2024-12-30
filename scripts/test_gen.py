import os
import sys
import grpc
import time
from concurrent import futures
from google.protobuf.empty_pb2 import Empty

current_dir = os.path.dirname(os.path.abspath(__file__))
gen_python_path = os.path.join(current_dir, '..', 'proto_files')
sys.path.append(gen_python_path)

import grpc
import pointcloud_pb2
import slam_service_pb2_grpc

import numpy as np


NUM_POINTS = 10

INDICE = 0

# generation du pcd
def generate_point_clouds():
    global INDICE
    for i in range(3):  # Envoyer 3 nuages de points

        # gen point cloud
        points_array = np.zeros((NUM_POINTS, 3))  # 300 points pour l'exemple
            
        points_array[:,0] = INDICE
        INDICE += 1

        # Créer un PointCloud avec tous les points à envoyer d'un coup
        points = [pointcloud_pb2.Point(x=row[0], y=row[1], z=row[2]) for row in points_array]
        
        # Créer le message PointCloud avec tous les points
        point_cloud = pointcloud_pb2.PointCloud(points=points)

        print("Envoie point cloud")

        yield point_cloud  # Générer le PointCloud pour chaque point

        #     points = []
        #     for j in range(NUM_POINTS):  # Générer 100 points par nuage
        #         points.append(pointcloud_pb2.Point(x=i + j, y=(i + j) * 2, z=(i + j) * 3))
        # 
        # point_cloud = pointcloud_pb2.PointCloud(points=points)
        # print(f"Envoi d'un PointCloud avec {len(point_cloud.points)} points.")
        # yield point_cloud  # Générer les nuages de points un par un

        # attente simule attente slam
        print("Waiting ... ")
        time.sleep(5)

# definition du client pour envouyer les points
def run():
    # chennel pour se connecter au serveur
    #with grpc.insecure_channel('localhost:50051') as channel:
    with grpc.insecure_channel(
        'localhost:50051',
        options=[
            ('grpc.max_receive_message_length', 50 * 1024 * 1024),  # 50 Mo
            ('grpc.max_send_message_length', 50 * 1024 * 1024),     # 50 Mo
        ]
    ) as channel:
        # stub client definition
        stub = slam_service_pb2_grpc.SlamServiceStub(channel)
        # appelle la methode ConnectPointCloud du fichier proto methode client streaming

        start_time = time.time()
        response = stub.ConnectPointCloud(generate_point_clouds())
        end_time = time.time()

        print("Stream terminé, réponse du serveur :", response)

        # Calculer le temps et le débit
        elapsed_time = end_time - start_time
        data_size = 3 * NUM_POINTS * 24  # 3 nuages x 100 points x 24 octets par point
        throughput_mbps = (data_size / elapsed_time) * 8 / 10**6

        print(f"Temps total : {elapsed_time:.2f} secondes")
        print(f"Débit : {throughput_mbps:.2f} Mbps")

if __name__ == '__main__':
    run()
