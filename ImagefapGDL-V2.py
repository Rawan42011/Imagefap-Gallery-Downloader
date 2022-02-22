#----------------------- LIBRARIES --------------------------
import os               # OS interaction
from os import system, name
import urllib.request
import urllib.parse
import re               # use regular expresssions
import sys
import time
import concurrent.futures
from itertools import cycle
from time import sleep

#----------------------- GLOBAL VARIABLES -------------------
myURL = ""              # Friendly Name URL (user input)
myPATH = ""             # Custom Save Path (default is same location as py-script)
prURL = ""              # Processed URL with gid & view parameters
imgnames = []           # List of all original jpg names with file extention
imgURLs = []            # List of all URLs to HD jpg files with file extention
galleryName = ""
ghtml = ""              # gHTML = HTML code of full gallery
gfirstrun = True
errCount = 0           # Total amount of errors
imgIDlist =[]

def mainLoop():
    global myURL, galleryName, gfirstrun, ghtml

    ## HEADER ##
    displayHeader() ; gfirstrun = False 

    # FASE 1: GET HTML OF SINGLE-PAGE GALLERY #
    # also fills in the globals ghtml and galleryName
    myURL = urllib.parse.unquote(input("Please input the gallery url [Press Q to Quit]: "))              
    quit(0) if myURL.lower() == "q" else discoverGallery(myURL) 

    # FASE 2: GET/SET PATH & CREATE FOLDER #
    setPath()                                                                                   
                                                               
    # FASE 3: GET ALL LINKS TO PAGES OF HI_RES IMAGES
    imgIDlist = getImageURLList()

    # FASE 4: SCRUB ALL IMAGE-HTML FOR THE NAME AND PRECISE HD-IMAGELINK
    print("[", end="" )
    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(discoverImage, imgIDlist )
    print("]" )
    print("[INFO] "+ str(len(imgIDlist))+ " images discovered & downloaded.")

    finish()


def discoverImage(image):
    global imgIDlist, galleryName, myPATH
    last_msg_length = 0
    ihtml =  urllib.request.urlopen(image).read() # iHTML = HTML code image-page with link to HD version
    imgname = re.findall(b'<title>([a-zA-Z0-9_-]+[.jpg|.JPG|.jpeg|.GIF|.gif|.PNG|.png]+) Porn Pic', ihtml)[0]
    imgURL = re.findall(b'"contentUrl": "(.*?)",', ihtml)[0]
    with urllib.request.urlopen(imgURL.decode('UTF-8')) as f:
        imageContent = f.read()
        if myPATH != "":
            with open(myPATH + '/' + galleryName + '/' + str(imgname.decode('UTF-8')), "wb") as f:
                f.write(imageContent)
        else:
            with open(galleryName + '/' + str(imgname.decode('UTF-8')), "wb") as f:
                f.write(imageContent)

    print(".", end="" )
    
def displayHeader():
    if (gfirstrun == True): 
        print("")
        print(" ___                      __             ___                  _              _         ")
        print("|_ _|_ __  __ _ __ _ ___ / _|__ _ _ __  |   \ _____ __ ___ _ | |___  __ _ __| |___ _ _ ")
        print(" | || '  \/ _` / _` / -_)  _/ _` | '_ \ | |) / _ \ V  V / ' \| / _ \/ _` / _` / -_) '_|")
        print(" |__|_|_|_\__,_\__, \___|_| \__,_| .__/ |___/\___/\_/\_/|_||_|_\___/\__,_\__,_\___|_|  ")
        print("               |___/             |_|                                                   ")
        print("")
        print("")
    else:
        print("")

def discoverGallery(URL):
    global galleryName, ghtml
    print("Processing GALLERY.....................................", end="", flush=True)
    #Step 1: Check if valid url
    if (URL.find("https://www.imagefap.com/pictures/") == -1): 
        print("[ERROR IN URL]" ) 
        cleanup()
    #Step 2: Get Name of Gallery : Takes the input URL and removes everything before the \ and after the ?
    galleryName = str(URL).split("/")[-1].split("?", 1)[0]
    #Step 3: Acquire HTML of 1-page-gallery page
    ghtml =  urllib.request.urlopen(onePageURL(URL)).read()
    #Step 4: Count all link-names on page
    count = 0 
    for match in re.finditer('<td id="([0-9]+)" align="center"  ?valign="top">', str(ghtml)): count +=1
    #Step 4: Display galleryname and imagecount 
    print("[SUCCESS: Found \"" + galleryName + "\" with " + str(count) + " images]")

def setPath():
    global galleryName, myPATH
    myPATH = urllib.parse.unquote(input("Please input save location [Press Enter for default] : "))
    if myPATH == "": 
        print("[INFO] Saving to default location: " + os.getcwd())
        myPATH = os.getcwd()
    else:
        print("[INFO] Saving to custom location: " + myPATH)

    print("Creating DIRECTORY.....................................", end="", flush=True)
    path = os.path.join(myPATH, galleryName)
    try:
        os.mkdir(path) ; print("[SUCCESS]")
    except:
        if os.path.isdir(path) == True: print("[DIRECTORY ALREADY EXISTS]")
        print ("[Info] This gallery seems to exsist already. Please choose a different location.")
        cleanup()
    
def onePageURL(URL):
    # DEPENDS ON discoverGallery(URL)
    # Uses the input url to find the one-page view (used in discoverGallery() )
    # e.g. changes https://www.imagefap.com/pictures/8493380/Lola-Myluv-%28Dido-Angel%29-76.?gid=8493380&page=0&view=0 
    # into https://www.imagefap.com/pictures/8493380/?gid=8493380&view=2
    url = "https://www.imagefap.com/pictures/"
    galleryId = URL.replace(url,"") 
    galleryId = galleryId.split("/")[0] 
    prURL = "{}{}/?gid={}&view=2".format(url, galleryId, galleryId)
    return prURL

def getImageURLList():
    global ghtml, imgIDlist
    lead = "Discovering HI-RES IMAGE URLs........"
    last_msg_length = 0
    #Get All HTML URLs of Hi-res-images (FUll Page)
    imgIDlist = re.findall('<td id="([0-9]+)" align="center"  ?valign="top">', str(ghtml))
    for i in range(len(imgIDlist)):
        imgIDlist[i] =  "https://www.imagefap.com/photo/"+imgIDlist[i]+"/"
    return imgIDlist

def finish():
    global  errCount
    if errCount>0: print(str(errCount) + " image(s) could not be downloaded.")
    print("All Done. Happy Fapping :-)")
    cleanup()
          
def cleanup():
    global myURL, prURL, galleryName, ghtml, imglist, imgnames, imgURLs, errCount
    errCount=0
    myURL, prURL, galleryName, ghtml = " " * 4             
    imglist, imgnames, imgURLs = [], [], []         
    mainLoop()

mainLoop()
