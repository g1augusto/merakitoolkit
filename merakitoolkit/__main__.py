"""
merakitoolkit main
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
main program executable
"""

# standard libraries
import sys

# additional libraries
import merakitoolkit.merakitoolkitparser as merakitoolkitparser # pylint: disable=import-error
import merakitoolkit.merakitoolkit as merakitoolkit

def main() -> int:
    '''merakitoolkit main program call'''

    mainparser,return_code = merakitoolkitparser.parser()
    if mainparser:
        if mainparser.command == "psk":
            merakiobj = merakitoolkit.MerakiToolkit(vars(mainparser))
            merakiobj.pskchange()
            merakiobj.send_email_psk()
    return return_code

if __name__ == "__main__":
    sys.exit(main())
