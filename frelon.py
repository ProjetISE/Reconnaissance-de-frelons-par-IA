import cv2
from roboflow import Roboflow

# Initialiser Roboflow et charger le modèle
rf = Roboflow(api_key="ohEuViyjUuambcMVH60V")
project = rf.workspace().project("hornetbee")
model = project.version(2).model

# Chemin du fichier vidéo
video_path = "video111.mp4"

# Ouvrir la vidéo
cap = cv2.VideoCapture(video_path)

# Vérifier si la vidéo a été ouverte correctement
if not cap.isOpened():
    print("Erreur : Impossible d'ouvrir la vidéo.")
    exit()

# Déterminer le codec et créer un objet VideoWriter
fourcc = cv2.VideoWriter_fourcc(*'MP4V')  # Codec
fps = cap.get(cv2.CAP_PROP_FPS)  # Taux de frames par seconde de la vidéo source
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))  # Largeur de la frame de la vidéo source
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))  # Hauteur de la frame de la vidéo source
out = cv2.VideoWriter('video_traitee.mp4', fourcc, fps, (frame_width, frame_height))

while True:
    # Lire la frame
    ret, frame = cap.read()
    if not ret:
        print("Erreur : Impossible de lire la vidéo ou fin de la vidéo.")
        break

    # Réduire la taille de la frame
    scale_percent = 50  # Réduction de 50%
    width = int(frame.shape[1] * scale_percent / 100)
    height = int(frame.shape[0] * scale_percent / 100)
    dim = (width, height)
    resized_frame = cv2.resize(frame, dim, interpolation=cv2.INTER_AREA)

    # Sauvegarder la frame redimensionnée dans un fichier temporaire
    temp_image_path = "temp_frame.jpg"
    cv2.imwrite(temp_image_path, resized_frame)
    
    # Effectuer l'inférence sur la frame redimensionnée
    response = model.predict(temp_image_path, confidence=40, overlap=30).json()

    # Dessiner un rectangle rouge plein sur chaque frelon détecté
    for pred in response["predictions"]:
        if pred['class'] == 'hornet':
            center_x = int(pred["x"] * (100 / scale_percent))
            center_y = int(pred["y"] * (100 / scale_percent))
            width = int(pred["width"] * (100 / scale_percent))
            height = int(pred["height"] * (100 / scale_percent))

            start_point = (center_x - width // 2, center_y - height // 2)
            end_point = (center_x + width // 2, center_y + height // 2)

            # Dessiner un rectangle plein de couleur rouge pour cacher le frelon
            cv2.rectangle(frame, start_point, end_point, (0, 255, 0), -1)  # Vert et plein

    # Écrire la frame traitée dans le fichier vidéo de sortie
    out.write(frame)

    # Afficher la frame originale annotée
    cv2.imshow("Frame Annotée", frame)

    # Quitter avec la touche 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Libérer la capture et fermer les fenêtres, et relâcher l'objet VideoWriter
cap.release()
out.release()  # Important pour s'assurer que la vidéo est sauvegardée correctement
cv2.destroyAllWindows()
