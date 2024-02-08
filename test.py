import cv2
from roboflow import Roboflow

# Initialiser Roboflow et charger le modèle
rf = Roboflow(api_key="UQWMmmp4d1h0QEveclY3")
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

    # Dessiner les boîtes englobantes et les étiquettes sur la frame redimensionnée
    for pred in response["predictions"]:
        # Ajuster les coordonnées pour le centrage basé sur le milieu de l'objet
        center_x = int(pred["x"] * (100 / scale_percent))
        center_y = int(pred["y"] * (100 / scale_percent))
        width = int(pred["width"] * (100 / scale_percent))
        height = int(pred["height"] * (100 / scale_percent))

        # Calculer le coin supérieur gauche et le coin inférieur droit
        start_point = (center_x - width // 2, center_y - height // 2)
        end_point = (center_x + width // 2, center_y + height // 2)

        # Choisir la couleur en fonction de la classe détectée
        if pred['class'] == 'hornet':
            color = (0, 0, 255)  # Rouge pour "hornet"
        elif pred['class'] == 'bee':
            color = (0, 255, 0)  # Vert pour "bee"
        else:
            color = (255, 0, 0)  # Couleur par défaut

        thickness = 2
        cv2.rectangle(frame, start_point, end_point, color, thickness)
        label = f"{pred['class']}"
        # Positionner le texte au-dessus du coin supérieur gauche de la boîte englobante
        cv2.putText(frame, label, (start_point[0], start_point[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        confidence_percentage = pred["confidence"] * 100
        label = f"{pred['class']} {confidence_percentage:.2f}%"
        cv2.putText(frame, label, (start_point[0], start_point[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    
    out.write(frame)
    # Afficher la frame originale annotée
    cv2.imshow("Frame Annotée", frame)

    # Quitter avec la touche 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Libérer la capture et fermer les fenêtres
cap.release()
cv2.destroyAllWindows()
