#----------------------- LIBRARIES --------------------------
import os               # OS interaction
from os import system, name
import urllib.request
import urllib.parse
import re               # use regular expresssions
import sys
import time

#----------------------- GLOBAL VARIABLES -------------------
myURL = ""              # Friendly Name URL (user input)
prURL = ""              # Processed URL with gid & view parameters
imglist = []            # List of all numerical jpg names without file extention
imgnames = []           # List of all original jpg names with file extention
imgURLs = []            # List of all URLs to HD jpg files with file extention
galleryName = ""
ghtml = ""              # gHTML = HTML code of full gallery
gfirstrun = True
errCount = 0           # Total amount of errors

def mainLoop():
    global myURL, galleryName, gfirstrun
    displayHeader() 
    gfirstrun = False   
    #Getting Info
    myURL = urllib.parse.unquote(input("Please input the gallery url: "))
    processGALLERY(myURL)
    #DoStuff
    createFolder(galleryName)
    getImageURLS(prURL)
    download(imgURLs)
    finish()

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


def processGALLERY(URL):
    global galleryName, ghtml, imglist
    print("Processing GALLERY...................", end="", flush=True)
    #Step 0: Check if valid url
    if (URL.find("https://www.imagefap.com/pictures/") == -1): 
        print("[ERROR IN URL]" )
        retry()
    #Step 1: Get Name of Gallery
    galleryName = getGalleryName(URL)
    #Step 2: Acquire HTML of gallery page
    ghtml =  urllib.request.urlopen(processURL(URL)).read() # gHTML = HTML code of gallery
    #Step 3: Find all Hi-Res images links on page
    imglist = re.findall('<td id="([0-9]+)" align="center"  ?valign="top">', str(ghtml))
    print("[SUCCESS: Found \"" + galleryName + "\" with " + str(len(imglist)) + " images]")
    return

def createFolder(DIRNAME):
    dir_name = DIRNAME
    print("Creating DIRECTORY...................", end="", flush=True)
    try:
        os.mkdir(dir_name)
        print("[SUCCESS]")
    except:
        if os.path.isdir(dir_name) == True: 
            print("[DIRECTORY ALREADY EXISTS]")
        else:
            print("[FAILURE]")
        return

def getGalleryName(URL):
    # Takes the input URL and removes everything before the \ and after the ?
    gName = str(URL).split("/")[-1].split("?", 1)[0]
    return gName

def processURL(URL):
    # Uses the input url to find the one-page view 
    # e.g. changes https://www.imagefap.com/pictures/8493380/Lola-Myluv-%28Dido-Angel%29-76.?gid=8493380&page=0&view=0 
    # into https://www.imagefap.com/pictures/8493380/?gid=8493380&view=2
    url = "https://www.imagefap.com/pictures/"
    galleryId = URL.replace(url,"") 
    galleryId = galleryId.split("/")[0] 
    prURL = "{}{}/?gid={}&view=2".format(url, galleryId, galleryId)
    return prURL

def getImageURLS(html):
    # Fills the imgURLs list with all links to hi-res images, based on the info in the imglist
    # Fills the imgnames list with all original names of the images
    global imglist, imgnames, imgURLs
    lead = "Discovering HI-RES IMAGE URLs........"
    last_msg_length = 0
    for image in imglist:
        url = "https://www.imagefap.com/photo/{}/".format(image)
        ihtml =  urllib.request.urlopen(url).read() # iHTML = HTML code image-page with link to HD version
        imgnames.append(re.findall('<title>([a-zA-Z0-9_-]+[.jpg|.JPG|.jpeg|.GIF|.gif|.PNG|.png]+) Porn Pic', str(ihtml)))
        imgURLs.append(re.findall('"contentUrl": "(.*?)",', str(ihtml)))
        if last_msg_length != 0: print(' ' * last_msg_length, end='\r')
        output = lead+"{} of {}".format(str(len(imgURLs)), str(len(imglist))) + " : " + str(imgnames[-1])[2:-2]
        last_msg_length = len(output)
        print(output, end='\r')
        #sys.stdout.flush()
    if last_msg_length != 0: print(' ' * last_msg_length, end='\r')
    print(lead+"[SUCCES]")
    sys.stdout.flush()
    return

def download(ImgURLs):
    # Loops through the imgURLs and imgnames lists to save the numerically named hi-res image with the original filename
    global imgnames, errCount
    lead = "Downloading HI-RES IMAGES............"
    last_msg_length = 0
    x=0
    for image in ImgURLs:
        image = str(image[0])
        name = str(imgnames[x])[2:-2]
        try:
             with urllib.request.urlopen(image) as f:
                imageContent = f.read()
                with open(galleryName + '/' + name, "wb") as f:
                    f.write(imageContent)
        except:
           print("[Error]", end='\r')
           errCount+=1
        if last_msg_length != 0: print(' ' * last_msg_length, end='\r')
        output = lead+"{} of {}".format(str(x+1), str(len(imglist))) + " : " + str(imgnames[x])[2:-2]
        last_msg_length = len(output)
        print(output, end='\r')
        #sys.stdout.flush()
        x=x+1
    if last_msg_length != 0: print(' ' * last_msg_length, end='\r')
    print(lead+"[SUCCES]")
    sys.stdout.flush()
    x=0
    return
 
def finish():
    global  errCount
    if errCount>0: print(str(errCount) + " image(s) could not be downloaded.")
    print("All Done. Happy Fapping :-)")
    retry()

def retry():
    response = input("Wanna do some more? [Y/N]: ")
    if response.lower() == "y": cleanup()
    elif response.lower() == "n": sys.exit()
    else: print("Bruh. Not a valid response."); retry()

           
def cleanup():
    global myURL, prURL, galleryName, ghtml, imglist, imgnames, imgURLs, errCount
    errCount=0
    myURL, prURL, galleryName, ghtml = " " * 4             
    imglist, imgnames, imgURLs = [], [], []         
    mainLoop()

mainLoop()
