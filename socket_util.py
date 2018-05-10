import socket

def recvall(sock, message_length):
	"""Version of socket.recv that loops until entire message is received.

	Args:
		sock: socket object on which to wait for message
		message_length: how many bytes to receive

	Returns:
		Bytes, in total message_length.
	"""
    chunks = []
    bytes_received = 0
    while bytes_received < message_length:
        chunk = sock.recv(min(message_length - bytes_received, 2048))
        if chunk == b'':
            raise RuntimeError("socket connection broken")
        chunks.append(chunk)
        bytes_received = bytes_received + len(chunk)
    return b''.join(chunks)
