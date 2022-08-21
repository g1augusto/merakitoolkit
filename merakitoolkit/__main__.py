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
            merakiobj = merakitoolkit.MerakiToolkit(
                apikey=mainparser.apikey,
                verbose=mainparser.verbose
                )
            merakiobj.get_organizations()
            merakiobj.pskchange(
                mainparser.organization,
                mainparser.network,
                mainparser.tags,
                mainparser.ssid,
                mainparser.passhprase,
                mainparser.dryrun
            )
    return return_code

if __name__ == "__main__":
    sys.exit(main())
