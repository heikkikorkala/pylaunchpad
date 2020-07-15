import numpy as np
import mido
from time import sleep

msg = mido.Message('note_on', note=60)

ports = mido.get_output_names()

launchpad = ports[0]

print(launchpad)

port = mido.open_output(launchpad)


n_rows = 8
n_columns = 9

b = np.zeros((n_rows, n_columns), dtype=int)

def notenum(r, c):
    return r*16+c

def notecoor(num):
    c = num % 16
    r = (num-c) / 16
    return (int(r), int(c))


def gametick(bo):
    print("gametick")
    bn = np.zeros((n_rows, n_columns), dtype=int)

    for r in range(n_rows):
        for c in range(n_columns):
            n = 0

            if r-1 >= 0:
                n = n + bo[r-1, c]
                
            if r+1 < n_rows:
                n = n + bo[r+1, c]
            
            if c-1 >= 0:
                n = n + bo[r, c-1]    

            if c+1 < n_columns:
                n = n + bo[r, c+1]

            if r-1 >= 0 and c-1 >= 0:
                n = n + bo[r-1, c-1]

            if r-1 >= 0 and c+1 < n_columns:
                n = n + bo[r-1, c+1]

            if r+1 < n_rows and c-1 >= 0:
                n = n + bo[r+1, c-1]

            if r+1 < n_rows and c+1 < n_columns:
                n = n + bo[r+1, c+1]
           

            if n > 3:
                bn[r, c] = 0

            if n == 3:
                bn[r, c] = 1

            if n == 2:
                bn[r, c] = bo[r, c]

            if n < 2:
                bn[r, c] = 0
            
            
    print(bn)

    return np.copy(bn)



def updatestate():
    for r in range(n_rows):
        for c in range(n_columns):
            outmsg = mido.Message("note_on", note=notenum(r, c), velocity=b[r, c]*0b0110001)
            port.send(outmsg)


running = False
inport = mido.open_input(launchpad)


updatestate()
while 1:
    if running:
        print("Running")

        print(b)
        b= gametick(b)
        print(b)
        updatestate()
        sleep(0.1)

    for m in inport.iter_pending():
        if m.type == "control_change":
            if m.value == 127:
                if m.control == 104:
                    print("state change")
                    running = not running
                    updatestate()
                else:
                    print("reset")
                    b = np.zeros((n_rows, n_columns), dtype=int)

        if m.type == "note_on":
            (r, c) = notecoor(m.note)
            print(r, c)
            if m.velocity == 127:
                b[r, c] = not b[r, c]
                updatestate()



# 127
# 111 1000 

