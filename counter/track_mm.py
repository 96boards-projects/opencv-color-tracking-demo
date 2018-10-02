"""
Summary: This Python program uses OpenCV to isolate colors and then track colored object going in a singular direction and counting the number of objects that.   It is focused on using Peanut M&M's as a baseline, but could be easily modified for varying objects and varying colors.   This program requires tuning.  Please see the associated instructions on my github for more details.  


Copyright 2018 Don Harbin

Permission is hereby granted, free of charge, to any person obtaining a copy of this software 
and associated documentation files (the "Software"), to deal in the Software without restriction, 
including without limitation the rights to use, copy, modify, merge, publish, distribute, 
sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is 
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or 
substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, 
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR 
PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE 
FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR 
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER 
DEALINGS IN THE SOFTWARE.


"""
from __future__ import division
import numpy as np
import cv2
import MM
from file_utility import writeCount
import time
import imutils
from imutils.video import WebcamVideoStream

# Used to tune morphologicals
kernel3 = np.ones((3,3),np.uint8)
kernel5 = np.ones((5,5),np.uint8)
kernel7 = np.ones((7,7),np.uint8)
kernel11 = np.ones((11,11),np.uint8)
kernel15 = np.ones((15,15),np.uint8)
kernel20 = np.ones((20,20),np.uint8)
kernel25 = np.ones((25,25),np.uint8)

#Variables
font = cv2.FONT_HERSHEY_SIMPLEX

# Tuning parameters
mm = []
max_age = 4            # a mm object only lives through max_age passes
min_radius = 11        # Adjust to size of m & m. Impacted by distance from camera

#DEBUG import pdb; pdb.set_trace() # Begin debug

##########
# Create color objects  
# Note: Run the colorIsolationApp.py to define HSV min and max parms for each color.
##########

# RED
color_id = 0          # One for each color
redCircleColor = (0,0,255)
redTextLocation = (10,25)

red_hue_min = 0
red_saturation_min = 80 
red_value_min = 23 
red_hsv_min=np.array([red_hue_min,red_saturation_min,red_value_min])

red_hue_max = 10
red_saturation_max = 256 
red_value_max = 110
red_hsv_max=np.array([red_hue_max,red_saturation_max,red_value_max])

mm.append(MM.M_and_M(color_id, "Red", max_age, redCircleColor, red_hsv_min,red_hsv_max,redTextLocation))  # Create Red Tracking Object

# BLUE
color_id += 1
blueCircleColor = (255,0,0)
blueTextLocation = (10,50)

blue_hue_min = 83
blue_saturation_min = 96 
blue_value_min = 55 
blue_hsv_min=np.array([blue_hue_min,blue_saturation_min,blue_value_min])

blue_hue_max = 143
blue_saturation_max = 251 
blue_value_max = 167
blue_hsv_max=np.array([blue_hue_max,blue_saturation_max,blue_value_max])

mm.append(MM.M_and_M(color_id, "Blue", max_age, blueCircleColor, blue_hsv_min,blue_hsv_max,blueTextLocation))  # Create Blue Tracking Object

# ORANGE
color_id += 1
orangeCircleColor = (0,125,255)
orangeTextLocation = (10,75)

orange_hue_min = 5
orange_saturation_min = 190 
orange_value_min = 97 
orange_hsv_min=np.array([orange_hue_min,orange_saturation_min,orange_value_min,])

orange_hue_max = 20
orange_saturation_max = 256 
orange_value_max = 185
orange_hsv_max=np.array([orange_hue_max,orange_saturation_max,orange_value_max])

mm.append(MM.M_and_M(color_id, "Orange", max_age, orangeCircleColor, orange_hsv_min,orange_hsv_max,orangeTextLocation))  # Create Orange Tracking Object

# YELLOW
color_id += 1
yellowCircleColor = (0,255,255)
yellowTextLocation = (10,100)

yellow_hue_min = 27
yellow_saturation_min = 150 
yellow_value_min = 90 
yellow_hsv_min=np.array([yellow_hue_min,yellow_saturation_min,yellow_value_min])

yellow_hue_max = 38
yellow_saturation_max = 256 
yellow_value_max = 192
yellow_hsv_max=np.array([yellow_hue_max,yellow_saturation_max,yellow_value_max])

mm.append(MM.M_and_M(color_id, "Yellow", max_age, yellowCircleColor, yellow_hsv_min,yellow_hsv_max,yellowTextLocation))  # Create Yellow Tracking Object

# BLACK
color_id += 1
blackCircleColor = (0,0,0)
blackTextLocation = (10,125)

black_hue_min = 5
black_saturation_min = 11 
black_value_min = 0 
black_hsv_min=np.array([black_hue_min,black_saturation_min,black_value_min])

black_hue_max = 59
black_saturation_max = 187  
black_value_max = 39
black_hsv_max=np.array([black_hue_max,black_saturation_max,black_value_max])

mm.append(MM.M_and_M(color_id, "Black", max_age, blackCircleColor, black_hsv_min,black_hsv_max,blackTextLocation))  # Create Black Tracking Object

# GREEN
color_id += 1
greenCircleColor = (0,255,0)
greenTextLocation = (10,150)

green_hue_min = 46
green_saturation_min = 50 
green_value_min = 50 
green_hsv_min=np.array([green_hue_min,green_saturation_min,green_value_min])

green_hue_max = 76
green_saturation_max = 177 
green_value_max = 174
green_hsv_max=np.array([green_hue_max,green_saturation_max,green_value_max])

mm.append(MM.M_and_M(color_id, "Green", max_age, greenCircleColor, green_hsv_min,green_hsv_max, greenTextLocation))  # Create Green Tracking Object

