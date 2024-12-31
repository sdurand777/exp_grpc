
import os
import sys
import grpc
import threading
import time
import open3d as o3d

import open3d.visualization.gui as gui
import open3d.visualization.rendering as rendering
import open3d.visualization as visualizer

import numpy as np
from google.protobuf.empty_pb2 import Empty

current_dir = os.path.dirname(os.path.abspath(__file__))
gen_python_path = os.path.join(current_dir, '..', 'proto_files')
sys.path.append(gen_python_path)

import slam_service_pb2_grpc
import google.protobuf.empty_pb2


# connexion grpc
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
    response_iterator = stub.GetPointCloudWithPose(google.protobuf.empty_pb2.Empty())

    INDICE_CLOUD = 0

# Initialiser Open3D Application
    app = o3d.visualization.gui.Application.instance
    app.initialize()
    font = gui.FontDescription("serif",point_size=18)
    app.set_font(gui.Application.DEFAULT_FONT_ID,font)

    window_init = gui.Application.instance.create_window("IVM SLAM", 1200, 800)
    window = window_init
    scene = gui.SceneWidget()
    scene.scene = rendering.Open3DScene(window.renderer)
    scene.scene.set_background_color(np.asarray([0.7,0.7,0.7,1]))

    window.add_child(scene)

    pcd = o3d.geometry.PointCloud()  # Objet PointCloud d'Open3D

    mat = rendering.MaterialRecord()
    mat.point_size = 12.0  # Taille des points en pixels

    scene.scene.add_geometry("PointCloud "+ str(INDICE_CLOUD), pcd, mat)
    #INDICE_CLOUD+=1

    POINTS = np.array([])
    COLORS = np.array([])
    POSES = []  # Utilisation d'une liste pour les poses (matrices 4x4)

    def receiver_thread():
        global POINTS, COLORS, POSES
        
        for point_cloud_with_pose in response_iterator:
            point_cloud_data = []  # Pour stocker temporairement les points
            point_cloud_color = []  # Pour stocker temporairement les couleurs

            point_cloud = point_cloud_with_pose.pointCloud
            pose = point_cloud_with_pose.pose
            print(f"Reçu PointCloud avec {len(point_cloud.points)} points.")
            print(f"Reçu Pose avec matrice : {pose.matrix}")

            # Récupérer les données du point cloud
            for point in point_cloud.points:
                # Ajouter chaque point et sa couleur dans les listes
                point_cloud_data.append([point.x, point.y, point.z])
                point_cloud_color.append([point.r, point.g, point.b])
            
            # Convertir la liste de points et couleurs en tableaux numpy
            if point_cloud_data:
                new_points = np.array(point_cloud_data)
                new_colors = np.array(point_cloud_color)
                
                if POINTS.size == 0:
                    POINTS = new_points
                else:
                    POINTS = np.append(POINTS, new_points, axis=0)

                if COLORS.size == 0:
                    COLORS = new_colors
                else:
                    COLORS = np.append(COLORS, new_colors, axis=0)

                print("points shape : \n", POINTS.shape)
                print("colors shape : \n", COLORS.shape)

            # Récupérer la pose et l'ajouter à la liste POSES
            pose_matrix = np.array(point_cloud_with_pose.pose.matrix).reshape(4, 4)
            POSES.append(pose_matrix)
            print("Pose reçue : \n", pose_matrix)

            # Facultatif : vérifier la taille de POSES
            print(f"Nombre de poses stockées : {len(POSES)}")


    def animation_callback():
        global INDICE_CLOUD, POINTS, COLORS, POSES
        print("animation callback")
        print("POINTS ANIMATION : \n", POINTS)
        if POINTS.any():
            pcd = o3d.geometry.PointCloud()

            pcd.points = o3d.utility.Vector3dVector(POINTS)
           
            # Assigner les couleurs au nuage de points
            pcd.colors = o3d.utility.Vector3dVector(COLORS)

            scene.scene.add_geometry("PointCloud " + str(INDICE_CLOUD), pcd, mat)
            INDICE_CLOUD += 1
            POINTS = np.array([])
            COLORS = np.array([])
            POSES = []

            bounds = scene.scene.bounding_box
            scene.setup_camera(60, bounds, bounds.get_center())
            scene.scene.show_axes(True)

        print("End callback ---")

        # thread pour update le pcd
    def update_thread():
        while True:
            print("update thread")
            # Poster une mise à jour dans le thread principal
            o3d.visualization.gui.Application.instance.post_to_main_thread(
                    window, animation_callback)

            time.sleep(0.1)

    # Démarrer un thread pour recevoir et afficher les données
    thread_anim = threading.Thread(target=update_thread)
    thread_grpc = threading.Thread(target=receiver_thread)

    thread_anim.start()
    thread_grpc.start()

    # Exécuter l'application Open3D
    app.run()











