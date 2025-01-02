
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

import cv2

# construction cameras
CAM_POINTS = np.array([
        [ 0,   0,   0],
        [-1,  -1, 1.5],
        [ 1,  -1, 1.5],
        [ 1,   1, 1.5],
        [-1,   1, 1.5],
        [-0.5, 1, 1.5],
        [ 0.5, 1, 1.5],
        [ 0, 1.2, 1.5]])

CAM_LINES = np.array([
    [1,2], [2,3], [3,4], [4,1], [1,0], [0,2], [3,0], [0,4], [5,7], [7,6]])

### add or update camera actor ###
TRANSFO_CAM = np.array([  [1,0,0,0],
                        [0,-1,0,0],
                        [0,0,-1,0],
                        [0,0,0,1]
                        ])

AUTOTRACK = False

POINTS = np.array([])
COLORS = np.array([])
POSES = []  # Utilisation d'une liste pour les poses (matrices 4x4)

# liste globale de toutes les donnees
COORDS_LIST = {}
POSES_LIST = {}
COLORS_LIST = {}
LOCAL_INDEX_LIST = [] # liste local pour update visualisateur
GLOBAL_INDEX_LIST = [] # liste avec toutes les KFs globale
CAMERA_ACTOR_LIST = {} # dict avec les camera actors


SHOW_CAMERA = True



def create_camera_actor(scale=0.05):
    """ build open3d camera polydata """
    camera_actor = o3d.geometry.LineSet(
        points=o3d.utility.Vector3dVector(scale * CAM_POINTS),
        lines=o3d.utility.Vector2iVector(CAM_LINES))

    #color = (g * 1.0, 0.5 * (1-g), 0.9 * (1-g))
    color = (25/255, 79/255, 140/255)
    if scale > 0.05:
        color = (1.0, 167/255, 0)

    camera_actor.paint_uniform_color(color)
    return camera_actor



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

    # gris souris
    #scene.scene.set_background_color(np.asarray([0.7,0.7,0.7,1]))

    # afficher background clean
    background = cv2.imread("./IVM.jpg")
    seuil = 128
    _, background = cv2.threshold(background, seuil, 255, cv2.THRESH_BINARY)
    pixels_blancs = (background[:, :, 0] == 255) & (background[:, :, 1] == 255) & (background[:, :, 2] == 255)
    background[pixels_blancs] = [100,100,100]
    pixels_noirs = (background[:, :, 0] == 0) & (background[:, :, 1] == 0) & (background[:, :, 2] == 0)
    background[pixels_noirs] = [50,50,50]
    background_o3d = o3d.geometry.Image(background)
    scene.scene.set_background(np.asarray([0.39,0.39,0.39,1]), background_o3d )



# GUI panel
    em = window.theme.font_size

