'''support functions for merakitoolkit parser'''

# standard libraries
import sys

# additional libraries
import argparse
from  merakitoolkit import __version__,__copyright__,__license__

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
                        help="Enable logging (also for Meraki API)",action="store_true")
    psksubparser.add_argument("-d",
                        "--dryrun",
                        help="Enable a failsafe run by only listing actions without applying them",
                        action="store_true")
    psksubparser.add_argument("-p",
                        "--passphrase",
                        help="PSK, can be loaded from environment variable MERAKI_DASHBOARD_API_KEY",
                        type=str,
                        action="store")
    psksubparser.add_argument("-e",
                        "--email",
                        nargs="+",
                        help="Specify a recipient Email or multiple recipients",
                        action="store")
    psksubparser.add_argument("-et",
                        "--emailtemplate",
                        default="./templates/psk/default/",
                        help="template folder for email, valid only if --email is set",
                        action="store") # can be used only if --email is set
    psksubparser.add_argument("--smtp-server",
                        help="specify a mailserver server",
                        action="store")
    psksubparser.add_argument("--smtp-port",
                        help="specify a mailserver server port",
                        action="store")
    psksubparser.add_argument("--smtp-mode",
                        help="specify connection mode to the mailserver [TLS|STARTTLS] default=TLS ",
                        choices=["TLS","STARTTLS"],
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
                               help="Specify an Organization",
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
        return_code = 0
    return args,return_code
