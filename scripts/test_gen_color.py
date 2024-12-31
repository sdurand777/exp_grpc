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
    for i in range(12):  # Envoyer 3 nuages de points

        # gen point cloud
        points_array = np.zeros((NUM_POINTS, 3))  # 300 points pour l'exemple
            
        points_array[:,0] = INDICE
        points_array[:,1] = np.arange(0,NUM_POINTS)
        INDICE += 1

        # Créer un PointCloud avec tous les points à envoyer d'un coup
        points = [pointcloud_pb2.Point(x=row[0], y=row[1], z=row[2], r=1.0, g=0.0, b=0.0) for row in points_array]
        
        # Créer le message PointCloud avec tous les points
        point_cloud = pointcloud_pb2.PointCloud(points=points)

        print("Envoie point cloud")

        yield point_cloud  # Générer le PointCloud pour chaque point

        # attente simule attente slam
        print("Waiting ... ")
        time.sleep(1)

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

        response = stub.ConnectPointCloud(generate_point_clouds())

        print("Stream terminé, réponse du serveur :", response)

if __name__ == '__main__':
    run()