import cv2
from cv2 import inRange
from cv2 import WINDOW_AUTOSIZE
import pantilt
import time
print(cv2.__version__)
import numpy as np
import equ_rec
FEEDBACK=True
DETECT_CONTOURS=True
SHOW_IMAGE=True
SHOW_TRACKBARS=True
PRINT_VALUES=True
import sys

def get_tracker(tracker_type):
    (major_ver, minor_ver, subminor_ver) = (cv2.__version__).split('.')
    if int(minor_ver) < 3:
            tracker = cv2.Tracker_create(tracker_type)
    else:
        if tracker_type == 'BOOSTING':
            tracker = cv2.TrackerBoosting_create()
        elif tracker_type == 'MIL':
            tracker = cv2.TrackerMIL_create()
        elif tracker_type == 'KCF':
            tracker = cv2.TrackerKCF_create()
        elif tracker_type == 'TLD':
            tracker = cv2.TrackerTLD_create()
        elif tracker_type == 'MEDIANFLOW':
            tracker = cv2.TrackerMedianFlow_create()
        elif tracker_type == 'GOTURN':
            tracker = cv2.TrackerGOTURN_create()
        elif tracker_type == 'MOSSE':
            tracker = cv2.TrackerMOSSE_create()
        elif tracker_type == "CSRT":
            tracker = cv2.TrackerCSRT_create()
    return tracker  
if __name__ == '__main__' :
    # Set up tracker.
    # Instead of CSRT, you can also use
    tracker_types = ['BOOSTING', 'MIL','KCF', 'TLD', 'MEDIANFLOW', 'GOTURN', 'MOSSE', 'CSRT']
    tracker_type=tracker_types[7]
    tracker=get_tracker(tracker_type)  
# mouse_click.
def mouse_click(event, x, y, 
                flags,params):
    # to check if left mouse 
    # button was clicked
    if event == cv2.EVENT_LBUTTONDOWN:         
        print('new left pixel at x=',x, 'y=',y)
    elif event == cv2.EVENT_RBUTTONDOWN:          
        print('new right pixel at x=',x, 'y=',y)

#---------------------------------------------------------------
# get laser pixel as a function of distance d of point
# interpolation parabolique depuis des mesures manuelles
# preparation des donnees
#-------------------------------------------------------------------
def getLaserPixel(cm=1000,cols=1280): # pixel as a function of distance within laser and target, in centimeters
    if cols==1280:
        dataLaser=np.array([
            [40,500,571],
            [76.5,501,532],
            [126.5,502,514],
            [200,505,504],
            [124.5+270,506,496],
            [126.5+330+320,470,477]])
    elif cols==640:
        dataLaser=np.array([
        [440,224,240]])    
    cmLaser=dataLaser[:,0] 
    xLaser=dataLaser[:,1] 
    yLaser=dataLaser[:,2] 
    x=xLaser[-1]+105
    y=yLaser[-1]+120
    return x,y
#define the events for the
def draw_points(img1,x=[],y=[],color=(0,255,0),drawFromCenter=False):
    rows,columns,_= img1.shape
#   img1 = cv.cvtColor(img1,cv.COLOR_GRAY2BGR)
    center=(int(columns/2),int(rows/2))
    #print(rows,columns)
    if len(x)<1:
        x=[int(columns/2)]
        y=[int(rows/2)]
    for k in range(0,len(x)):
        xk=int(x[k])
        yk=int(y[k])
        #color = tuple(np.random.randint(0,255,3).tolist())
        if drawFromCenter:
            img1 = cv2.line(img1, center, (xk,yk), color,1)

        img1 = cv2.line(img1, (xk-3,yk), (xk+3,yk), color,1)
        img1 = cv2.line(img1, (xk,yk-3), (xk,yk+3), color,1)
        k=k+1
    return img1
