import serial
import time
import socket

# Run on Boot
# Change this to your raspeberry pi's IP address
HOST = "10.42.0.1"
PORT = 5005

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind((HOST, PORT))

with serial.Serial("/dev/ttyUSB0", 500000, timeout=1) as arduino:
    time.sleep(0.1)  # wait for serial to open
    if arduino.isOpen():
        print("{} connected!".format(arduino.port))
        while True:
            data, addr = server.recvfrom(1024)
            arduino.write(data)
            while arduino.inWaiting() > 0:
                answer = arduino.readline()
                time.sleep(0.01)
            arduino.flushInput()  # remove data after reading
