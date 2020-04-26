# LicensePlateDetection
First of all I'd like to say that when creating this project I didn't know about `os.system.path...` functions in python.
That is why in order for it to woek you'll need to change some paths in the main file.
### Before running 
- Open `license_plate_recongnition_v2.py` 
- Change `line 9` to the path to the photo from `/pics/` folder of this project. Or you can download any other sample image of a car 
with a __russian__ license plate on it
- Change `line 12` to the path to `plates_cascade.xml` file from this project
- Change `line 13` to the path to `\tesseract\tesseract.exe` file from this project
- Change `line 262` to the path you want the processed photo to be stored at
- Change `line 264` to the exact same path as the line 262
____
### Functionality
- Run the `license_plate_recongnition_v2.py` 
- In the console choose `1)` if you want to see all steps of processing or `2)` if you don't

The program takes a photo of a car with a __russian__ license plate on it, processes in with many different OpenCV methods and outputs
a picture of a processed license plate and the text found on it
I have to admit that the result depands on the quality of a photo very much. So try it on different photos to compare the results.