#---------------------------------------------------------
# tourelle panTilt
#--------------------------------------------------------        
pan_tilt=pantilt.PanTilt(LXMin=7,LY=-0.5,LZw=6.1)
pan_tilt.setLimitsDegres(panMin=-45,panMax=45,tiltMin=-20,tiltMax=42)

useSsc32=True
if useSsc32:
    #pan_tilt.addSsc32()
    #HS422 pantilt
    pan_tilt.addSsc32(usZeroPan=1500,usZeroTilt=1500,panUsRad=-500/(np.pi/4),tiltUsRad=500/(np.pi/4),servoPan=0,servoTilt=1,servoLaser=2,portName="/dev/ttyUSB0",baudRate=115200,timeOutSecond=0.05)
def nothing(x):
    pass
if SHOW_IMAGE:
    cv2.namedWindow('nanoCam')
    cv2.setMouseCallback('nanoCam', mouse_click)
RED=0
GREEN=1
BLUE=2
Reglage=GREEN

if Reglage==GREEN:
    defaultHueLower=50
    defaulthueUpper=100
    defaultsatLow=100
    defaultsatHigh=255
    defaultvalLow=100
    defaultvalHigh=255
elif Reglage==RED:
    defaultHueLower=0
    defaulthueUpper=14
    defaultsatLow=151
    defaultsatHigh=255
    defaultvalLow=85
    defaultvalHigh=255
if SHOW_TRACKBARS:
    cv2.namedWindow('Trackbars',cv2.WINDOW_NORMAL)#,WINDOW_AUTOSIZE)
    cv2.moveWindow('Trackbars',1320,0)
    cv2.createTrackbar('hueLower', 'Trackbars',defaultHueLower,255,nothing)
    cv2.createTrackbar('hueUpper', 'Trackbars',defaulthueUpper,255,nothing)
    cv2.createTrackbar('satLow', 'Trackbars',defaultsatLow,255,nothing)
    cv2.createTrackbar('satHigh', 'Trackbars',defaultsatHigh,255,nothing)
    cv2.createTrackbar('valLow','Trackbars',defaultvalLow,255,nothing)
    cv2.createTrackbar('valHigh','Trackbars',defaultvalHigh,255,nothing)
    if not FEEDBACK:
        scalePanTilt=10
        maxPan=20 *scalePanTilt
        maxTilt=20 *scalePanTilt
        scalePanTilt=np.pi/180/scalePanTilt
        trackPan='pan+'+str(maxPan)
        trackTilt='tilt+'+str(maxTilt)
        cv2.createTrackbar(trackPan,'nanoCam',maxPan,2*maxPan,nothing)
        cv2.createTrackbar(trackTilt,'nanoCam',maxTilt,2*maxTilt,nothing)


dispW=640
dispH=480
flip=2
#Uncomment These next Two Line for Pi Camera
#camSet='nvarguscamerasrc !  video/x-raw(memory:NVMM), width=3264, height=2464, format=NV12, framerate=21/1 ! nvvidconv flip-method='+str(flip)+' ! video/x-raw, width='+str(dispW)+', height='+str(dispH)+', format=BGRx ! videoconvert ! video/x-raw, format=BGR ! appsink'
#cam= cv2.VideoCapture(camSet)

#Or, if you have a WEB cam, uncomment the next line
#(If it does not work, try setting to '1' instead of '0')
cam=cv2.VideoCapture(0)
cols=1280
rows=960
cols=640
rows=480

cam.set(cv2.CAP_PROP_FRAME_WIDTH,cols)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT,rows)
#cam.set(cv2.CAP_PROP_FPS, 30)
#------------------------------
# parametres asservissement 
#------------------------------

targetLocked=5
targetLost=200

refX,refY=getLaserPixel(1000,cols)  
mesX=refX
mesY=refY
TARGET_LOCKED=1
TARGET_UNLOCKED=2
TARGET_LOST=3
state=TARGET_LOST

