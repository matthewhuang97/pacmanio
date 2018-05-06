import socket

def recvall(sock, message_length):
    chunks = []
    bytes_received = 0
    while bytes_received < message_length:
        chunk = sock.recv(min(message_length - bytes_received, 2048))
        if chunk == b'':
            raise RuntimeError("socket connection broken")
        chunks.append(chunk)
        bytes_received = bytes_received + len(chunk)
    return b''.join(chunks)
