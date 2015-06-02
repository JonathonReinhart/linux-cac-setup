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
            if v:
                s += '  {0}: {1}\n'.format(k, v)
        return s

    def __getitem__(self, k):
        k = k.lower()
        return self.attrs[k]

    def __setitem__(self, k, v):
        k = k.lower()
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
            if curtok:
                tokens.append(curtok)
            curtok = Token(int(m.group(1)))
            continue

        # Nope, keep adding to current token
        k,v = line.split(':', 1)
        v = v.strip()
        curtok[k] = v

    if curtok:
        tokens.append(curtok)

    return tokens

def input_int(prompt):
    while True:
        res = raw_input(prompt)
        if res:
            try:
                return int(res)
            except ValueError:
                print 'Invalid input'



def main():
   
    print 'Finding hardware tokens...'
    hw_tokens = [t for t in get_tokens() \
                 if t['type'] == 'Hardware token']

    if not hw_tokens:
        print 'No hardware tokens found.'
        print 'Is your reader connected and smart card inserted?'
        return 1

    print 'Select the hardware token that is your CAC:'
    for t in hw_tokens:
        print t

    while True:
        tokn = input_int('Token #? ')

        for t in hw_tokens:
            if t.id == tokn:
                break
        else:
            print 'No hardware token by that number'
            continue
        token = t
        break

    print 'Selected: '
    print token



    return 0

    

if __name__ == '__main__':
    try:
        rc = main()
    except KeyboardInterrupt:
        rc = 33
    sys.exit(rc)
