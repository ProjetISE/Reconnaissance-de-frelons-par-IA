import numpy as np
# Enable pyserial extensions
import ssc32
import time
import tr_homogene
class PanTilt:
    def get_sol_panTilt(self,cPInit,cPFinal):
        # calcul de pan, tilt tels que le point de coordonnees cPinit dans le repere camera intial
        # soit envoye apres rotation sur le point de coordonnees cP final dans le repere camera final
        # a un facteur d'echelle inconnu pret 
        # typiquement cPinit correspond au coordonnees un point a viser avec un laser ou autre dans le repere initial 
        #             cPfinal correspond au coordonnees d'un point de la ligne visee par le laser, lie au repere camera
 
        cPInit=cPInit/np.linalg.norm(cPInit)
        cPFinal=cPFinal/np.linalg.norm(cPFinal)
        cxPi=cPInit[0]
        cyPi=cPInit[1]
        czPi=cPInit[2]
        cxPf=cPFinal[0]
        cyPf=cPFinal[1]
        czPf=cPFinal[2]
        
        
        #cpanPi = coords point initial dans le repere obtenu apres rotation de pan
        #cpanPi =
        #   cxPi*cos(pan) - czPi*sin(pan)
        #   cyPi
        #   czPi*cos(pan) + cxPi*sin(pan)        
        #cpanPf = coords point final dans le repere obtenu avant rotation de tilt
        #   cxPf
        #   cyPf*cos(tilt) + czPf*sin(tilt)
        #   czPf*cos(tilt) - cyPf*sin(tilt)
        sols_pan=tr_homogene.get_sol_type2(-czPi,cxPi,cxPf) #cxPi*cos(pan) - czPi*sin(pan)==cxPf
        sols_tilt=tr_homogene.get_sol_type2(czPf,cyPf,cyPi) #cyPf*cos(tilt) + czPf*sin(tilt)=cyPi
        ok_pan=False 
        pan=0
        for kpan in range(len(sols_pan)):
            pan_i=sols_pan[kpan,0]
            ok_pan=(pan_i>=-np.pi/2) and (pan_i<=np.pi/2)
            if ok_pan:
                pan=pan_i
                break
        ok_tilt=False
        tilt=0 
        for ktilt in range(len(sols_tilt)):
            tilt_i=sols_tilt[ktilt,0]
            ok_tilt=(tilt_i>=-np.pi/2) and (tilt_i<=np.pi/2)
            if ok_tilt:
                tilt=tilt_i
                break
        ok=ok_pan and ok_tilt     
        return pan,tilt,ok
    
    def addSsc32(self,usZeroPan=1465,usZeroTilt=1545,panUsRad=500/(np.pi/4),tiltUsRad=-75/(6.76*np.pi/180),servoPan=0,servoTilt=1,servoLaser=2,portName="/dev/ttyUSB0",baudRate=115200,timeOutSecond=0.05):    
    #Cette méthode initialise un objet Ssc32 (qui semble être une classe externe ou un module) 
    # pour le contrôle d'un servocommande (pan, tilt et laser). 
    # Les paramètres tels que les zéros des servos, les conversions d'angles, 
    # et les ports de communication sont configurés.     
        self.ssC32=ssc32.Ssc32(portName,baudRate,timeOutSecond)
        self.ssC32.verbose=False
        self.okssC32=True
        self.panUsZeroDegres=usZeroPan
        self.panUsRad=panUsRad
        self.panServo=servoPan
        self.tiltUsZeroDegres=usZeroTilt
        self.tiltUsRad=tiltUsRad
        self.tiltServo=servoTilt
        self.servoLaser=servoLaser
        self.setPanTiltRad(0,0)
        self.setLaserState(True)
    def setLaserState(self,laserState=True):
        self.laserState=laserState
        if self.okssC32:         
            self.ssC32.digitalOutput([self.servoLaser],[laserState])    
    def setLimitsDegres(self,panMin=-45,panMax=45,tiltMin=-45,tiltMax=45):
        self.panMin=panMin*np.pi/180
        self.panMax=panMax*np.pi/180
        self.tiltMin=tiltMin*np.pi/180
        self.tiltMax=tiltMax*np.pi/180    
    def __init__(self, LXMin=7 , LY=-0.5 ,LZw=7 ):
        self.panMin=-2*np.pi/180
        self.panMax=2*np.pi/180
        self.tiltMin=-2*np.pi/180
        self.tiltMax=2*np.pi/180

        self.okssC32=False
        self.LXMin=LXMin
        self.LY=LY
        self.LY2=self.LY*self.LY
        self.LZ=LZw 
        self.dist2Min=self.LXMin*self.LXMin+self.LY2
        self.setLimitsDegres(panMin=-45,panMax=45,tiltMin=-45,tiltMax=45)
        self.setPanTiltRad(0,0)
    def close(self):
        if (self.okssC32):
            self.setPanTiltRad(0,0)
            self.setLaserState(False)
            self.ssC32.close()
    def setPanTiltRad(self,pan=0,tilt=0,timeTravelms=1000):
    #Cette méthode permet de définir les angles de pan et tilt en radians,
    # en prenant en compte les limites définies et en utilisant la classe Ssc32 pour déplacer les servos.
        pan=np.min([self.panMax,pan])
        self.pan=np.max([self.panMin,pan])
        tilt=np.min([self.tiltMax,tilt])
        self.tilt=np.max([self.tiltMin,tilt])
        if (self.okssC32):
            self.panUs=self.pan*self.panUsRad+self.panUsZeroDegres
            self.tiltUs=self.tilt*self.tiltUsRad+self.tiltUsZeroDegres
            self.ssC32.gotoUs([self.panServo,self.tiltServo],[self.panUs,self.tiltUs],timeTravelms)
    def getPanTiltRad(self):
        return self.pan,self.tilt

    def MGI(self,Px,Py,Pz):
    #Cette méthode effectue une cinématique inverse pour convertir les coordonnées d'un point P 
    # dans le repère de la caméra en angles de pan et tilt. Elle utilise également des vérifications 
    # pour s'assurer que le point est atteignable.
        pan=np.arctan2(Py,Px)
        distXY2=(Px*np.cos(pan) + Py*np.sin(pan))
        distXY2=distXY2*distXY2
        Pz2=(Pz-self.LZ)
        Pz2=Pz2*Pz2
        dist2=Pz2 + distXY2
        ok=dist2>=self.dist2Min
        if ok:
            LX2=dist2-self.LY2
            LX=np.sqrt(LX2)
            #-------------------------------------------
            # LX is known, solve tilt equation 
            #Pz -Lz== Ly*cos(tilt) + Lx*sin(tilt)     
            #-------------------------------------------
            alpha=np.arctan2(self.LY,LX) # sin(alpha=Ly), cos(alpha) =Lx
            sin_alpha_plus_tilt=(Pz-self.LZ)/np.sqrt(self.LY2+LX2) 
            alpha_plus_tilt1=np.arcsin(sin_alpha_plus_tilt)
            tilt1=alpha_plus_tilt1-alpha
            if (tilt1>=-np.pi/2) and (tilt1<=np.pi/2):
                tilt=tilt1
            else:    
                tilt2=(np.pi- np.arcsin(alpha_plus_tilt1)) -alpha
                tilt=tilt2
        else:
            #not ok
            tilt=0
            LX=0
        return pan,tilt,LX,ok  
    
      
    def MGD(self,pan,tilt,Lx):
    #Cette méthode effectue une cinématique directe pour convertir les angles de pan et tilt en coordonnées 
    # XYZ dans le repère du monde.
        cp=np.cos(pan)
        sp=np.sin(pan)
        ct=np.cos(tilt)
        st=np.sin(tilt)
        #wX=Lx*cos(pan)*cos(tilt) - Ly*cos(pan)*sin(tilt)
        #wY=Lx*cos(tilt)*sp - Ly*sp*sin(tilt)
        #wZ=Ly*cos(tilt) + Lx*sin(tilt) + LZ
        wX=Lx*cp*ct - self.LY*cp*st
        wY=Lx*ct*sp - self.LY*sp*st
        wZ=self.LY*ct + Lx*st + self.LZ
        return wX,wY,wZ    
    
    
# Receive bytes
testePanTilt=True
if testePanTilt:
    pantilt=PanTilt()
    pantilt.addSsc32()
    pantilt.setPanTiltRad(0,0)    
    time.sleep(1)
    Px=10
    Py=0
    Pz=2
    pan,tilt,LX,ok=pantilt.MGI(Px,Py,Pz)
    print('Px=',Px,' Py=',Py,' Pz=',Pz)
    print('ok=',ok, ' pan=',pan*180/np.pi,'degres, tilt=',tilt*180/np.pi,' degres, LX=',LX)
    wX,wY,wZ=pantilt.MGD(pan,tilt,LX)
    print(' wX=',wX,', wY=',wY,' wZ=',wZ)
    pantilt.setPanTiltRad(pan,tilt)    
    pantilt.close()
