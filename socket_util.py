import socket

def recvall(sock, message_length):
    chunks = []
    bytes_recd = 0
    while bytes_recd < message_length:
        chunk = sock.recv(min(message_length - bytes_recd, 2048))
        if chunk == b'':
            raise RuntimeError("socket connection broken")
        chunks.append(chunk)
        bytes_recd = bytes_recd + len(chunk)
    return b''.join(chunks)
