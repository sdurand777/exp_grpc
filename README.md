# exp_grpc

Test grpc

On a un serveur qui gere les pcd
Un client 1 qui envoie les pcd au serveur
Un client 2 qui recoit les pcd du serveur

test_gen pour gen points pour open3d
serveur pour gerer les data
test_disp pour afficher les points dans open3d

Finalisation de la gestion des slam_data en test
On utilise les proto_files_exp
Dans scripts_exp on a les 3 fichiers
GEN_SLAM_DATA pour generer les data simuler un SLAM
SERVEUR_SLAM_DATA pour recuperer les data et les transmettre au visualisateur
DISP_SLAM_DATA pour recuperer les data du visualisateur et les afficher avec open3D