if FEEDBACK:
    # possible states when using feddback

    USE_TUSTIN=True
    Kpan=(767-479)/((10.4)*np.pi/180) # deltax / deltapan (rad), manual measure
    Ktilt=(595-290)/((10.3)*np.pi/180) # deltay / deltatilt (rad),, manual measure
    Kpan=(Kpan*cols)/1280
    Ktilt=(Ktilt*rows)/960
    if cols==1280:
        Te=0.130 # mesure de Te qd Ok
        wi=0.5
        TauSec=0.6 # time constant for regulation in ms 
        KregPan=1/(TauSec*Kpan)# Tau =1/(K.Kpan) => K=1/(Tau.Kpan)
        KregTilt=1/(TauSec*Ktilt)# Tau =1/(K.Ktilt) => K=1/(Tau.Ktilt)
        equPan=equ_rec.EquRec([wi*KregPan,KregPan],[0,1,1],Te)
        equTilt=equ_rec.EquRec([wi*KregTilt,KregTilt],[0,1,1],Te)
    elif cols==640:
        Te=0.033 # mesure de Te qd Ok
        TEST=True
        if not TEST:
            TauSecPan=0.2 # time constant for regulation in ms 
            TauSecTilt=0.2 # time constant for regulation in ms
            a=1.5        
            tauPred=0.2*a
            tauFlt=0.2/a
            KregPan=1/(TauSecPan*Kpan)# Tau =1/(K.Kpan) => K=1/(Tau.Kpan)
            KregTilt=1/(TauSecTilt*Ktilt)# Tau =1/(K.Ktilt) => K=1/(Tau.Ktilt)
            equPan=equ_rec.EquRec([KregPan/a,KregPan*tauPred/a],[0,1,tauFlt],Te)
            equTilt=equ_rec.EquRec([KregTilt/a,KregTilt*tauPred/a],[0,1,tauFlt],Te)
        else:
            w0=20
            KHF=0.3
            KBF=max(cols,rows)
            equPan=equ_rec.EquRec([KHF*w0/Kpan,KHF/Kpan],[KHF*w0/KBF,1],Te)
            equTilt=equ_rec.EquRec([KHF*w0/Ktilt,KHF/Ktilt],[KHF*w0/KBF,1],Te)

    equPan.setOutputLimits(pan_tilt.panMin,pan_tilt.panMax)
    equTilt.setOutputLimits(pan_tilt.tiltMin,pan_tilt.tiltMax)
    equPan.setOutputRateLimits(-120*np.pi/180,120*np.pi/180 )
    equTilt.setOutputRateLimits(-120*np.pi/180,120*np.pi/180 )
    okVisee=False
pan=0
tilt=0
ditter=0 *np.pi/180 #ditter on pan and tilt in rad ( should be in micro seconds)
mesOK=False

t0S=time.time()
if PRINT_VALUES:
    tiS=t0S
    derivTime=equ_rec.EquRec([0,1],[1,10],1)
