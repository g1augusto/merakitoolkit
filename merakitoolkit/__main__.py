"""
merakitoolkit main
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
main program executable
"""

# standard libraries
import asyncio
import sys
import os
from importlib import resources

# additional libraries
from merakitoolkit import merakitoolkitparser
from merakitoolkit import merakitoolkit


def main() -> int:
    '''merakitoolkit main program call'''

    mainparser,return_code = merakitoolkitparser.parser()
    if mainparser:
        if mainparser.command == "psk":
            merakiobj = merakitoolkit.MerakiToolkit(vars(mainparser))
            # This is a bugfix for async Event loop in windows (seems for aiohttp) https://stackoverflow.com/a/68137823/13616177
            if os.name == 'nt':
                asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
            asyncio.run(merakiobj.pskchangeasync())
            if mainparser.email:
                merakiobj.send_email_psk()
        if mainparser.command == "psktemplategen":
            # copy default template into local directory
            # create directory structure
            original_templatepath = templatepath = "./merakitoolkit/templates/psk/default"
            suffix = 2
            while True:
                try:
                    os.makedirs(templatepath)
                    break
                except FileExistsError:
                    templatepath = original_templatepath + str(suffix)
                    suffix += 1

            # copy files from default template folder to the local folder
            exclusion = [
                "__init__.py",
                "__pycache__"
            ]
            for resource in resources.contents("merakitoolkit.templates.psk.default"):
                if resource in exclusion:
                    continue
                try:
                    # try as a text file
                    with resources.open_text("merakitoolkit.templates.psk.default",resource) as source:
                        sourcedata = source.read()
                        with open(templatepath+"/"+resource,"w",encoding="utf-8") as destination:
                            destination.write(sourcedata)
                except UnicodeDecodeError:
                    # if an error occurs then it is a binary file
                    with resources.open_binary("merakitoolkit.templates.psk.default",resource) as source:
                        sourcedata = source.read()
                        with open(templatepath+"/"+resource,"wb") as destination:
                            destination.write(sourcedata)

    return return_code

if __name__ == "__main__":
    sys.exit(main())
