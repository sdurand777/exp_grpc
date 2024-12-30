
import os
import sys
import grpc
import threading
import time
import open3d as o3d

import open3d.visualization.gui as gui
import open3d.visualization.rendering as rendering
import numpy as np
from google.protobuf.empty_pb2 import Empty

# Initialiser Open3D Application
app = o3d.visualization.gui.Application.instance
app.initialize()
font = gui.FontDescription("serif", point_size=18)
app.set_font(gui.Application.DEFAULT_FONT_ID, font)

window = gui.Application.instance.create_window("IVM SLAM", 1200, 800)
scene = gui.SceneWidget()
scene.scene = rendering.Open3DScene(window.renderer)
scene.scene.set_background([0.7, 0.7, 0.7, 1.0])

# Ajouter un widget à la fenêtre
window.add_child(scene)

# Ajouter l'objet PointCloud à la scène
points_array = np.random.rand(300, 3) * 10 - 5  # 300 points centrés autour de 0
pcd = o3d.geometry.PointCloud()  # Objet PointCloud d'Open3D
pcd.points = o3d.utility.Vector3dVector(points_array)

mat = rendering.MaterialRecord()
mat.shader = "defaultLit"  # Utiliser un shader par défaut

scene.scene.add_geometry("PointCloud", pcd, mat)

# Configurer la caméra pour visualiser les points
bounds = pcd.get_axis_aligned_bounding_box()
scene.scene.show_axes(True)
scene.scene.camera.look_at(bounds.get_center(), bounds.get_center() + [0, 0, -10], [0, -1, 0])

# Exécuter l'application Open3D
app.run()
