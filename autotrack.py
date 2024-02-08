#---------------------------------------------------------------------------------------------
# video from youtube-dl https://www.youtube.com/watch?v=xtAwipxys90
# program based on https://livecodestream.dev/post/object-tracking-with-opencv/#wiot
#-----------------------------------------------------------------------------------------
import cv2
import sys
import os
#---------------------------------------------------------------
# useDisplay indicate if we have a valid Display to Use
#-------------------------------------------------------------
debug=True
useDisplay=True
try:
    display=os.environ["DISPLAY"]
except:
    useDislay=False

(major_ver, minor_ver, subminor_ver) = (cv2.__version__).split('.')





fgbg = cv2.createBackgroundSubtractorMOG2()

if __name__ == '__main__' : 
    # Set up tracker.
    # Instead of CSRT, you can also use
 
    tracker_types = ['BOOSTING', 'MIL','KCF', 'TLD', 'MEDIANFLOW', 'GOTURN', 'MOSSE', 'CSRT']
    tracker_type = tracker_types[7]
    
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
# Read video
video = cv2.VideoCapture("frelons.mkv")
#video = cv2.VideoCapture(0) # for using CAM

# Exit if video not opened.
if not video.isOpened():
    print("Could not open video")
    sys.exit()
bbox = (937, 857, 90, 66)  
initial_time= 14000
#bbox = (581, 684, 92, 59)
#initial_time= 20000

# Read first frame.
video.set(cv2.CAP_PROP_POS_MSEC, initial_time)
#video.set(cv2.CAP_PROP_POS_FRAMES, index)
t=video.get(cv2.CAP_PROP_POS_MSEC)

ok, frame = video.read()
fgmask = fgbg.apply(frame)

if not ok:
    print ('Cannot read video file')
    sys.exit()

# Uncomment the line below to select a specific bounding box
#bbox = cv2.selectROI(frame, False)
print("bbox =",bbox, " initial time =",t)
STATE_SEARCH_FRELON=1
STATE_FOLLOW_FRELON=2

state=STATE_SEARCH_FRELON

# Initialize tracker with first frame and bounding box
ok = tracker.init(frame, bbox)
finished=False
while not finished:
    ok, frame = video.read()
    if state==STATE_SEARCH_FRELON:
        fgmask = fgbg.apply(frame)    
        src_gray = cv2.blur(fgmask, (3,3))
        if useDisplay==True:
            # Display result
            cv2.imshow("searching a flying hornet", fgmask)        
    if state==STATE_FOLLOW_FRELON:
        # Read a new frame
        if not ok:
            break
        
        # Start timer
        timer = cv2.getTickCount()

        # Update tracker
        ok, bbox = tracker.update(frame)

        # Calculate Frames per second (FPS)
        fps = cv2.getTickFrequency() / (cv2.getTickCount() - timer);

        # Draw bounding box
        if ok:
            # Tracking success
            p1 = (int(bbox[0]), int(bbox[1]))
            p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
            cv2.rectangle(frame, p1, p2, (255,0,0), 2, 1)
        else :
            # Tracking failure
            cv2.putText(frame, "Tracking failure detected", (100,80), cv2.FONT_HERSHEY_SIMPLEX, 0.75,(0,0,255),2)

        # Display tracker type on frame
        cv2.putText(frame, tracker_type + " Tracker", (100,20), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (50,170,50),2);
    
        # Display FPS on frame
        cv2.putText(frame, "FPS : " + str(int(fps)), (100,50), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (50,170,50), 2);
        if useDisplay==True:
            # Display result
            cv2.imshow("Tracking", frame)

    # Exit if ESC pressed
    if debug==True:
        # wait indefinitely for a key in debug mode
        key=cv2.waitKey(0)& 0xFF
    else:
        # get key without waiting in normal mode
        key=cv2.waitKey(1)& 0xFF  
    if key == ord('q'): # if press SPACE bar
        break

video.release()
cv2.destroyAllWindows()