while True:
    ret=False
    while not ret:
        ret, frame = cam.read()
    ditter=-ditter    
    if PRINT_VALUES:
        tfS=time.time()-tiS
        dt=derivTime.oneStep(tfS)

    else: # open loop, manually change pan and tilt    
        if SHOW_TRACKBARS:  
            pan=cv2.getTrackbarPos(trackPan, 'nanoCam')-maxPan
            tilt=cv2.getTrackbarPos(trackTilt, 'nanoCam')-maxTilt
            pan=pan*scalePanTilt
            tilt=tilt*scalePanTilt
        pan=pan+ditter
        tilt=tilt+ditter    
        pan_tilt.setPanTiltRad(pan,tilt,timeTravelms=0)
    ditter=-ditter
    if DETECT_CONTOURS:
        if not ret:
            print ('Cannot read video file')
            sys.exit()

        # Uncomment the line below to select a specific bounding box
        bbox = cv2.selectROI(frame, False)

        # Initialize tracker with first frame and bounding box
        ok = tracker.init(frame, bbox)
        finished=False
        while not finished:
            # Read a new frame
            ok, frame = cam.read()
            if not ok:
                break
            
            # Update tracker
            ok, bbox = tracker.update(frame)

            # Draw bounding box
            if ok:
                # Tracking success
                p1 = (int(bbox[0]), int(bbox[1]))
                p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
                cv2.rectangle(frame, p1, p2, (0,255,0), 2, 1)
                cv2.imshow('Draw Rectangle', frame)
                key = cv2.waitKey(1) & 0xFF
            if len(bbox)>0:
                (x, y, w, h) = (int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3]))
                xc=x+w/2
                yc=y+h/2
                if PRINT_VALUES:
                    print('dt=',int(dt*1000),' ms , [pan=', int(pan*18000/np.pi),'tilt=',int(tilt*18000/np.pi),'] (deg/100) , xc=',xc, 'yc =',yc, 'errx=',refX-xc,'erry=',refY-yc)
                if (w>=3)and(h>=3):
                    #cv2.drawContours(frame,[cnt],0,(255,0,0),3)
                    okVisee=(refX>=xc-targetLocked)and(refX<=xc+targetLocked)and(refY>=yc-targetLocked) and (refY<=yc+targetLocked)
                    if okVisee:
                        newState=TARGET_LOCKED
                        cv2.rectangle(frame,(x,y),(x+w,y+h),(0,0,255),1)                    
                    else:   
                        cv2.rectangle(frame,(x,y),(x+w,y+h),(255,0,0),2)
                        abandonVisee=(refX<=xc-targetLost)or(refX>=xc+targetLost)or(refY<=yc-targetLost) or (refY>=yc+targetLost)
                        if abandonVisee:
                            newState=TARGET_LOST
                        else:
                            newState=TARGET_UNLOCKED    
                    if newState!=state:
                        if newState==TARGET_LOCKED:
                            pan_tilt.setLaserState(True)
                        elif newState== TARGET_LOST:
                            pan_tilt.setLaserState(False) 
                        state=newState
                    mesX=xc
                    mesY=yc
                    mesOK=True
                if FEEDBACK:
                    if mesOK: # update value only if we get a new measure
                        tS=time.time()
                        dtS=max(tS-t0S,0.01)
                        #print('dt =',dtS,' s')
                        t0S=tS
                        mesOK=dtS<0.150
                    if mesOK:
                        errX=refX-mesX
                        errY=refY-mesY
                        #if not okVisee:
                        #print('do not apply dpan and dtilt, laser is on the target!!!') 
                        #else:    
                        if USE_TUSTIN:
                            newPan=equPan.oneStep(errX)
                            newTilt=equTilt.oneStep(errY)
                            deltaPan=newPan-pan
                            deltaTilt=newTilt-tilt
                        else:
                            deltaPan=dtS*KregPan*errX
                            deltaTilt=dtS*KregTilt*errY            
                        pan=pan+deltaPan
                        tilt=tilt+deltaTilt
                        #   print('pan;dpan =',pan,':',deltaPan*180/np.pi,'deg, tilt:dtilt =',tilt,':',deltaTilt*180/np.pi,' deg')
                    pan_tilt.setPanTiltRad(pan+ditter,tilt+ditter,timeTravelms=0) # apply pan and tilt at each new image
    if SHOW_IMAGE:
        frame=draw_points(frame,[mesX],[mesY],(255,0,0))  
        frame=draw_points(frame) # draw center of frame      
        frame=draw_points(frame,[refX],[refY],(0,0,255))  
        cv2.imshow('nanoCam',frame)
        cv2.moveWindow('nanoCam',0,0)
    

    if cv2.waitKey(1)==ord('q'):
        break
    if cv2.waitKey(1)==ord('r'): #reset pan and tilt
        print('TO DO, RESET PAN AND TILT TO ZERO WITH WORKING FEEDBACK')
pan_tilt.close()
cam.release()
cv2.destroyAllWindows()
