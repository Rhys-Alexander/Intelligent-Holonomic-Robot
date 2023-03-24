import serial
import time


print("Running. Press CTRL-C to exit.")
with serial.Serial("/dev/ttyUSB0", 115200, timeout=1) as arduino:
    time.sleep(0.1)  # wait for serial to open
    if arduino.isOpen():
        print("{} connected!".format(arduino.port))
        try:
            while True:
                cmd = input("Enter command : ") + "\n"
                arduino.write(cmd.encode())
                while arduino.inWaiting() == 0:
                    pass
                while arduino.inWaiting() > 0:
                    answer = arduino.readline()
                    print(answer.decode())
                    time.sleep(0.01)
                arduino.flushInput()  # remove data after reading
        except KeyboardInterrupt:
            print("KeyboardInterrupt has been caught.")
