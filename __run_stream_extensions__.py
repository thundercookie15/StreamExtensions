'''
This file serves as entry-point for installer scripts
'''

# local imports
from userinterface.main import main
import pyuac

if __name__ == '__main__':
    if not pyuac.isUserAdmin():
        pyuac.runAsAdmin()
    else:
        main()
