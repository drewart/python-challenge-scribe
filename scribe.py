import time
import os

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

for i in range(0, 20):
    print('\n\n\n\n\n')
    print(' ' * i + '.')
    time.sleep(0.1)
    clear()
