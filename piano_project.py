import cv2 as cv
import numpy as np
import math 
import time
import serial
import time
import matplotlib.pyplot as plt
import warnings
import winsound

warnings.filterwarnings('ignore')    

ser = serial.Serial('COM3', 9600)


capture = cv.VideoCapture(1)
sections = [0] #sections marks where the piano keys are based on coordinates of lines

while True: #loop used for getting lines on the paper to mark the piano keys 
    _,frame = capture.read()
    cv.imshow('Video',frame) #show video
    edges = cv.Canny(frame,50,200) #use canny edge detector to find edges in video

    if cv.waitKey(20) & 0xFF==ord('d'): #press d to stop video and move to next stage
        break

cdst = cv.cvtColor(edges, cv.COLOR_GRAY2BGR) #used to output edges in a picture
lines = cv.HoughLines(edges, 1, np.pi / 180, 45, None, 0, 0) #use edges to find lines, 45 is the threshold
if lines is not None:
    newlines = np.squeeze(lines) #used to get a 2-d array instead of 3-d
    angles = newlines[:, 1] #get angles from new lines array
    onlyvert = newlines[angles < 0.15, :] # use angles to only keep in vertical lines
    onlyvert = onlyvert[onlyvert[:,0].argsort()] #sort onlyvert array so lines are ordered from left to right
    rho = onlyvert[:,0] #onlyvert includes multiple lines per line on the paper, so this is used
    diff = rho[1:] - rho[0:-1] #to only take one line per paper line
    countlines = diff>50 #find where there are a group of lines very close together
    final = np.zeros(np.count_nonzero(countlines)+1) #set size of final based off number of lines 
    indexes = np.where(countlines)[0]+1 #find which lines to keep
    final[0] = 0
    final[1:] = indexes #add which indexes of onlyvert to keep
    
    
    for i in range(0, len(final)): #loop through the lines to keep 
        xcoor = onlyvert[int(final[i])][0] #get x coordinate and angle 
        theta = onlyvert[int(final[i])][1]
        a = math.cos(theta) #this formula uses the distance and radius from Hough output to plot with coordinates
        b = math.sin(theta)
        x0 = a * xcoor
        y0 = b * xcoor
        pt1 = (int(x0 + 1000*(-b)), int(y0 + 1000*(a)))
        pt2 = (int(x0 - 1000*(-b)), int(y0 - 1000*(a)))
        #sections holds the boundaries of where each key starts and ends
        sections.append(int ((int(x0 + 1000*(-b)) + int(x0 - 1000*(-b))) /2)) 
        cv.line(cdst, pt1, pt2, (255,0,0), 1, cv.LINE_AA) #draw lines of where the keys are

sections.append(640) #add right edge
sections.sort()
cv.imshow("Detected Lines (in blue) - Standard Hough Line Transform", cdst)
notes = {'0': 'c4', '1': 'd4', '2': 'e4', '3': 'f4', '4': 'g4'} #map to convert index to filename

currkey = -1 #use these variables to record current and previous states to make sure audio doesn't restart
prevkey = -1 #when a key is held
currpress = False
prevpress = False
while True:
    _,frame = capture.read() #set up video
    cv.imshow('Video',frame)
    edges = cv.Canny(frame,50,200)

    hsv = cv.cvtColor(frame,cv.COLOR_BGR2HSV) #create mask based off if a pixel's values are in between
    lower_orange = np.array([10,120,70])      #the range of lower and upper orange
    upper_orange = np.array([20,255,255])
    mask1 = cv.inRange(hsv, lower_orange, upper_orange)
     
    opixels = np.zeros(len(final)+1) #set opixels size to be the number of sections
    for i in range(0, len(final)+1):  #count how many orange pixels are in each section by using the mask
        opixels[i] = np.count_nonzero(mask1[:, int(sections[i]):int(sections[i+1])]) 
    currkey = np.argmax(opixels) #find which section has the highest amount of orange pixels
    cv.imshow('MASK', mask1)
    
    ser.flushInput() #read in current photoresistor data from arduino
    time.sleep(0.001)
    b = ser.readline()         # read a byte string
    string_n = b.decode()      # decode byte string into Unicode  
    string = string_n.rstrip() # remove \n and \r
    
    try:
        flt = float(string) #get value from photoresistor
        if flt < 100: #this means data from the buffer got cut off, so it is a throwaway value
            continue
        currpress = flt > 200 and flt < 800  #if key is pressed
        if flt > 800:  #if no key is pressed, play no sound
            winsound.PlaySound(None, winsound.SND_PURGE|winsound.SND_ASYNC)
            
        elif currpress and currpress != prevpress: #if key is pressed and wasn't previously pressed, start sound
            winsound.PlaySound(notes[str(currkey)], winsound.SND_ALIAS|winsound.SND_ASYNC|winsound.SND_LOOP)

        elif currpress and currkey != prevkey: #if key changes, then play the new sound
            winsound.PlaySound(notes[str(currkey)], winsound.SND_ALIAS|winsound.SND_ASYNC|winsound.SND_LOOP)

        else:
            pass
    except:
        pass
    
    prevkey = currkey  #update prevkey and prevpress
    prevpress = currpress
    if cv.waitKey(20) & 0xFF==ord('d'):
        break



winsound.PlaySound(None, winsound.SND_PURGE|winsound.SND_ASYNC) #stop sound and close extra windows
capture.release()
cv.destroyAllWindows()

