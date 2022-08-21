"""
merakitoolkit
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Define MerakiToolKit class to ease operations with Meraki Cloud
"""

# standard libraries
import os
import sys
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import date

# additional libraries
import meraki
import merakitoolkitemail

__author__ = "Giovanni Augusto"
__copyright__ = "Copyright (C) 2022 Giovanni Augusto"
__license__ = "MIT"
__version__ = "1.0.0"


class MerakiToolkit():
    '''Defines the base class with all functionalities'''
    def __init__(self,apikey=None,verbose=False):
        self.verbose = verbose
        self.organizations = None
        self.apikey = apikey
        self._last_operation = None
        self.connect()


    @property
    def apikey(self):
        '''getter method for attribute apikey'''
        return self.__apikey

    @apikey.setter
    def apikey(self,apikey=None):
        '''
        setter method for apikey attribute
        making the API key retrievable only internally via "hidden" _apikey attribute
        '''
        try:
            if apikey:
                self.__apikey = apikey
            elif  "MERAKI_DASHBOARD_API_KEY" in os.environ:
                self.__apikey = os.environ["MERAKI_DASHBOARD_API_KEY"]
            else:
                raise ValueError("API key not found")
        except Exception as err: # pylint: disable=broad-except
            print("An error occurred while loading Meraki API key: ",err)
            sys.exit(2)


    def connect(self):
        '''
        connects to Meraki dashboard
        '''
        try:
            self.dashboard = meraki.DashboardAPI(
                api_key=self.apikey,
                suppress_logging=not self.verbose,
                simulate=False,
                caller="merakitoolkit"
                )
        except Exception as err: # pylint: disable=broad-except
            print("An error occurred while connecting to Meraki Dashboard: ",err)
            sys.exit(2)


    def get_organizations(self):
        '''
        Retrieve organizations from Meraki dashboard and store them in obj variable .organizations
        '''
        try:
            self.organizations = self.dashboard.organizations.getOrganizations()
        except Exception as err: # pylint: disable=broad-except
            print("An error occurred while retrieving Organizations: ",err)
            sys.exit(2)


    def pskchange(
        self,
        in_organizations:list=None,
        in_networks:list=None,
        in_tags:list=None,
        in_ssid:str=None,
        in_psk:str=None,
        dryrun:bool=False
        ):
        '''
        Change Pre Shared Key for an SSID in specified network name in organizations
        '''
        try:
            # verify that mandatory attributes are present, otherwise raise a ValueError exception
            if in_organizations is None:
                raise ValueError("PSK change : Organization input list is empty")
            if in_networks is None:
                raise ValueError("PSK change : Networks input list is empty")
            if (in_psk is None) or (len(in_psk)<8):
                raise ValueError("PSK change : PSK input is empty or less than 8 characters")

            # network_to_process will contain the list of networks to apply the PSK change
            networks_to_process = []

            # flag to set to save relevant data for other processes
            data_has_changed = False

            # scan matching organizations -> networks -> ssid -> collect data
            for organization in self.organizations:
                # Verify that the current organization is in the list of organizations to process
                if organization["name"] in in_organizations:
                    # Retrieve Networks for the current organization
                    networks = self.dashboard.organizations.getOrganizationNetworks(organization["id"]) # pylint: disable=line-too-long
                    for network in networks:
                        # Verify that network name is a match, if not skip this cycle
                        if (network["name"] not in in_networks) and ("ALL" not in in_networks):
                            continue
                        # verify that at least one of the TAGs is in the list of network tags
                        if in_tags:
                            if not any( tag in in_tags for tag in network["tags"]):
                                continue
                        # retrieve SSIDs of the evaluated network
                        network_ssids = self.dashboard.wireless.getNetworkWirelessSsids(network["id"]) # pylint: disable=line-too-long
                        # some networks has no SSIDs (camera,appliance,etc) so we skip those
                        if not network_ssids:
                            continue
                        for ssidposition in range(len(network_ssids)): # pylint: disable=consider-using-enumerate
                            if in_ssid == network_ssids[ssidposition]["name"]: # SSID is found
                                # create dictionary to collect all necessary information
                                network_to_process = {}
                                network_to_process["organization"] = organization["name"]
                                network_to_process["name"] = network["name"]
                                network_to_process["id"] = network["id"]
                                network_to_process["ssidPosition"] = str(ssidposition)
                                network_to_process["ssidName"] = network_ssids[ssidposition]["name"]
                                networks_to_process.append(network_to_process)
                                break # SSID was found -> exit the loop
        except Exception as err: # pylint: disable=broad-except
            print("An error occurred while running PSK change: ",err)
            sys.exit(2)
        if dryrun:
            for network in networks_to_process:
                print(f"| Org:{network['organization']:^20}| Network: {network['name']:^30}| SSID:{network['ssidName']:^20}| PSK:{in_psk:^15}|") # pylint: disable=line-too-long
            data_has_changed = True
        else:
            for network in networks_to_process:
                try:
                    self.dashboard.wireless.updateNetworkWirelessSsid(network["id"],network["ssidPosition"],psk=in_psk) # pylint: disable=line-too-long
                except TypeError as err:
                    print("An error occurred while running PSK change: ",err)
                except Exception as err: # pylint: disable=broad-except
                    print("operation: ",err.operation," error: ",err.message["errors"]," network: ",network["name"]," SSID: ",network["ssidName"]) # pylint: disable=line-too-long disable=no-member
            data_has_changed = True

        # save last operation data only if a change (real or simulated) happened
        if data_has_changed:
            self._last_operation = {
                "type":"pskchange",
                "networks":networks_to_process,
                "ssid":in_ssid,
                "psk":in_psk,
                "dryrun":dryrun
            }


    def send_email_psk(
        self,
        recipient:list,
        path:str,
        smtp_server:str=None,
        smtp_port:int=None,
        smtp_mode:str=None,
        sender:str="merakitoolkit",
        credentials:dict=None,
        ):
        ''' send email for PSK change notification'''

        if self._last_operation is not None:
            print("No Network changes -> Email discarded")
            return False

        context = ssl.create_default_context()

        if smtp_server is None:
            if "MERAKITK_SMTP" in os.environ.keys():
                smtp_settings = os.environ["MERAKITK_SMTP"].split(":")
                smtp_server=smtp_settings[0]
                smtp_port=smtp_settings[1]
                smtp_mode=smtp_settings[2]
                if credentials is None and (len(smtp_settings) >4):
                    credentials["user"] = smtp_settings[3]
                    credentials["password"] = smtp_settings[4]


        if smtp_mode == "TLS":
            try:
                with smtplib.SMTP_SSL(smtp_server,smtp_port,context=context) as server:
                    if credentials:
                        server.login(**credentials)
            except Exception as err:
                print("An error occurred while opening the SMTP connection: ",err)
        if smtp_mode == "STARTTLS":
            try:
                server = smtplib.SMTP(host=smtp_server, port=smtp_port)
                server.starttls()
                if credentials:
                    server.login(**credentials)
            except Exception as err:
                print("An error occurred while opening the SMTP connection: ",err)

        # Create the root MIME message
        msg_root = MIMEMultipart("related")
        msg_root['From']=sender
        msg_root['Bcc']=",".join(recipient) # for multiple email recipients 
        msg_root['Subject']=self._last_operation["ssid"] + " PSK changed " + date.today().strftime("%d/%m/%Y")
        msg_root.preamble = 'This is a multi-part message in MIME format.'

        data = {
            "ssid":self._last_operation["ssid"],
            "psk":self._last_operation["psk"],
            "logo":"logo.png",
            "qrcode":"QRcode.png",
        }
        # Attach text message part
        msg_alternative = MIMEMultipart("alternative")
        msg_root.attach(msg_alternative)
        msg_plaintext = merakitoolkitemail.generate_email_body("templatetxt.j2",path,data)
        msg_alternative.attach(msg_plaintext)
        # Send email
        try:
            server.send_message(msg_root)
        except Exception as err:
            print("An error occurred while sending the email: ",err)
