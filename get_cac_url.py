#!/usr/bin/env python
import sys
import subprocess
import re

class Token(object):
    def __init__(self, id):
        self.attrs = {}
        self.id = id

    def __str__(self):
        s = 'Token {0}:\n'.format(self.id)
        for k,v in self.attrs.iteritems():
            s += '  {0}: {1}\n'.format(k, v)
        return s

    def add_attr(self, k, v):
        if k in self.attrs:
            raise ValueError('Key {0} already exists'.format(k))
        self.attrs[k] = v

def get_tokens():
    p = subprocess.Popen(
            args = ['p11tool','--list-tokens'],
            stdout = subprocess.PIPE)

    tokens = []
    curtok = None
    for line in p.stdout:
        line = line.strip()
        if not line: continue

        # New token?
        m = re.match('^Token (\d+)', line)
        if m:
            tokens.append(curtok)
            curtok = Token(int(m.group(1)))
            continue

        # Nope, keep adding to current token
        k,v = line.split(':', 1)
        curtok.add_attr(k, v)


    return tokens


        
        


def main():
    for t in get_tokens():
        print t
    return 0

if __name__ == '__main__':
    sys.exit(main())
