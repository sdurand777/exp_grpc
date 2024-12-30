
import os
import sys
import grpc
import open3d as o3d  # Importation de Open3D
import numpy as np
from concurrent import futures
from google.protobuf.empty_pb2 import Empty

current_dir = os.path.dirname(os.path.abspath(__file__))
gen_python_path = os.path.join(current_dir, '..', 'proto_files')
sys.path.append(gen_python_path)

import slam_service_pb2_grpc
import google.protobuf.empty_pb2

# Fonction pour gérer la réception continue des points 3D
def run():
    # Connexion au serveur gRPC
    with grpc.insecure_channel(
        'localhost:50051',
        options=[
            ('grpc.max_receive_message_length', 50 * 1024 * 1024),  # 50 Mo
            ('grpc.max_send_message_length', 50 * 1024 * 1024),     # 50 Mo
        ]
    ) as channel:
        # Stub client definition pour accéder aux méthodes du serveur
        stub = slam_service_pb2_grpc.SlamServiceStub(channel)

        # Appel méthode GetPointCloud pour recevoir des points en continu
        response_iterator = stub.GetPointCloud(google.protobuf.empty_pb2.Empty())

        print("Réception continue des points depuis le serveur...")
        
        # Créer un objet PointCloud d'Open3D pour afficher les points
        point_cloud_data = []
        pcd = o3d.geometry.PointCloud()
        
        # Affichage initial vide
        vis = o3d.visualization.Visualizer()
        vis.create_window()
        
        for point_cloud in response_iterator:
            print(f"Reçu un PointCloud avec {len(point_cloud.points)} points.")
            for point in point_cloud.points:
                # Ajouter chaque point dans la liste
                point_cloud_data.append([point.x, point.y, point.z])
            
            # Convertir la liste de points en un tableau numpy
            if point_cloud_data:
                points_np = np.array(point_cloud_data)
                pcd.points = o3d.utility.Vector3dVector(points_np)

                # Effacer les points précédents et ajouter les nouveaux
                vis.clear_geometries()
                vis.add_geometry(pcd)
                
                # Mettre à jour la fenêtre de visualisation
                vis.update_geometry(pcd)
                vis.poll_events()
                vis.update_renderer()

        vis.run()  # Exécuter la visualisation

if __name__ == '__main__':
    run()
