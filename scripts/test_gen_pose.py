
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


def generate_point_clouds_with_poses():
    global INDICE

    for i in range(12):  # Envoyer 12 nuages de points avec leurs poses associées

        # Générer les points du nuage
        points_array = np.zeros((NUM_POINTS, 3))  # 10 points pour l'exemple
        points_array[:, 0] = INDICE
        points_array[:, 1] = np.arange(0, NUM_POINTS)
        INDICE += 1

        # Générer une matrice de pose 4x4
        pose_matrix = np.eye(4)  # Matrice identité pour l'exemple
        pose_matrix[:3, 3] = [INDICE, 0, 0]  # Déplacer la caméra selon X

        # Construire le message `Pose`
        pose = pointcloud_pb2.Pose(matrix=pose_matrix.flatten().tolist())

        # Construire le message `PointCloud`
        points = [pointcloud_pb2.Point(x=row[0], y=row[1], z=row[2], r=np.random.rand(), g=np.random.rand(), b=np.random.rand()) for row in points_array]
        point_cloud = pointcloud_pb2.PointCloud(points=points)

        # Construire le message `PointCloudWithPose`
        point_cloud_with_pose = pointcloud_pb2.PointCloudWithPose(pointCloud=point_cloud, pose=pose)

        print("Envoie point cloud avec pose")
        yield point_cloud_with_pose  # Envoyer le message combiné

        # Attente pour simuler une génération de données
        print("Waiting ...")
        time.sleep(3)


def run_client():
    # Connexion au serveur
    channel = grpc.insecure_channel('localhost:50051')
    stub = slam_service_pb2_grpc.SlamServiceStub(channel)

    # Stream des nuages de points et poses au serveur
    try:
        response = stub.ConnectPointCloudWithPose(generate_point_clouds_with_poses())
        print("Réponse du serveur : ", response)
    except grpc.RpcError as e:
        print(f"Erreur RPC : {e.code()}, message : {e.details()}")


if __name__ == '__main__':
    run_client()
