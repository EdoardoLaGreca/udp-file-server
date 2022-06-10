'''
matricola: 0000976628
email: edoardo.lagreca@studio.unibo.it
'''

import os
import sys
import socket
import base64

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


def print_usage() -> None:
	print("usage: python3 client.py <address> <port>")


def check_args() -> bool:
	if len(sys.argv) != 3:
		return False
	return True


def print_commands():
	print('Available commands:')
	print('list - list files in the server')
	print('get <filename> - get file from the server')
	print('put <path> - put file to the server')
	print('exit - exit the client')
	print('quit - same as exit')


def interpret_cmd(command: str) -> bytes:
	cmd = command.split(' ', maxsplit=1)
	cmd_name = cmd[0]
	request = ''

	if cmd_name == 'list':
		request = 'list'
	elif cmd_name == 'get':
		request = 'get ' + cmd[1]
	elif cmd_name == 'put':
		path = cmd[1].strip()
		file = open(path, 'rb')
		file_content = file.read()
		file.close()
		request = 'put ' + os.path.basename(path) + ' ' + str(base64.b64encode(file_content), 'utf-8')
	else:
		print('Unknown command, try again.')

	return bytes(request, 'utf-8')


def interpret_response(request: bytes, response: bytes):
	cmd = str(request, 'utf-8').split(' ')
	cmd_name = cmd[0]

	if cmd_name == 'list':
		if len(response) == 0:
			print('(empty)')
		else:
			print(response.decode('utf-8'))
	elif cmd_name == 'get':
		file = open(' '.join(cmd[1:]), 'wb')
		file.write(base64.b64decode(response))
		file.close()
	elif cmd_name == 'put':
		print(response.decode('utf-8'))
	elif cmd_name == 'error':
		print('An error occurred: ' + response.decode('utf-8'))
	else:
		print(response.decode('utf-8'))


def send_packet(packet: bytes, address: str, port: int):
	for i in range(0, len(packet), 4096):
		s.sendto(packet[i:i + 4096], (address, port))


# receive the next packet from a certain address
def receive_from_addr(address: str, length: int) -> bytes:
	while True:
		data, pkt_addr = s.recvfrom(length)
		if pkt_addr == address:
			return data


# receive a packet and return its content and the sender's address
def receive_packet() -> (bytes, str):
	chunk_size = 4096
	data, address = s.recvfrom(chunk_size)

	if len(data) == chunk_size:
		while True:
			tmp_data = receive_from_addr(address, chunk_size)
			data += tmp_data
			if len(tmp_data) < chunk_size:
				break

	return data, address


if __name__ == '__main__':
	if not check_args():
		print_usage()
		exit(1)

	address = sys.argv[1]
	port = int(sys.argv[2])

	print_commands()

	print()  # spacing

	while True:
		cmd = input('> ')
		if cmd == 'exit' or cmd == 'quit':
			break
		request = interpret_cmd(cmd)
		send_packet(request, address, port)
		response, _ = receive_packet()
		interpret_response(request, response)

	exit(0)
