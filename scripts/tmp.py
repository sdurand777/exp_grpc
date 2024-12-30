
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


# Variables globales pour la gestion de l'application
is_done = False  # Pour arrêter proprement le thread
pcd = o3d.geometry.PointCloud()  # Objet PointCloud d'Open3D
mat = rendering.MaterialRecord()

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

# indice pcd
ix = 0

def animation_callback():
    global ix, pcd, mat
    print("animation callback cloud : ", ix)
    scene.scene.add_geometry("Cloud "+str(ix), pcd, mat)
    ix = ix+1

def update_thread(stub, window):
    """Thread pour recevoir les points et les afficher."""
    global is_done, pcd, mat, ix

    response_iterator = stub.GetPointCloud(google.protobuf.empty_pb2.Empty())
    point_cloud_data = []  # Stocke temporairement les points

    print("Réception des points depuis le serveur...")
    for point_cloud in response_iterator:
        if is_done:
            break

        print(f"Reçu un PointCloud avec {len(point_cloud.points)} points.")
        for point in point_cloud.points:
            point_cloud_data.append([point.x, point.y, point.z])

        if point_cloud_data:
            # Convertir en tableau numpy
            points_np = np.array(point_cloud_data)
            pcd.points = o3d.utility.Vector3dVector(points_np)

            # Poster une mise à jour dans le thread principal
            o3d.visualization.gui.Application.instance.post_to_main_thread(
                window, animation_callback)

        time.sleep(1)  # Attendre un peu avant la prochaine mise à jour


def run():
    """Fonction principale."""
    global is_done, pcd, window, scene, app

    # Connexion au serveur gRPC
    with grpc.insecure_channel(
        'localhost:50051',
        options=[
            ('grpc.max_receive_message_length', 50 * 1024 * 1024),
            ('grpc.max_send_message_length', 50 * 1024 * 1024),
        ]
    ) as channel:
        stub = slam_service_pb2_grpc.SlamServiceStub(channel)

        # Ajouter l'objet PointCloud à la scène

        points_array = np.random.rand(100, 3) * 10  # 300 points pour l'exemple
        pcd.points = o3d.utility.Vector3dVector(points_array)

        scene.scene.add_geometry("PointCloud", pcd, mat)

        # Démarrer un thread pour recevoir et afficher les données
        thread = threading.Thread(target=update_thread, args=(stub, window), daemon=True)
        thread.start()

        # Exécuter l'application Open3D
        app.run()

        # Arrêter le thread à la fermeture
        is_done = True
        thread.join()


if __name__ == '__main__':
    run()
