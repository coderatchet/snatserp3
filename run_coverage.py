#!/bin/env/python

import os

from subprocess import Popen, PIPE, STDOUT

if __name__ == '__main__':
    if 'TRAVIS' in os.environ and 'TRAVIS_PYTHON_VERSION' in os.environ and os.environ['TRAVIS_PYTHON_VERSION'] == '3.5':
        rc = Popen(['coverage', 'run', '--source=prestans3', '--rcfile', os.path.expandvars('${envdir}/.coveragerc'), 'python', os.path.expandvars('${toxinidir}/setup.py'), 'test'], stdout=PIPE, stderr=STDOUT)
        while True:
            line = rc.stdout.readline()
            if not line:
                break
            print(line)
        raise SystemExit(rc)
