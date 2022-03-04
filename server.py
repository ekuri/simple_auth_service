# coding:utf-8

import socket
import json
import hashlib
import time
import threading

from lib.link import SOCKET_ENCODE, send_err, socket_recv_all, socket_send_all, send_ok

TOKEN_MAX_AGE_SECOND = 2.0 * 60.0 * 60.0

user_store = {}
role_store = {}
token_store = {}


def link_encrypt(password: str, salf: float):
    phash = hashlib.sha256()
    phash.update(password.encode(SOCKET_ENCODE))
    phash.update(('%f' % salf).encode(SOCKET_ENCODE))
    return phash.hexdigest()


class Role:

    def __init__(self, name: str) -> None:
        self.users = {}
        self.name = name
        pass

    def delete_user(self, username):
        self.users.pop(username, None)

    def add_user(self, user):
        if not self.users.get(user.name, None):
            self.users[user.name] = user

    def on_delete(self):
        for username, user in self.users.items():
            user.remove_role(self.name)


class Token:

    def __init__(self, token: str, born, user) -> None:
        self.token = token
        self.born = born
        self.user = user

    def invalid(self):
        self.user.remove_token()
        token_store.pop(self.token, None)

    def is_valid(self):
        t = time.time()
        return t > self.born and ((t - self.born) <= TOKEN_MAX_AGE_SECOND)


class User:

    def __init__(self, username: str, password: str) -> None:
        self.name = username
        self.salf = time.time()
        self.role = {}
        self.token = None

        self.password = link_encrypt(password, self.salf)

    def on_delete(self):
        for role_name, role_obj in self.role.items():
            role_obj.delete_user(self.name)

    def add_role(self, role_name):
        if self.role.get(role_name, None):
            return True

        role_obj = role_store.get(role_name, None)
        if not role_obj:
            return False

        role_obj.add_user(self)
        return True

    def remove_role(self, role_name):
        role_obj = self.role.get(role_name, None)
        if role_obj:
            role_obj.delete_user(self.name)

    def auth(self, password):
        challenge = link_encrypt(password, self.salf)
        if self.password != challenge:
            return None

        if self.token and self.token.is_valid():
            return self.token.token

        start_time = time.time()
        t = link_encrypt(password, time.time())
        self.token[t] = Token(t, start_time, self)
        return t

    def remove_token(self):
        self.token = None


def create_user(req):
    username = req.get('n', None)
    password = req.get('p', None)
    if not username:
        return False, 'Username should be provided'
    if not password:
        return False, 'Password should be provided'

    if user_store.get(username, None):
        return False, 'User already exist'

    user_store[username] = User(username, password)
    print('User %s created' % username)
    return True, ''


def delete_user(req):
    username = req.get('n', None)
    if not username:
        return False, 'Username should be provided'

    if user_store.get(username, None):
        user = user_store.pop(username)
        user.on_delete()
        return True, ''

    return False, 'User do not exist'


def create_role(req):
    role = req.get('r', None)
    if not role:
        return False, 'Role name should be provided'

    if role_store.get(role, None):
        return False, 'Role already exist'

    role_store[role] = []
    print('Role %s created' % role)
    return True, ''


def delete_role(req):
    role = req.get('r', None)
    if not role:
        return False, 'Role name should be provided'

    role_obj = role_store.get(role, None)
    if not role_obj:
        return False, 'Role do not exist'

    role_obj.on_delete()
    return True, ''


def attach_role(req):
    username = req.get('n', None)
    if not username:
        return False, 'Username should be provided'
    role = req.get('r', None)
    if not role:
        return False, 'Role name should be provided'

    user = user_store.get(username, None)
    if not user:
        return False, 'User do not exist'

    status = user.add_role(role)
    if status:
        return True, ''

    return False, 'Role do not exist'


def auth(req):
    username = req.get('n', None)
    password = req.get('p', None)
    if not username:
        return False, 'Username should be provided'
    if not password:
        return False, 'Password should be provided'

    user = user_store.get(username, None)
    if not user:
        return False, 'User do not exist'

    token = user.auth(password)
    if token:
        return True, 'token is %s' % token

    return False, 'Invalid password'


def token_invalid(req):
    token = req.get('t', None)
    if not token:
        return False, 'token should be provided'

    token_obj = token_store.get(token, None)
    if token_obj:
        token_obj.invalid()

    return True, ''


def check_role(req):
    token = req.get('t', None)
    if not token:
        return False, 'token should be provided'
    role = req.get('r', None)
    if not role:
        return False, 'role should be provided'

    token_obj = token_store.get(token)
    if not token_obj:
        return False, 'Invalid token'

    if not token_obj.is_valid():
        token_obj.invalid()
        return False, 'Invalid token'

    if token_obj.user.role.get(role, None):
        return True, 'Role is associated'

    return False, 'Role is not associated'


def query_role(req):
    token = req.get('t', None)
    if not token:
        return False, 'token should be provided'

    token_obj = token_store.get(token)
    if not token_obj:
        return False, 'Invalid token'

    if not token_obj.is_valid():
        token_obj.invalid()
        return False, 'Invalid token'

    return True, 'User role: %s' % ','.join(token.user.role.keys())


cmd_handle = {
    'create_user': create_user,
    'delete_user': delete_user,
    'create_role': create_role,
    'delete_role': delete_role,
    'attach_role': attach_role,
    'auth': auth,
    'invalid': token_invalid,
    'chk_role': check_role,
    'query_role': query_role
}


def handle_client(client_socket: socket.socket):
    req_data = socket_recv_all(client_socket)
    req_data = json.loads(req_data)
    print("request data:", req_data)

    cmd = req_data.get('cmd', None)
    handle = cmd_handle.get(cmd, None)
    if not handle:
        send_err(client_socket, 'Not such action')
        return

    status, msg = handle(req_data)
    print(status)
    if status:
        send_ok(client_socket, msg)
    else:
        send_err(client_socket, msg)

    client_socket.close()


if __name__ == "__main__":
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(("", 8000))
    server_socket.listen(128)

    while True:
        client_socket, client_address = server_socket.accept()
        print("[%s, %s] connected" % client_address)
        hdl_t = threading.Thread(
            target=handle_client, args=(client_socket,))
        hdl_t.start()
