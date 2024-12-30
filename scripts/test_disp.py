
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
    response_iterator = stub.GetPointCloud(google.protobuf.empty_pb2.Empty())

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
    INDICE_CLOUD+=1

    POINTS = np.array([])
    
    def receiver_thread():
        global POINTS
        
        for point_cloud in response_iterator:
            print(f"Reçu PointCloud avec {len(point_cloud.points)} points.")
            point_cloud_data = []
            for point in point_cloud.points:
                # Ajouter chaque point dans la liste
                point_cloud_data.append([point.x, point.y, point.z])
            
            # Convertir la liste de points en un tableau numpy
            if point_cloud_data:
                POINTS= np.array(point_cloud_data)
                print("points_np : ", POINTS)
                print("points shape : \n", POINTS.shape)


    def animation_callback():
        global INDICE_CLOUD, POINTS
        print("animation callback")
        print("POINTS ANIMATION : \n", POINTS)
        if POINTS.any():
            pcd = o3d.geometry.PointCloud()

            pcd.points = o3d.utility.Vector3dVector(POINTS)

            scene.scene.add_geometry("PointCloud " + str(INDICE_CLOUD), pcd, mat)
            INDICE_CLOUD += 1
            POINTS = np.array([])

            bounds = scene.scene.bounding_box
            scene.setup_camera(60, bounds, bounds.get_center())
            scene.scene.show_axes(True)

        print("End callback ---")

#                 all_pcd.append(points_np)
#                 if points_np.shape[0] > 100:
#                     print("Show this shit")
#                     pcd.points = o3d.utility.Vector3dVector(points_np)
#                     print("points_np :\n", points_np)
# #                     points_array = np.random.rand(300, 3) * 10  # 300 points pour l'exemple
# #                     print("points_array shape : ", points_array.shape)
# # # Générer des couleurs aléatoires
# #                     colors_array = np.random.rand(300, 3)  # Une couleur pour chaque point
# #                     pcd = o3d.geometry.PointCloud()  # Objet PointCloud d'Open3D
# #                     pcd.points = o3d.utility.Vector3dVector(points_array)
# #                     pcd.colors = o3d.utility.Vector3dVector(colors_array)
#
#                     scene.scene.add_geometry("PointCloud " + str(INDICE_CLOUD), pcd, mat)
#                     INDICE_CLOUD += 1
#
# # Configurer la caméra pour visualiser les points
#                     bounds = scene.scene.bounding_box
#                     scene.setup_camera(60, bounds, bounds.get_center())
#                     scene.scene.show_axes(True)
#                     return


        #
        # print("---------- Affichage des points") 
        # 
        # all_concat = np.concatenate(all_pcd, axis=0)
        # print("all_concat shape : ", all_concat.shape)
        # bounds = pcd.get_axis_aligned_bounding_box()
        # scene.scene.camera.look_at(bounds.get_center(), bounds.get_center() + [0, 0, -1], [0, -1, 0])



        # thread pour update le pcd
    def update_thread():
        while True:
            print("update thread")
            # Poster une mise à jour dans le thread principal
            o3d.visualization.gui.Application.instance.post_to_main_thread(
                    window, animation_callback)

            time.sleep(1.0)

# Démarrer un thread pour recevoir et afficher les données
    thread_anim = threading.Thread(target=update_thread)

    thread_grpc = threading.Thread(target=receiver_thread)

    thread_anim.start()
    thread_grpc.start()

# Exécuter l'application Open3D
    app.run()











