# Intelligent Holonomic Robot

https://user-images.githubusercontent.com/54585720/228057465-ab6f09dc-bda7-4561-ab9f-450bd0d2d0cd.mov

https://user-images.githubusercontent.com/54585720/228053104-ffe0973a-ddcf-4789-9422-15cd4c7ff1fc.mp4

## Tracker
Computer Vision Program "detection.py":
- finds the 2d arena where the robot maneuvers
- finds the robot an enemy locations and rotations in the 2d plane while accounting for height
- finds the item's and their locations in the 2d plane while accounting for their height
 
Pathfinding Algorithms "pathfinder.py":
- creates graph of all possible paths, not allowing paths through enemies
- weighs paths by length and distance to enemies
- gets best possible path
- generates X, Y, and rotaion velocities relative to the rotation of the robot which are porportional to the distance from the robot

Algorithm Visualiser "visualiser.py":
- visualises all items in sight
- displays robot rotation
- displays the X, Y, and rotation velocity being given to the robot

Client Program "main.py"
- connects to the robot
- runs all appropriate code in order to instruct the robot

## Bot
Raspberry Pi Server "server.py"
- receives instructions from tracker
- sends instructions to onboard arduino

## Arduino
Omniwheel Motor Control "arduino.py"
- receives instructions from the raspberry pi
- calculates holonomic drive
- controls the motors with appropriate accelaration
