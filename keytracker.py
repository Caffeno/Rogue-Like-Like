#!/usr/bin/env python3

import os
import time

# Windows
if os.name == 'nt':
    import msvcrt

# Posix (Linux, OS X)
else:
    import sys
    import termios
    import atexit
    from select import select


class KBHit:

    def __init__(self):
        '''Creates a KBHit object that you can call to do various keyboard things.
        '''

        if os.name == 'nt':
            pass

        else:
            # Save the terminal settings
            self.fd = sys.stdin.fileno()
            self.new_term = termios.tcgetattr(self.fd)
            self.old_term = termios.tcgetattr(self.fd)

            # New terminal setting unbuffered
            self.new_term[3] = (self.new_term[3] & ~termios.ICANON & ~termios.ECHO)
            termios.tcsetattr(self.fd, termios.TCSAFLUSH, self.new_term)

            # Support normal-terminal reset at exit
            atexit.register(self.set_normal_term)


    def set_normal_term(self):
        ''' Resets to normal terminal.  On Windows this is a no-op.
        '''

        if os.name == 'nt':
            pass

        else:
            termios.tcsetattr(self.fd, termios.TCSAFLUSH, self.old_term)


    def getch(self):
        ''' Returns a keyboard character after kbhit() has been called.
            Should not be called in the same program as getarrow().
        '''

        s = ''

        if os.name == 'nt':
            return msvcrt.getch().decode('utf-8')

        else:
            return sys.stdin.read(1)


    def kbhit(self):
        ''' Returns True if keyboard character was hit, False otherwise.
        '''
        if os.name == 'nt':
            return msvcrt.kbhit()

        else:
            dr,dw,de = select([sys.stdin], [], [], 0)
            return dr != []


    def process_keystroke(self):
        key = None                         #Default value to return when untracked key was pressed (Such as function keys)
        c1 = self.getch()                  #These other keys can be added if needed, otherwise they are not relivent to current project
        if ord(c1) == 32:
            key = 'space'
        elif ord(c1) != 27:
            key = '{}'.format(c1)
        else:
            c2 = self.getch()
            if not c2:
                print('no next key')
                key = 'esc'
            else:
                c3 = self.getch()
                if not c3:
                    return
                else:
                    if ord(c3) == 65:
                        key = 'up'
                    elif ord(c3) == 66:
                        key = 'down'
                    elif ord(c3) == 67:
                        key = 'right'
                    elif ord(c3) == 68:
                        key = 'left'
        if key:
            return key
        
    def check_input(self):
        key_pressed = self.kbhit()         #Boolean check to see if there is a key press to return
        if key_pressed:
            key = self.process_keystroke() #getting the key pressed by the user
            return key                         #None incicates a key that isn't being tracked
        else:
            return None

if __name__ == "__main__":
    kb = KBHit()
    print('init')
    st = time.time()
    while True:
        now = time.time()
        if now - st > 1:
            print('tick')
            st = now
        key = kb.check_input()
        if key:
            print("a print of {}".format(key))
            print(len(key))
            print(ord(key))
