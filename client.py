# coding:utf-8
import socket
import argparse
import json


def CreateArgParse():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help='sub-command help', dest='cmd')

    # user create
    sub_parser = subparsers.add_parser('create_user', help='create a user')
    sub_parser.add_argument('-n', type=str, help='username', required=True)
    sub_parser.add_argument('-p', type=str, help='password', required=True)

    # user delete
    sub_parser = subparsers.add_parser('delete_user', help='delete a user')
    sub_parser.add_argument('-n', type=str, help='username', required=True)

    # role create
    sub_parser = subparsers.add_parser('create_role', help='create a role')
    sub_parser.add_argument('-r', type=str, help='role name', required=True)

    # role delete
    sub_parser = subparsers.add_parser('delete_role', help='delete a role')
    sub_parser.add_argument('-r', type=str, help='role name', required=True)

    # role attach to user
    sub_parser = subparsers.add_parser(
        'attach_role', help='attach a role to user')
    sub_parser.add_argument('-n', type=str, help='username', required=True)
    sub_parser.add_argument('-r', type=str, help='role name', required=True)

    # auth
    sub_parser = subparsers.add_parser(
        'auth', help='authenticate user')
    sub_parser.add_argument('-n', type=str, help='username', required=True)
    sub_parser.add_argument('-p', type=str, help='password', required=True)

    # token invalid
    sub_parser = subparsers.add_parser(
        'invalid', help='invalidate user token')
    sub_parser.add_argument('-t', type=str, help='user token', required=True)

    # check role
    sub_parser = subparsers.add_parser(
        'chk_role', help='check user role')
    sub_parser.add_argument('-t', type=str, help='user token', required=True)
    sub_parser.add_argument('-r', type=str, help='user role', required=True)

    # query all roles
    sub_parser = subparsers.add_parser(
        'query_role', help='query all user role(s)')
    sub_parser.add_argument('-t', type=str, help='user token', required=True)

    return parser


if __name__ == "__main__":
    parser = CreateArgParse()
    args = parser.parse_args()
    req_data = json.dumps(args.__dict__)

    # send to server
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('localhost', 8000))

    client.sendall(req_data.encode('utf-8'))
    client.close()
