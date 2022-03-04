# coding:utf-8

import subprocess

def run_expect(cmd, expected):
    cmd = 'python3 client.py %s' % cmd
    print('Running: %s' % cmd)
    try:
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
        output = output.decode('utf-8')
    except subprocess.CalledProcessError as e:
        print('-> [Failed]: %s' % e.output)
        raise RuntimeError('Test Failed')

    output = output.strip('\n')
    if output[:len(expected)] == expected:
        print('-> [Success]')
        # print('-> [Success]: %s' % output)
    else:
        print('-> [Failed]')
        # print('-> [Failed]: %s' % output)
        raise RuntimeError('Test Failed')

    return output

def run_expect_ok(cmd):
    return run_expect(cmd, 'OK')

def run_expect_failed(cmd):
    return run_expect(cmd, 'ERR')

def get_token(output: str):
    idx_start = len('OK: token is ')
    return output[idx_start:idx_start + 64]

def base_case():
    # base function
    run_expect_ok('create_user -n ekuri -p asd')
    run_expect_ok('create_role -r admin')
    run_expect_ok('attach_role -n ekuri -r admin')
    token = run_expect_ok('auth -n ekuri -p asd')
    token = get_token(token)
    print("Capture token: %s" % token)
    run_expect_ok('chk_role -t %s -r admin' % token)
    query_output = run_expect_ok('query_role -t %s' % token)
    if query_output == 'OK: User role: [admin]':
        print('-> Query OK')

    run_expect_ok('invalid -t %s' % token)
    run_expect_ok('delete_role -r admin')
    run_expect_ok('delete_user -n ekuri')

def user_case():
    run_expect_ok('create_user -n ekuri -p asd')
    run_expect_failed('create_user -n ekuri -p asd')
    run_expect_failed('create_user -n ekuri -p asda')
    run_expect_failed('delete_user -n ekur0')
    run_expect_ok('delete_user -n ekuri')
    run_expect_failed('delete_user -n ekuri')


def role_case():
    run_expect_ok('create_role -r admin')
    run_expect_failed('create_role -r admin')
    run_expect_failed('delete_role -r admin1')

    run_expect_ok('create_user -n ekuri -p asd')
    run_expect_ok('attach_role -n ekuri -r admin')
    run_expect_failed('attach_role -n ekuri -r admin0')
    run_expect_failed('attach_role -n ekuri0 -r admin')

    run_expect_ok('delete_role -r admin')
    run_expect_failed('delete_role -r admin')

    run_expect_ok('delete_user -n ekuri')


def token_case():
    run_expect_ok('create_user -n ekuri -p asd')
    token = run_expect_ok('auth -n ekuri -p asd')
    token = get_token(token)
    print("Capture token: %s" % token)
    exp_token = run_expect_failed('auth -n ekuri -p asda')
    exp_token = run_expect_failed('auth -n ekuro -p asd')
    exp_token = run_expect_ok('auth -n ekuri -p asd')
    exp_token = get_token(exp_token)
    if exp_token != token:
        raise RuntimeError("Test Failed")
    run_expect_ok('invalid -t %s' % token)
    run_expect_ok('invalid -t %s' % token)
    token = run_expect_ok('auth -n ekuri -p asd')
    token = get_token(token)
    print("Capture token: %s" % token)
    if exp_token == token:
        raise RuntimeError("Test Failed")

    run_expect_ok('create_role -r admin')
    run_expect_ok('attach_role -n ekuri -r admin')
    run_expect_ok('chk_role -t %s -r admin' % token)
    query_output = run_expect_ok('query_role -t %s' % token)
    if query_output == 'OK: User role: [admin]':
        print('-> Query OK')

    # delete role to delete user role
    run_expect_ok('delete_role -r admin')
    run_expect_failed('chk_role -t %s -r admin' % token)
    query_output = run_expect_ok('query_role -t %s' % token)
    if query_output == 'OK: User role: []':
        print('-> Query OK')

    run_expect_ok('delete_user -n ekuri')

if __name__ == "__main__":
    base_case()
    user_case()
    role_case()
    token_case()
