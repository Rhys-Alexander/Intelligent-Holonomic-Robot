import serial
import time
import socket

host = "10.42.0.1"
port = 5005

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind((host, port))

print("Running. Press CTRL-C to exit.")
with serial.Serial("/dev/ttyUSB0", 115200, timeout=1) as arduino:
    time.sleep(0.1)  # wait for serial to open
    if arduino.isOpen():
        print("{} connected!".format(arduino.port))
        try:
            while True:
                data, addr = server.recvfrom(1024)
                data = data.decode()
                arduino.write(data.encode())
                while arduino.inWaiting() == 0:
                    pass
                while arduino.inWaiting() > 0:
                    answer = arduino.readline()
                    print("arduino:", answer.decode())
                    time.sleep(0.01)
                data = "finsihed"
                data = data.encode()
                server.sendto(data, addr)
                arduino.flushInput()  # remove data after reading
        except KeyboardInterrupt:
            print("KeyboardInterrupt has been caught.")
