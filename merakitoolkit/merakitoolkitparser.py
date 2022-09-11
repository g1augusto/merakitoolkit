"""
merakitoolkit parser
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Define a parser function to process input parameters for MerakiToolkit
"""

# standard libraries
import argparse
import sys
import os

# additional libraries
from  .merakitoolkit import __version__,__copyright__,__license__

class MyParser(argparse.ArgumentParser):
    '''
    Class to modify ArgumentParser standard behavior in case or input error
    prints the help message along with the usage tip
    '''
    def error(self, message):
        sys.stderr.write(f'error: {message}\n')
        self.print_help()
        sys.exit(2)


def parser():
    '''
    Support function to create the parser for all program options
    '''
    # Create argparse main parser with title and copyright
    merakiparser = MyParser(
        description=f"Meraki Toolkit version {__version__}",
        epilog=f"{__copyright__} | License: {__license__}"
    )
    merakiparser.add_argument("-k",
                        "--apikey",
                        help="Meraki API KEY, can be loaded from variable MERAKI_DASHBOARD_API_KEY",
                        action="store")

    # Create subparser object containing all possible merakitoolkit operations:
    # any new operation needs to be generated from the subparser object
    subparser = merakiparser.add_subparsers(help="meraki operations")


    # PSK email generation command
    psktemplatesubparser = subparser.add_parser(
                                        "psktemplategen",
                                        description="Generate PSK email template",
                                        help="Generate PSK email template in local directory"
                                        )
    psktemplatesubparser.set_defaults(command="psktemplategen") # to identify in main() the command
    # psksubparser adds the "psk" operation
    # --------------------------------------------------------------------------------------------
    psksubparser = subparser.add_parser(
                                        "psk",
                                        description="Changes a Meraki SSID Pre Shared Key",
                                        help="Pre Shared Key modifications"
                                        )

    # psk operation arguments
    # ---------------------------------------------
    psksubparser.set_defaults(command="psk") # to identify in main() the command
    psksubparser.add_argument("-t",
                        "--tags",
                        nargs="+",
                        help="Specify a list of tags",
                        action="store")
    psksubparser.add_argument("-v",
                        "--verbose",
                        help='''Incremental logging level
                        1: print operation resuls
                        2: Print concurrent functions execution
                        3: Print Meraki API calls and save them to local log file ''',
                        action="count",
                        default=0)
    psksubparser.add_argument("-d",
                        "--dryrun",
                        help="Enable a failsafe run by only listing actions without applying them",
                        action="store_true")
    psksubparser.add_argument("-p",
                        "--passphrase",
                        help="PSK, can be loaded from env MERAKITK_PSK",
                        type=str,
                        action="store")
    psksubparser.add_argument("-pr",
                        "--passrandomize",
                        help="if PSK is given in input, apply entropy to it",
                        default=False,
                        action="store_true")
    psksubparser.add_argument("-e",
                        "--email",
                        nargs="+",
                        help="Specify a recipient Email or multiple recipients",
                        action="store")
    psksubparser.add_argument("-et",
                        "--emailtemplate",
                        default="./merakitoolkit/templates/psk/default/",
                        help="template folder for email, valid only if --email is set",
                        action="store") # can be used only if --email is set
    psksubparser.add_argument("--smtp-sender",
                        help="specify a sender for the email delivery",
                        default="MerakiToolkit",
                        action="store")
    psksubparser.add_argument("--smtp-server",
                        help="specify a mailserver, or env MERAKITK_SMTP=<server>:<port>:<mode>:<user>:<pass>",
                        action="store")
    psksubparser.add_argument("--smtp-port",
                        help="specify a mailserver server port",
                        action="store")
    psksubparser.add_argument("--smtp-mode",
                        help="specify connection mode to the mailserver [TLS|STARTTLS|SMTP] default=TLS ",
                        choices=["TLS","STARTTLS","SMTP"],
                        default="TLS",
                        action="store")
    psksubparser.add_argument("--smtp-user",
                        help="specify an username for SMTP connection",
                        action="store")
    psksubparser.add_argument("--smtp-pass",
                        help="specify a password for SMTP connection",
                        action="store")
    pskrequirednamed = psksubparser.add_argument_group('required arguments')
    pskrequirednamed.add_argument("-o",
                               "--organization",
                               nargs="+",
                               help="Specify one or more Organizations (ALL for all Organizations)",
                               required=True)
    pskrequirednamed.add_argument("-n",
                               "--network",
                               nargs="+",
                               help="Specify one or more networks (ALL for all networks)",
                               action="store",
                               required=True)
    pskrequirednamed.add_argument("-s",
                               "--ssid",
                               help="Specify an SSID",
                               required=True)
    # ---------------------------------------------


    # modify argparse standard behavior: if no argument print parser help (eq: -h)
    # --------------------------------------------------------------------------------------------
    if len(sys.argv) == 1:
        args = None
        merakiparser.print_help()
        return_code = 1
    else:
        args = merakiparser.parse_args()
        if args.command == "psk":
            # verify that email template path is not missing the last forward slash
            if args.emailtemplate[-1] != "/":
                args.emailtemplate += "/"

            # verify that template path chosen is valid
            if args.email:
                templates = ["templatehtml.j2","templatetxt.j2"]
                for template in templates:
                    try:
                        if not os.path.exists(args.emailtemplate+template):
                            raise FileNotFoundError
                    except FileNotFoundError as err:
                        print("Template missing from template path,you can generate one with 'psktemplategen' command: ",err)
                        sys.exit(2)
        if args.command == "psktemplategen":
            # for future use
            pass
        return_code = 0
    return args,return_code
