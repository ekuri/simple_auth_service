from http.client import REQUEST_HEADER_FIELDS_TOO_LARGE
import socket
import json

REQUEST_HEADER_MAX = 16
REQ_RECV_BUFF = 1024
MAX_REQ_CHUNK = 16
SOCKET_ENCODE = 'utf-8'
OK_CODE = 'OK'
ERR_CODE = 'ERR'


def socket_send_all(sock: socket.socket, msg: str):
    head = '%d ' % len(msg)
    if len(head) > REQUEST_HEADER_MAX:
        print("Send too large: %d" % len(msg))
        return
    sock.sendall(head.encode(SOCKET_ENCODE))
    sock.sendall(msg.encode(SOCKET_ENCODE))


def socket_recv_all(sock: socket.socket, err_send=False):
    req_data = []
    req_seq = REQUEST_HEADER_MAX
    while req_seq > 0:
        data = sock.recv(1)
        # print(data)
        if not data:
            req_seq = 0
            break
        if data == b' ':
            break
        req_data.append(data)
        req_seq -= 1
    if req_seq <= 0:
        if err_send:
            send_err(sock, 'Invalid req')
        return ''

    # print(req_data)
    req_data = bytes().join(req_data)
    req_length = int(req_data.decode(SOCKET_ENCODE))
    # print('Req length: %d' % req_length)

    req_data = sock.recv(req_length)
    return req_data.decode(SOCKET_ENCODE)


def send_err(sock: socket.socket, msg: str):
    socket_send_all(sock, json.dumps(
        {'status': ERR_CODE, 'msg': msg}))


def send_ok(sock: socket.socket, msg: str):
    socket_send_all(sock, json.dumps(
        {'status': OK_CODE, 'msg': msg}))


def decode_rsp(r: str):
    rsp = json.loads(r)
    status = rsp.get('status', False)
    msg = rsp.get('msg', '')
    return status, msg
