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
    def __init__(self,settings):
        '''
        apikey
        command
        tags
        verbose
        dryrun
        passphrase
        email
        emailtemplate
        organization
        network
        ssid
        smtp-server
        smtp-port
        smtp-mode
        smtp-user
        smtp-pass
        '''
        # Meraki API key is common for all operations and is assigned via the property method
        self.apikey = settings["apikey"]
        # operation data received in input
        self.current_operation = settings
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

    @property
    def current_operation(self):
        if hasattr(self,"_current_operation"):
            return self._current_operation
        else:
            return None

    @current_operation.setter
    def current_operation(self,settings):
        if hasattr(self,"_last_operation"):
            self._last_operation = self.current_operation.copy()
        else:
            self._last_operation = None
        self._current_operation = {
            "settings": {x: settings[x] for x in settings if x not in ["apikey"] },
            "success": False
        }
         # verify that at least one parameter for smtp is empty
        if None in ([ settings[x] for x in settings if "smtp" in x ]):
            # verify that the MERAKITK_SMTP environment variable exists and loads it
            if "MERAKITK_SMTP" in os.environ.keys():
                smtp_settings = os.environ["MERAKITK_SMTP"].split(":")
                # if a parameter was passed in input, retain it otherwise use the environment var
                if settings["smtp_server"] is None:
                    self._current_operation["settings"]["smtp_server"]=smtp_settings[0]
                if settings["smtp_port"] is None:
                    self._current_operation["settings"]["smtp_port"]=smtp_settings[1]
                if settings["smtp_mode"] is None:
                    self._current_operation["settings"]["smtp_mode"]=smtp_settings[2]
                if settings["smtp_user"] is None:
                    self._current_operation["settings"]["smtp_user"]=smtp_settings[3]
                if settings["smtp_pass"] is None:
                    self._current_operation["settings"]["smtp_pass"]=smtp_settings[4]


    def connect(self):
        '''
        connects to Meraki dashboard
        '''
        try:
            self.dashboard = meraki.DashboardAPI(
                api_key=self.apikey,
                suppress_logging=not self.current_operation["settings"]["verbose"],
                simulate=False,
                caller="merakitoolkit"
                )
        except Exception as err: # pylint: disable=broad-except
            print("An error occurred while connecting to Meraki Dashboard: ",err)
            sys.exit(2)


    def get_organizations(self):
        '''
        Retrieve organizations from Meraki dashboard and return them
        '''
        try:
            organizations = self.dashboard.organizations.getOrganizations()
            return organizations
        except Exception as err: # pylint: disable=broad-except
            print("An error occurred while retrieving Organizations: ",err)
            sys.exit(2)


    def pskchange(self):
        '''
        Change Pre Shared Key for an SSID in specified network name in organizations
        '''
        settings = self.current_operation["settings"]
        try:
            if settings is None:
                raise ValueError("PSK change : No operation has been defined")
            # verify that mandatory attributes are present, otherwise raise a ValueError exception
            if settings["organization"] is None:
                raise ValueError("PSK change : Organization input list is empty")
            if settings["network"] is None:
                raise ValueError("PSK change : Networks input list is empty")
            if (settings["passphrase"] is None) or (len(settings["passphrase"])<8):
                raise ValueError("PSK change : PSK input is empty or less than 8 characters")

            # network_to_process will contain the list of networks to apply the PSK change
            networks_to_process = []

            # flag to set to save relevant data for other processes
            data_has_changed = False

            # scan matching organizations -> networks -> ssid -> collect data
            for organization in self.get_organizations():
                # Verify that the current organization is in the list of organizations to process
                if organization["name"] in settings["organization"]:
                    # Retrieve Networks for the current organization
                    networks = self.dashboard.organizations.getOrganizationNetworks(organization["id"]) # pylint: disable=line-too-long
                    for network in networks:
                        # Verify that network name is a match, if not skip this cycle
                        if (network["name"] not in settings["network"]) and ("ALL" not in settings["network"]):
                            continue
                        # verify that at least one of the TAGs is in the list of network tags
                        if settings["tags"]:
                            if not any( tag in settings["tags"] for tag in network["tags"]):
                                continue
                        # retrieve SSIDs of the evaluated network
                        network_ssids = self.dashboard.wireless.getNetworkWirelessSsids(network["id"]) # pylint: disable=line-too-long
                        # some networks has no SSIDs (camera,appliance,etc) so we skip those
                        if not network_ssids:
                            continue
                        for ssidposition in range(len(network_ssids)): # pylint: disable=consider-using-enumerate
                            if settings["ssid"] == network_ssids[ssidposition]["name"]: # SSID is found
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
        if settings["dryrun"]:
            for network in networks_to_process:
                print(f"| Org:{network['organization']:^20}| Network: {network['name']:^30}| SSID:{network['ssidName']:^20}| PSK:{settings['passphrase']:^15}|") # pylint: disable=line-too-long
            data_has_changed = True
        else:
            for network in networks_to_process:
                try:
                    self.dashboard.wireless.updateNetworkWirelessSsid(network["id"],network["ssidPosition"],psk=settings["passphrase"]) # pylint: disable=line-too-long
                except TypeError as err:
                    print("An error occurred while running PSK change: ",err)
                except Exception as err: # pylint: disable=broad-except
                    print("operation: ",err.operation," error: ",err.message["errors"]," network: ",network["name"]," SSID: ",network["ssidName"]) # pylint: disable=line-too-long disable=no-member
            data_has_changed = True

        # save last operation data only if a change (real or simulated) happened
        if data_has_changed:
            self.current_operation["networks"] = networks_to_process
            self.current_operation["success"] = True


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
