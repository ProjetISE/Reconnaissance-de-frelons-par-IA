"""
Script de Contrôle Laser avec Conversion de Coordonnées
"""

import numpy as np
import pantilt
import time

pantilt=pantilt.PanTilt()
pantilt.addSsc32()
pantilt.setPanTiltRad(0,0)  

#à définir selon les valeurs réelles pour passer de la salle au monde
offset = np.array([-1.54, 0.67, 2.23]) 

# Définir la fonction pour convertir les coordonnées de la0 salle au monde
def salle_vers_monde(salle_coords, offset):
    for i in range(3): 
        salle_coords[i] += offset[i]
    return salle_coords

# Coordonnées du point dans le référentiel "salle"
salle_coords = np.array([float(input("Coordonnée X dans la salle : ")),
                         float(input("Coordonnée Y dans la salle : ")),
                         float(input("Coordonnée Z dans la salle : "))])

#salle_coords[0] = 0.6738*salle_coords[0] + 0.2806 
#calibration sur plusieurs données ??? 
#à faire ?

# Convertir les coordonnées de la salle au monde
camera_coords = salle_vers_monde(salle_coords, offset)

# Définition des angles de pan et de tilt dans le référentiel de la caméra
pan, tilt, Lx, ok = pantilt.MGI(camera_coords[0],camera_coords[1],camera_coords[2])

if ok:
    print("Angles de Pan et Tilt dans le référentiel de la caméra : ", pan, tilt)

    # Déplacement du système pan tilt pour viser le point 
    pantilt.setPanTiltRad(pan, tilt)

    # Activation du laser
    pantilt.setLaserState(True)
    time.sleep(100)
    pantilt.setLaserState(False)
else:
    print("Le point spécifié est hors de portée.")
