#!/usr/bin/python

import os
import subprocess
import argparse
import datetime

try:
    from subprocess import DEVNULL # py3k
except ImportError:
    DEVNULL = open(os.devnull, 'wb')

branches = []
builders = []

def get_branch(path=None):
    if path is None:
        path = os.getcwd()

    return get_command_values(['git', 'symbolic-ref', 'HEAD'], path)[0].split('/')[2]

def run_command(cmd, path, output=None):
    if output is None:
        output = DEVNULL

    p = subprocess.Popen(cmd, cwd=path, stdout=output, stderr=output)
    p.wait()

def get_command_values(cmd, path):
    p = subprocess.Popen(cmd, cwd=path, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    r = p.communicate()
    return r[0].decode().split('\n')[:-1]

def log_command_output(cmd, path, logfile, wait=False):
    with open(logfile, 'a') as f:
        f.write('--- ' + ' '.join(cmd) + ' - ' + str(datetime.datetime.now()) + ' ---')
        p = subprocess.Popen(cmd, cwd=path, stdout=f, stderr=f)
        if wait is True:
            p.wait()

def change_branch(branch, path):
    run_command(['git', 'checkout', branch], path)
    print('[sub-repo]: checked out branch: ' + branch + ' in staging.')

def get_avalible_branches():
    current_branch = get_branch(os.getcwd())

    if current_branch not in branches:
        branches.append(current_branch)

    return branches

def branch_cleanup(path):
    extant_branches = get_command_values(['ls', '.git/refs/heads'], path)

    for branch in branches:
        if branch not in extant_branches:
            cmd = ['git', 'branch', branch, 'origin/' + branch ]
            run_command(cmd, path)
            print('[sub-repo]: created ' + branch + ' branch in staging.')

    for branch in extant_branches:
        if branch not in branches:
            run_command(['git', 'branch', '-D', branch], path)
            print('[sub-repo]: cleaned up stale branch: ' + branch)

def update_repo(path, branch='master'):
    if not os.path.isdir(path):
        cmd = ['/usr/bin/git', 'clone', './', 'build/.staging']
        run_command(cmd, os.getcwd())
        print('[sub-repo] created staging repo.')
    else:
        cmd = ['git', 'pull']
        run_command(cmd, path)
        print('[sub-repo] updated staging.')

    if not os.path.join(path, 'build'):
        os.symlink(source='../../build', link_name='build')
        print('[sub-repo] created "build/" symlink in staging.')

    branch_cleanup(path)
    change_branch(branch, path)

def build_branch(branch, path, logfile, target='publish', wait=False):
    if get_branch(path) != branch:
        change_branch(branch, path)

    cmd = ['make', target]

    print('[sub-repo]: building ' + branch + ' check log for details.')
    if wait is True:
        print('[sub-repo]: building now, waiting for the build to finish.')

    log_command_output(cmd, path, logfile, wait)
    print('[sub-repo]: build complete.')

def ui():
    targets = builders
    targets.append('publish')
    targets.append('push')
    targets.append('stage')

    build_dir = os.path.join(os.getcwd(), 'build/.staging/')
    default_log = 'build/staging-build-' + str(datetime.date.today()) + '.log'

    parser = argparse.ArgumentParser('checks out and builds current repo in "build/" directory.')
    parser.add_argument('--branch', '-b', choices=branches, default=get_branch(), help='the name of the branch to build.')
    parser.add_argument('--target', '-t', choices=targets, default='publish', help='the make target to build.')
    parser.add_argument('--logfile', '-l', default=default_log, help='a path to a logfile for make output. defaults to "' + default_log + '" .')
    parser.add_argument('--wait', '-w', default=False, action='store_true', help='wait to return until build completes if specified.')

    return parser.parse_args()

def main():
    build_dir = os.path.join(os.getcwd(), 'build/.docs-staging/')
    user = ui()

    update_repo(build_dir, branch=user.branch)
    build_branch(user.branch, build_dir, logfile=user.logfile, target=user.target, wait=user.wait)

if __name__ == '__main__':
    main()