# settings panel
    panel_size = 0.0
    settings_panel = gui.Vert(
        0, gui.Margins(panel_size * em, panel_size * em, panel_size * em, panel_size * em))




    # Background options
    # menu pour les differents fonds
    background_settings = gui.CollapsableVert("Panel settings", 0,
                                                    gui.Margins(em, 0, 0, 0))
    background_settings.set_is_open(False)
    
    background_spacing = 0.5


    # ---------------------------------------
    #           CHANGE BACKGROUND
    # ---------------------------------------
    back_layout = gui.Horiz(background_spacing*em, gui.Margins(background_spacing*em, background_spacing*em,background_spacing*em,background_spacing*em))
        
    def change_img():
        background = cv2.imread("./IVM.jpg")
        seuil = 128
        _, background = cv2.threshold(background, seuil, 255, cv2.THRESH_BINARY)
        pixels_blancs = (background[:, :, 0] == 255) & (background[:, :, 1] == 255) & (background[:, :, 2] == 255)
        background[pixels_blancs] = [50,50,50]
        background_o3d = o3d.geometry.Image(background)
        scene.scene.set_background_color(np.asarray([0.2,0.2,0.2,1]))
        scene.scene.set_background(np.asarray([0.2,0.2,0.2,1]), background_o3d )
        bouton_change.background_color = gui.Color(r=1.0, g =167/255, b=0.0)
        bouton_change_2.background_color = gui.Color(r=25/255, g=79/255, b=140/255)
        bouton_change_3.background_color = gui.Color(r=25/255, g=79/255, b=140/255)
 
 
    def change_img_2():
        background = cv2.imread("./IVM.jpg")
        seuil = 128
        _, background = cv2.threshold(background, seuil, 255, cv2.THRESH_BINARY)
        pixels_blancs = (background[:, :, 0] == 255) & (background[:, :, 1] == 255) & (background[:, :, 2] == 255)
        background[pixels_blancs] = [150,150,150]
        pixels_noirs = (background[:, :, 0] == 0) & (background[:, :, 1] == 0) & (background[:, :, 2] == 0)
        background[pixels_noirs] = [100,100,100]
        background_o3d = o3d.geometry.Image(background)
        scene.scene.set_background_color(np.asarray([0.6,0.6,0.6,1]))
        scene.scene.set_background(np.asarray([0.6,0.6,0.6,1]), background_o3d )
        bouton_change_2.background_color = gui.Color(r=1.0, g =167/255, b=0.0)
        bouton_change.background_color = gui.Color(r=25/255, g=79/255, b=140/255)
        bouton_change_3.background_color = gui.Color(r=25/255, g=79/255, b=140/255)

    def change_img_3():
        background = cv2.imread("./IVM.jpg")
        seuil = 128
        _, background = cv2.threshold(background, seuil, 255, cv2.THRESH_BINARY)
        pixels_blancs = (background[:, :, 0] == 255) & (background[:, :, 1] == 255) & (background[:, :, 2] == 255)
        background[pixels_blancs] = [100,100,100]
        pixels_noirs = (background[:, :, 0] == 0) & (background[:, :, 1] == 0) & (background[:, :, 2] == 0)
        background[pixels_noirs] = [50,50,50]
        background_o3d = o3d.geometry.Image(background)
        scene.scene.set_background_color(np.asarray([0.39,0.39,0.39,1]))
        scene.scene.set_background(np.asarray([0.39,0.39,0.39,1]), background_o3d )
        bouton_change_3.background_color = gui.Color(r=1.0, g =167/255, b=0.0)
        bouton_change.background_color = gui.Color(r=25/255, g=79/255, b=140/255)
        bouton_change_2.background_color = gui.Color(r=25/255, g=79/255, b=140/255)

    background_label = gui.Label("Background")

    #back_layout.add_stretch()

    bouton_change = gui.Button("Darker")
    bouton_change.background_color = gui.Color(r=25/255, g=79/255, b=140/255)
    bouton_change.set_on_clicked(change_img)
    back_layout.add_child(bouton_change)

    bouton_change_3 = gui.Button("Default")
    bouton_change_3.background_color = gui.Color(r=1.0, g =167/255, b=0.0)
    bouton_change_3.set_on_clicked(change_img_3)
    back_layout.add_child(bouton_change_3)

    bouton_change_2 = gui.Button("Brighter")
    bouton_change_2.background_color = gui.Color(r=25/255, g=79/255, b=140/255)
    bouton_change_2.set_on_clicked(change_img_2)
    back_layout.add_child(bouton_change_2)

    background_settings.add_child(background_label)
    background_settings.add_child(back_layout)

    # Vizualisation Options
    material_spacing = 0.5

    # ---------------------------------------
    #           CHANGE CLOUD VIEW
    # ---------------------------------------
    layout_cloud = gui.Vert()
    layout_cloud_label = gui.Label("View")
    cloud_spacing = 0.5
    layout_cloud_button = gui.Horiz(cloud_spacing*em, gui.Margins(material_spacing*em, material_spacing*em,material_spacing*em,material_spacing*em))

    layout_cloud.add_child(layout_cloud_label)
    layout_cloud.add_child(layout_cloud_button)

    def reset_view():
        if len(COORDS_LIST) > 0:
                # scene.reset_view_point(True)
                # scene.get_view_control().rotate(0.0,-900.0)
                bounds = scene.scene.bounding_box
                scene.setup_camera(60, bounds, bounds.get_center())
                #scene.look_at(bounds.get_center(), bounds.get_center() - [0,2,0], [0,-1,0])
        reset_camera.background_color = gui.Color(r=1.0, g =167/255, b=0.0)
        autotrack_camera.background_color = gui.Color(r=25/255, g=79/255, b=140/255)

    def autotrack_view():
        global AUTOTRACK
        if len(COORDS_LIST) > 0:
            if AUTOTRACK == False:
                AUTOTRACK = True 
                autotrack_camera.background_color = gui.Color(r=1.0, g =167/255, b=0.0)
                reset_camera.background_color = gui.Color(r=25/255, g=79/255, b=140/255)
            else:
                AUTOTRACK = False 
                autotrack_camera.background_color = gui.Color(r=25/255, g=79/255, b=140/255)
                reset_camera.background_color = gui.Color(r=25/255, g=79/255, b=140/255)

    def hide_cameras():
        global SHOW_CAMERA
        SHOW_CAMERA = False
        # on parcours les indices des KFs pour hides les cameras
        for ix, camera_actor in CAMERA_ACTOR_LIST.items():
            scene.scene.remove_geometry("Camera " + str(ix))
        bounds = scene.scene.bounding_box
        scene.setup_camera(60, bounds, bounds.get_center())
        #scene.get_view_control().rotate(0.0,-900.0)
        hide_camera.background_color = gui.Color(r=1.0, g =167/255, b=0.0)
        show_camera.background_color = gui.Color(r=25/255, g=79/255, b=140/255)


    def show_cameras():
        global SHOW_CAMERA
        SHOW_CAMERA = True
        for ix, camera_actor in CAMERA_ACTOR_LIST.items():
            scene.scene.add_geometry("Camera " + str(ix),camera_actor, mat)
