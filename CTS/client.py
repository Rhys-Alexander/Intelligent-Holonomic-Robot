import socket

if __name__ == "__main__":
    host = "10.42.0.1"
    port = 5005
    addr = (host, port)

    """ Creating the UDP socket """
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    while True:
        data = input("Enter a word: ")
        data = data.encode()
        client.sendto(data, addr)
        if data == "!EXIT":
            print("Disconneted from the server.")
            break
        data, addr = client.recvfrom(1024)
        data = data.decode()
        print(f"Server: {data}")
