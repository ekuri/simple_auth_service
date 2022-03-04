# simple_auth_service

## Requirements

- Python3

## Usage

### Server side

```bash
python3 server.py
```

### Client Side

Base Usage is
``` bash
python3 client.py [action] [param]
```

Can use following command to show what we support
``` bash
python3 client.py -h
```

Sub-command usage:
``` bash
python3 client.py [action] -h
```

Following actions are supported
- create_user: create a user
- delete_user: delete a user
- create_role: create a role
- delete_role: delete a role
- attach_role: attach a role to user
- auth: authenticate user
- invalid: invalidate user token
- chk_role: check user role
- query_role: query all user role(s)

## Unit Test

1. Start server
```bash
python3 server.py
```
2. Run UT script
```bash
python3 ut.py
```

## Machanism

### Overroll Arch:

Client ---> JSON on tcp socket ---> Server

### Server password encrypt

sha256 of origin password and time as saft