#                scene.get_view_control().rotate(0.0,-900.0)
        bounds = scene.scene.bounding_box
        scene.setup_camera(60, bounds, bounds.get_center())
        show_camera.background_color = gui.Color(r=1.0, g =167/255, b=0.0)
        hide_camera.background_color = gui.Color(r=25/255, g=79/255, b=140/255)


    reset_camera = gui.Button("Reset")
    reset_camera.background_color = gui.Color(r=25/255, g=79/255, b=140/255)
    reset_camera.set_on_clicked(reset_view)

    autotrack_camera = gui.Button("Autotrack")
    autotrack_camera.background_color = gui.Color(r=25/255, g=79/255, b=140/255)
    autotrack_camera.set_on_clicked(autotrack_view)

    hide_camera = gui.Button("Hide Cams")
    hide_camera.background_color = gui.Color(r=25/255, g=79/255, b=140/255)
    hide_camera.set_on_clicked(hide_cameras)

    show_camera = gui.Button("Show Cams")
    show_camera.background_color = gui.Color(r=25/255, g=79/255, b=140/255)
    show_camera.set_on_clicked(show_cameras)

    layout_cloud_button.add_child(reset_camera)
    layout_cloud_button.add_child(autotrack_camera)
    layout_cloud_button.add_child(hide_camera)
    layout_cloud_button.add_child(show_camera)

    background_settings.add_child(layout_cloud)

    # ---------------------------------------
    #           CHANGE Point Size
    # ---------------------------------------
    # Layout pour la barre de reduction de la taille des points
    layout_point_size = gui.Horiz(0, gui.Margins(material_spacing*em, material_spacing*em,material_spacing*em,material_spacing*em))

    point_size_label = gui.Label("Point size")
    point_size = gui.Slider(gui.Slider.INT)
    point_size.set_limits(1, 5)

    # material object to update point size
    material = rendering.MaterialRecord()
    material.point_size = 1
    scene.scene.update_material(material)

    def on_point_size(size):
        material.point_size = int(size)
        point_size.double_value = size
        scene.scene.update_material(material)

    point_size.set_on_value_changed(on_point_size)
    layout_point_size.add_child(point_size_label)
    layout_point_size.add_child(point_size)

    background_settings.add_child(layout_point_size)

    # ---------------------------------------
    #           CHANGE Navigation Modes
    # ---------------------------------------
    # layout pour la navigation
    layout_nav = gui.Vert()
    layout_nav_label = gui.Label("Nav modes")
    layout_nav_button = gui.Horiz(material_spacing*em, gui.Margins(material_spacing*em, material_spacing*em,material_spacing*em,material_spacing*em))

    def set_mouse_mode_rotate():
        scene.set_view_controls(gui.SceneWidget.Controls.ROTATE_CAMERA)
        arcball_button.background_color = gui.Color(r=1.0, g =167/255, b=0.0)
        fly_button.background_color = gui.Color(r=25/255, g=79/255, b=140/255)

    def set_mouse_mode_fly():
        scene.set_view_controls(gui.SceneWidget.Controls.FLY)
        fly_button.background_color = gui.Color(r=1.0, g =167/255, b=0.0)
        arcball_button.background_color = gui.Color(r=25/255, g=79/255, b=140/255)

    def set_mouse_mode_model():
        scene.set_view_controls(gui.SceneWidget.Controls.ROTATE_MODEL)

    arcball_button = gui.Button("Trackball")
    arcball_button.background_color = gui.Color(r=1.0, g =167/255, b=0.0)
    arcball_button.set_on_clicked(set_mouse_mode_rotate)

    fly_button = gui.Button("Fly")
    fly_button.background_color = gui.Color(r=25/255, g=79/255, b=140/255)
    fly_button.set_on_clicked(set_mouse_mode_fly)

    layout_nav_button.add_child(arcball_button)
    layout_nav_button.add_child(fly_button)

    layout_nav.add_child(layout_nav_label)
    layout_nav.add_child(layout_nav_button)

    background_settings.add_child(layout_nav)





























    settings_panel.add_child(background_settings)


    info = gui.Label("")

    def on_layout(layout_context):
        r = window.content_rect
        scene.frame = r
        width = 25 * layout_context.theme.font_size
        #height = 17 * layout_context.theme.font_size

        height = min(
                r.height,
                settings_panel.calc_preferred_size(
                    layout_context, gui.Widget.Constraints()).height)

        # gestion settings
        #settings_panel.frame = gui.Rect(r.get_right() - width, r.y, width,
        #                                height)
        settings_panel.frame = gui.Rect(r.get_left(), r.y, width,
                                        height)

        pref = info.calc_preferred_size(layout_context,
                                         gui.Widget.Constraints())





    window.set_on_layout(on_layout)
    window.add_child(scene)
    window.add_child(settings_panel)

    #INDICE_CLOUD+=1


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
        global GLOBAL_INDEX_LIST, LOCAL_INDEX_LIST, COORDS_LIST, COLORS_LIST, POSES_LIST, CAMERA_ACTOR_LIST, AUTOTRACK, SHOW_CAMERA

        # on check si on des indices a update en stock

        if LOCAL_INDEX_LIST:
            
            # on loop sur les indexes
            for ix in LOCAL_INDEX_LIST:
                
                # on delete une KF deja traite
                if ix in GLOBAL_INDEX_LIST:
                    scene.scene.remove_geometry("PointCloud "+ str(ix))
                    scene.scene.remove_geometry("Camera "+ str(ix))


                if ix == LOCAL_INDEX_LIST[-1]:
                    cam_actor = create_camera_actor(scale=0.1)
                else:
                    cam_actor = create_camera_actor()

                cam_actor.transform(POSES_LIST[ix])
                cam_actor.transform(TRANSFO_CAM)

                if SHOW_CAMERA:
                    scene.scene.add_geometry("Camera " + str(ix), cam_actor,material)

                CAMERA_ACTOR_LIST[ix] = cam_actor

                # on update la geometry
                pcd = o3d.geometry.PointCloud()
                pcd.points = o3d.utility.Vector3dVector(COORDS_LIST[ix])
                pcd.colors = o3d.utility.Vector3dVector(COLORS_LIST[ix])

                scene.scene.add_geometry("PointCloud " + str(ix), pcd, material)

            # on delete les indices une fois update fait
            LOCAL_INDEX_LIST = []

            # bounds = scene.scene.bounding_box
            # scene.setup_camera(60, bounds, bounds.get_center())
            # scene.scene.show_axes(True)

            if AUTOTRACK == True:
                cles = list(CAMERA_ACTOR_LIST.keys())
                derniere_cle = cles[-1]
                pcd = CAMERA_ACTOR_LIST[derniere_cle] 
                points = np.asarray(pcd.points)
                # get points
                origine = points[0]
                barycentre = np.mean(points[1:5], axis=0)
                # compute verticale de la camera
                verticale = points[-1] - barycentre
                # Calculez la norme du vecteur verticale
                norme_verticale = np.linalg.norm(verticale)
                # Calculez le vecteur normalisé
                vecteur_normalise = verticale / norme_verticale
                # compute camera direction
                cam_dir = origine - barycentre
                norme_cam_dir = np.linalg.norm(cam_dir)
                cam_dir_normalise = cam_dir / norme_cam_dir
                # set up camera
                bounds = pcd.get_axis_aligned_bounding_box()
                center = bounds.get_center()
                scene.setup_camera(60.0, bounds, center)
                scene.look_at(center, center + cam_dir_normalise, -vecteur_normalise)

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











