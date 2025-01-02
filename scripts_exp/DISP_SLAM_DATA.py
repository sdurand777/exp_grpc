
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
gen_python_path = os.path.join(current_dir, '..', 'proto_files_exp')
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

    # Appel méthode pour recevoir les slam data
    response_iterator = stub.GetSlamData(google.protobuf.empty_pb2.Empty())

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

    # liste globale de toutes les donnees
    COORDS_LIST = {}
    POSES_LIST = {}
    COLORS_LIST = {}
    LOCAL_INDEX_LIST = [] # liste local pour update visualisateur
    GLOBAL_INDEX_LIST = [] # liste avec toutes les KFs globale


    def receiver_thread():
        global POINTS, COLORS, POSES, COORDS_LIST, POSES_LIST, LOCAL_INDEX_LIST, COLORS_LIST, GLOBAL_INDEX_LIST
        
        for slam_data in response_iterator:

            pointcloudlist = slam_data.pointcloudlist
            poselist = slam_data.poselist
            indexlist = slam_data.indexlist

            print(f"Reçu pointcloudlist avec {len(pointcloudlist.pointclouds)} pointclouds.")
            print(f"Reçu poselist avec {len(poselist.poses)} poses.")
            print(f"Reçu indexlist avec {len(indexlist.index)} indices.")

            # liste globale
            coords_list = []
            colors_list = []
            poses_list = []

            # recuperer les donnees PCD
            for pointcloud in pointcloudlist.pointclouds:

                point_cloud_data = []
                point_cloud_color = []

                for point in pointcloud.points:
                    # Ajouter chaque point et sa couleur dans les listes
                    point_cloud_data.append([point.x, point.y, point.z])
                    point_cloud_color.append([point.r, point.g, point.b])

                # Convertir la liste de points et couleurs en tableaux numpy
                if point_cloud_data:
                    new_points = np.array(point_cloud_data)
                    new_colors = np.array(point_cloud_color)
                    
                    coords_list.append(new_points)
                    colors_list.append(new_colors)

            # get indices
            index_list = list(indexlist.index)

            # recuperer les poses
            for pose in poselist.poses:
                # Récupérer la pose et l'ajouter à la liste POSES
                pose_matrix = np.array(pose.matrix).reshape(4, 4)
                poses_list.append(pose_matrix)

            # loop over indices

            print("index_list : \n", list(indexlist.index))
            print("len(coords_list) : ", len(coords_list))


            for i, index in enumerate(index_list):
                COORDS_LIST[index] = coords_list[i]
                COLORS_LIST[index] = colors_list[i]
                POSES_LIST[index] = poses_list[i]

            LOCAL_INDEX_LIST = index_list # sera delete apres animation pour eviter reset abusif
            
            # Fusion en ajoutant uniquement les nouveaux indices de list2 à list1
            GLOBAL_INDEX_LIST = GLOBAL_INDEX_LIST + [x for x in LOCAL_INDEX_LIST if x not in GLOBAL_INDEX_LIST]

            # Afficher les donnes recues
            print("-------- Afficher les SLAM DATA ------------")
            print("COORDS_LIST : \n", COORDS_LIST)
            print("COLORS_LIST : \n", COLORS_LIST)
            print("POSES_LIST : \n", POSES_LIST)
            print("LOCAL_INDEX_LIST : \n", LOCAL_INDEX_LIST)
            print("GLOBAL_INDEX_LIST : \n", GLOBAL_INDEX_LIST)
            # print("COORDS_LIST : \n", len(COORDS_LIST))
            # print("COLORS_LIST : \n", len(COLORS_LIST))
            # print("POSES_LIST : \n", len(POSES_LIST))


    def animation_callback():
        # variable global pour afficher
        global GLOBAL_INDEX_LIST, LOCAL_INDEX_LIST, COORDS_LIST, COLORS_LIST, POSES_LIST

        # on check si on des indices a update en stock

        if LOCAL_INDEX_LIST:
            
            # on loop sur les indexes
            for ix in LOCAL_INDEX_LIST:
                
                # on delete une KF deja traite
                if ix in GLOBAL_INDEX_LIST:
                    scene.scene.remove_geometry("PointCloud "+ str(ix))

                # on update la geometry
                pcd = o3d.geometry.PointCloud()
                pcd.points = o3d.utility.Vector3dVector(COORDS_LIST[ix])
                pcd.colors = o3d.utility.Vector3dVector(COLORS_LIST[ix])

                scene.scene.add_geometry("PointCloud " + str(ix), pcd, mat)

            # on delete les indices une fois update fait
            LOCAL_INDEX_LIST = []

            # bounds = scene.scene.bounding_box
            # scene.setup_camera(60, bounds, bounds.get_center())
            # scene.scene.show_axes(True)

        print("--- end callback ---")

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