##########
# Create video camera object and start streaming to it.
##########
#cap = cv2.VideoCapture(0) # NONTHREAD 0 == Continuous stream
capvs = WebcamVideoStream(src=0)  # THREAD Create video capture in separte thread
capvs.start()

# set up visual imaging for the trigger line that is the count line when crossed
cnt_down=0
y_trigger=160
trigger_line_color=(255,0,0)
trigger_line= np.array([[0, y_trigger],[720, y_trigger]])

counter=0

# Debug variables used to see how long it takes to process a frame.
millis1=0
millis2=0
milli_total=0
fps_count = 1



##########
# Begin the count loop that reads/processes one frame at a time
##########
try:
    #while(cap.isOpened()): # NONTHREAD
    while(True):    # THREAD
        # Capture a still image from the video stream
        #ret, frame = cap.read() # NONTHREAD read a frame
        frame=capvs.read()    # THREAD

        #Debug code to gauge loop timing
        if millis1 != 0: 
            millis2 = millis1
            millis1 = int(round(time.time() * 1000))
        else:
            millis1 = int(round(time.time() * 1000))
        millis = millis1-millis2
        #print "MilliSeconds per processing frame: ", millis

        if fps_count > 49:
            fps=float(1.0/(milli_total/50.0))
            print "Average FPS = ", round((fps*1000),2)
            fps_count = 1
            milli_total=0

            # Write counters from each color to file for Charting Web Page Use.
            count_string=[]
            for mmColor in mm:
                count_string.append(mmColor.getCount())
            writeCount("countTotal.txt",count_string)
        else:
            milli_total += millis
            fps_count += 1
        #Debug <end>

        frame = cv2.resize(frame, (0,0), fx=0.5, fy=0.5)

        ###############
        # Blur - HSV - Mask - erode - dilate
        ###############
        blurred = cv2.GaussianBlur(frame, (11, 11), 0)

        # Convert image to HSV
        hsvframe = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
        ##########
        # Loop on each color
        ##########
        for mmColor in mm:
            #print "Debug: ",mmColor.getColor()

            # Set up the min and max HSV settings 
            mask=cv2.inRange(hsvframe, mmColor.getHSV_min(), mmColor.getHSV_max())  # Red Mask
            # Get rid of noise
            mask = cv2.erode(mask, kernel7, iterations=1)
            mask = cv2.dilate(mask, kernel7, iterations=3)
    
            # Only return the contours parameter and ignore hierarchy parm, hence [-2]    
            # CHAIN_APPROX_SIMPLE to return less contour points (faster/less memory)
            contours0 = cv2.findContours(mask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)[-2]
        
            # Find the largest contour in the mask image, then use
            # it to compute the radius used for circle()
            # Design note: Radius could be hard coded and this step skipped for performance 
            # reasons if needed.
            #radius = 13    # Hard code radius
            if len(contours0) != 0:
                c = max(contours0, key=cv2.contourArea)
                if c.all() == 0:
                    print "Warning Contours: ",contours0
                ((x, y), radius) = cv2.minEnclosingCircle(c)
                print "Debug: valid ",mmColor.getColor()
            #else:
                #print "Warning: Contour Area empty sequence"

            #Iterate through the objects found
            mmColor.rstTrackNext()
            for cnt in contours0:
                print "Debug: contour found in ",mmColor.getColor()

                # Find center of current object
            	M = cv2.moments(cnt)
            	center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
            
                #print (radius)
            	# only proceed if the radius meets a minimum size
            	if radius > min_radius:
                    print "DEBUG: radius meets minimum size", radius
    
                    #TODO: Add max size and logic to split into multiple centroids if too big.


            	    # draw a circle around the centroid of the detected object
                    # in the original RGB frame.  Not the HSV masked frame.
                    # parameters (image, center, radius, color, thickness)
            	    cv2.circle(frame, center, int(radius)+4, mmColor.getCircleColor(), 2) 
                    x, y = center

                    #print "DEBUG: Color, Center(x,y) = ", mmColor.getColor(), center 
                    
                    mmColor.addTrackNext(x,y)    # Used to post process multiple mm objects in next steps
        
            # Save the mask for post processing display 
            locals()["Mask"+mmColor.color]=mask    

            #import pdb; pdb.set_trace() # Begin debug

            ##########
            # Now scan all new mm objects to see if a new ones have dropped in or if pre-existing
            ##########
            mmColor.newObjectCheck()
    

        ##########
        # Display the images
        ##########
        # overlay the trigger line and count onto original image.
        frame = cv2.polylines(frame, [trigger_line], False, trigger_line_color,thickness=4)
    
        for mmColor in mm:
            # Create the Mask images
            temp_mask=(locals()["Mask"+mmColor.color])
            cv2.namedWindow(mmColor.color+' Masked image',cv2.WINDOW_NORMAL)
            cv2.resizeWindow(mmColor.color+' Masked image',320,320)
            cv2.imshow(mmColor.color+' Masked image',temp_mask)

            str_down=mmColor.getColor() + ': '+ str(mmColor.getCount())    
            cv2.putText(frame, str_down, mmColor.getTextLocation(), font, .5, mmColor.getCircleColor(), 2,cv2.LINE_AA) 

        cv2.namedWindow('Frame',cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Frame',320,320)
        cv2.imshow('Frame',frame)
    
        
        ##########
        #Abort and exit with 'Q' or ESC
        ##########
        k = cv2.waitKey(1) & 0xff
        if k == 27:
            break
    
    cap.release() #release video file
    cv2.destroyAllWindows() #close all openCV windows

except RuntimeError, e:
            print "runtime error()"

