'''
matricola: 0000976628
email: edoardo.lagreca@studio.unibo.it
'''

import socket
import sys
import os
import base64

share_path = './share/'
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


def print_usage() -> None:
	print("usage: python3 server.py <ip> <port>")


def check_args() -> bool:
	if len(sys.argv) != 3:
		return False
	return True


def list_command() -> bytes:
	return bytes('\n'.join(os.listdir(path=share_path)), 'utf-8')


def get_command(name: str) -> bytes:
	if not os.path.isfile(share_path + name):
		raise IOError('The path does not point to a file')

	file = open(share_path + name, "rb")
	data = file.read()
	file.close()
	return base64.b64encode(data)


def put_command(name: str, content: str) -> bool:
	if os.path.exists(share_path + name) and not os.path.isfile(share_path + name):
		raise IOError('The path does not point to a file')

	file = open(share_path + name, "wb")
	file.write(base64.b64decode(content))
	file.close()
	return True


def error_pkt(message: str) -> bytes:
	return bytes('error ' + message, 'utf-8')


def interpret(packet: bytes) -> bytes:
	cmd = str(packet, 'utf-8').split(' ')

	if cmd[0] == 'list':
		try:
			return list_command()
		except Exception as e:
			return error_pkt(str(e))

	elif cmd[0] == 'get':
		cmd_arg = str(packet, 'utf-8').split(' ', maxsplit=1)[1]
		try:
			return get_command(cmd_arg)
		except Exception as e:
			return error_pkt(str(e))

	elif cmd[0] == 'put':
		name = ' '.join(cmd[1:-1])
		content = cmd[-1]
		try:
			put_command(name, content)
			return bytes('ok', 'utf-8')
		except:
			return error_pkt('put failed')
	else:
		return error_pkt('unknown command')


def send_packet(packet: bytes, address: str, port: int):
	if len(packet) == 0:
		s.sendto(packet, (address, port))

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

	print(address[0] + ': \"' + str(data, 'utf-8') + '\"')

	return data, address


if __name__ == '__main__':
	if not check_args():
		print_usage()
		exit(1)

	# create directory if it doesn't exist
	if not os.path.exists(share_path):
		os.makedirs(share_path)

	address = sys.argv[1]
	port = int(sys.argv[2])

	s.bind((address, port))

	print('server started on ' + address + ':' + str(port))

	failed = False

	while True:
		try:
			request, addr = receive_packet()
			if request:
				response = interpret(request)
				send_packet(response, addr[0], addr[1])
		except socket.error:
			failed = True
			print('socket threw an exception')
			break

	if failed:
		print('server failed to receive data')

	s.close()
	print('server closed')
	exit(0)
