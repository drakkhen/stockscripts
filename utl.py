#!/usr/bin/python

import fcntl
import os
import struct
import sys
import termios

COLORS = {
    'GRAY':         '\033[1;30m',
    'RED':          '\033[1;31m',
    'GREEN':        '\033[1;32m',
    'YELLOW':       '\033[1;33m',
    'BLUE':         '\033[1;34m',
    'MAGENTA':      '\033[1;35m',
    'CYAN':         '\033[1;36m',
    'WHITE':        '\033[1;37m',
    'CRIMSON':      '\033[1;38m',
    'HI-RED':       '\033[1;41m',
    'HI-GREEN':     '\033[1;42m',
    'HI-BROWN':     '\033[1;43m',
    'HI-BLUE':      '\033[1;44m',
    'HI-MAGENTA':   '\033[1;45m',
    'HI-CYAN':      '\033[1;46m',
    'HI-GRAY':      '\033[1;47m',
    'HI-CRIMSON':   '\033[1;48m',
    'OFF':          '\033[1;m',
}

def clear_screen():
    os.system('clear')

def get_console_size():
    s = struct.pack("HHHH", 0, 0, 0, 0)
    fd_stdout = sys.stdout.fileno()
    x = fcntl.ioctl(fd_stdout, termios.TIOCGWINSZ, s)

    #print '(rows, cols, x pixels, y pixels) =',
    #print struct.unpack("HHHH", x)
    r = struct.unpack("HHHH", x)

    return (r[0], r[1])

