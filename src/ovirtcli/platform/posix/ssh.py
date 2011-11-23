
def create_password_login_command(user, host):
    """
    Create an ssh command line.
    """
    cmd = 'ssh'
    cmd += ' -oPreferredAuthentications=password'
    cmd += ' -oStrictHostKeyChecking=no'
    cmd += ' %s@%s' % (user, host)
    return cmd
