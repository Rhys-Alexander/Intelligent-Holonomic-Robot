import serial

ser = serial.Serial("dev/ttyUSB0", 9600)

while True:
    data = input("Enter a word: ")
    data = data.encode("utf-8")
    ser.write(data)

    if data == "!EXIT":
        print("Disconneted from the server.")
        break

    data = ser.readline()
    data = data.decode("utf-8")
    print(f"Server: {data}")
