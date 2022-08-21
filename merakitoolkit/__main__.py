"""
merakitoolkit main
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
main program executable
"""

# standard libraries
import sys

# additional libraries
from merakitoolkitparser import parser
import merakitoolkit

def main() -> int:
    '''merakitoolkit main program call'''

    # ADD VALIDATION BEFORE PERFORMING OPERATIONS

    mainparser,return_code = parser()
    if mainparser:
        if mainparser.command == "psk":
            merakiobj = merakitoolkit.MerakiToolkit(vars(mainparser))
            merakiobj.pskchange()
    return return_code

if __name__ == "__main__":
    sys.exit(main())
