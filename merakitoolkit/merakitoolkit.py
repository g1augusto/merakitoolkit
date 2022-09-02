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
from . import merakitoolkitsupport

__author__ = "Giovanni Augusto"
__copyright__ = "Copyright (C) 2022 Giovanni Augusto"
__license__ = "MIT"
__version__ = "1.0.3"


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
        '''Getter for the current operatino data'''
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
            if "MERAKITK_SMTP" in os.environ:
                smtp_settings = os.environ["MERAKITK_SMTP"].split("::")
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

        # Generate a PSK
        # priority of PSK choice : input psk > MERAKI_PSK env > automatic generation
        # randomization has effect only if a PSK was given in input otherwise is always applied
        if settings["passphrase"] is None:
            if "MERAKITK_PSK" in os.environ:
                psk_dictionary = os.environ["MERAKITK_PSK"].split("::")
            else:
                psk_dictionary = [""]
        else:
            psk_dictionary = [settings["passphrase"]]
        self._current_operation["settings"]["passphrase"] = merakitoolkitsupport.generate_psk(
                                                                    psk_dictionary,
                                                                    randomize=settings["passrandomize"]
                                                                    )
        # Validate PSK security


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
        except meraki.exceptions.APIError as err:
            print(f'operation: {err.operation} error: {err.message["errors"]}')
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

    def get_network_wireless_ssids(self,network):
        '''
        Retrieve SSIDs from a Network in Meraki dashboard and return them
        '''
        try:
            ssids = self.dashboard.wireless.getNetworkWirelessSsids(network["id"])
            return ssids
        except meraki.exceptions.APIError as err:
            print(f'operation: {err.operation} error: {err.message["errors"]} network: {network["name"]}')
            return None
        except Exception as err: # pylint: disable=broad-except
            print("An error occurred while retrieving Organizations: ",err)
            sys.exit(2)

    def get_organization_networks(self,organization):
        '''
        Retrieve Networks from an organization in Meraki dashboard and return them
        '''
        try:
            networks = self.dashboard.organizations.getOrganizationNetworks(organization["id"])
            return networks
        except meraki.exceptions.APIError as err:
            print(f'operation: {err.operation} error: {err.message["errors"]} Organization: {organization["name"]}')
            return None
        except Exception as err: # pylint: disable=broad-except
            print("An error occurred while retrieving Networks: ",err)
            sys.exit(2)

    def update_network_wireless_ssid(self,network,passphrase):
        '''
        update Wireless SSID in a network and return outcome of the operation
        '''
        try:
            ssid = self.dashboard.wireless.updateNetworkWirelessSsid(network["id"],network["ssidPosition"],psk=passphrase)
            if ssid["psk"] == passphrase:
                return True
            else:
                raise ValueError(f"PSK change : {ssid['name']} passhprase was not changed!")
        except meraki.exceptions.APIError as err:
            print(f'operation: {err.operation} error: {err.message["errors"]} Network: {network["id"]} SSID: {network["ssidName"]}') # pylint: disable=line-too-long
            return False
        except Exception as err: # pylint: disable=broad-except
            print("An error occurred while retrieving Networks: ",err)
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
                if organization["name"] in settings["organization"] or "ALL" in settings["organization"]:
                    # Retrieve Networks for the current organization
                    networks = self.get_organization_networks(organization)
                    for network in networks:
                        # Verify that network name is a match, if not skip this cycle
                        if (network["name"] not in settings["network"]) and ("ALL" not in settings["network"]):
                            continue
                        # verify that at least one of the TAGs is in the list of network tags
                        if settings["tags"]:
                            if not any( tag in settings["tags"] for tag in network["tags"]):
                                continue
                        # retrieve SSIDs of the evaluated network
                        network_ssids = self.get_network_wireless_ssids(network) # pylint: disable=line-too-long
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
                                network_to_process["wpaEncryptionMode"] = network_ssids[ssidposition]["wpaEncryptionMode"]
                                networks_to_process.append(network_to_process)
                                break # SSID was found -> exit the loop
        except Exception as err: # pylint: disable=broad-except
            print("An error occurred while running PSK change: ",err)
            sys.exit(2)

        # Execution code : at this point data is being changed (or simulated) on Meraki Cloud
        # NOTE : this portion could be extracted into a standalone executor method for multiple tasks
        if settings["dryrun"]:
            print(f'{"Organization":<25} {"Network:":<45} {"SSID:":<20} {"PSK:":<20}')
            for network in networks_to_process:
                print("-"*100)
                print(f"{network['organization']:<25} {network['name']:<45} {network['ssidName']:<20} {settings['passphrase']:<20}") # pylint: disable=line-too-long
                data_has_changed = True
        else:
            for network in networks_to_process:
                data_has_changed = self.update_network_wireless_ssid(network,settings["passphrase"])

        # save last operation data only if a change (real or simulated) happened
        if data_has_changed:
            self.current_operation["networks_to_process"] = networks_to_process
            self.current_operation["success"] = True

    # refactor email send method
    def send_email_psk(self):
        ''' send email for PSK change notification'''

        if not self.current_operation["success"]:
            print("No Network changes -> Email discarded")
            return False

        settings = self.current_operation["settings"]

        # Create the root MIME message
        msg_root = MIMEMultipart("related")
        msg_root['From']=settings["smtp_sender"]
        msg_root['Bcc']=",".join(settings["email"]) # for multiple email recipients
        msg_root['Subject']=settings["ssid"] + " PSK changed " + date.today().strftime("%d/%m/%Y")
        msg_root.preamble = 'This is a multi-part message in MIME format.'

        # Attach text message part
        msg_alternative = MIMEMultipart("alternative")
        msg_root.attach(msg_alternative)
        msg_text = merakitoolkitsupport.generate_email_body(
            "templatetxt.j2",
            settings["emailtemplate"],
            settings["ssid"],
            settings["passphrase"]
            )
        msg_text_mime = MIMEText(msg_text,"plain")
        msg_alternative.attach(msg_text_mime)

        # Generate QR Code image to distribute in the email
        merakitoolkitsupport.generate_qrcode(settings["ssid"],settings["passphrase"],settings["emailtemplate"])

        # Gather the list of images filenames
        imagelist = [x for x in os.listdir(settings["emailtemplate"]) if x.lower().endswith(("png","bmp","jpg","gif"))]
        # generate the same list but with filenames without dots, to be used in jinja2 template
        imagelistj2 = [x.replace(".","") for x in imagelist]

        # image will be a tuple with the real filename from imagelist and the dot-stripped version from imagelistj2
        # real filename will be used to attach the image file, dot-stripped name to create he reference ID in the email
        for image in zip(imagelist,imagelistj2):
            # Open each image in the template folder and encode it in base64 to attach to the email
            try:
                with open(f'{settings["emailtemplate"]}/{image[0]}', 'rb') as imagefile:
                    # set attachment mime and file name, the image type is png
                    mime = MIMEBase('image', image[0][-3:], filename=image[0])
                    # add required header data:
                    mime.add_header('Content-Disposition', 'attachment', filename=image[0])
                    mime.add_header('X-Attachment-Id', image[0])
                    mime.add_header('Content-ID', f'<{image[1]}>')
                    # read attachment file content into the MIMEBase object
                    mime.set_payload(imagefile.read())
                    # encode with base64
                    encoders.encode_base64(mime)
                    # add MIMEBase object to MIMEMultipart object
                    msg_root.attach(mime)
            except Exception as err: # pylint: disable=broad-except
                print("An error occurred while opening logo image: ",err)

        msg_html = merakitoolkitsupport.generate_email_body(
            "templatehtml.j2",
            settings["emailtemplate"],
            settings["ssid"],
            settings["passphrase"],
            imagelistj2
            )
        msg_html_mime = MIMEText(msg_html,"html")
        msg_alternative.attach(msg_html_mime)

        context = ssl.create_default_context()

        if settings["smtp_mode"] == "TLS":
            try:
                with smtplib.SMTP_SSL(settings["smtp_server"],settings["smtp_port"],context=context) as server:
                    if settings["smtp_user"] and settings["smtp_pass"]:
                        server.login(user=settings["smtp_user"],password=settings["smtp_pass"])
                    server.send_message(msg_root)
            except Exception as err: # pylint: disable=broad-except
                print("An error occurred while opening the SMTP connection: ",err)
        if settings["smtp_mode"] in ["STARTTLS","SMTP"]:
            try:
                server = smtplib.SMTP(host=settings["smtp_server"], port=settings["smtp_port"])
                # apply TLS encryption only if STARTTLS is selected
                if settings["smtp_mode"] == "STARTTLS":
                    server.starttls()
                # login to server only if credentials are provided
                if settings["smtp_user"] and settings["smtp_pass"]:
                    server.login(user=settings["smtp_user"],password=settings["smtp_pass"])
                server.send_message(msg_root)
            except Exception as err: # pylint: disable=broad-except
                print("An error occurred while opening the SMTP connection: ",err)

        # Cleanup QR code files
        try:
            if os.path.exists(f"{settings['emailtemplate']}qrcode.png"):
                os.remove(f"{settings['emailtemplate']}qrcode.png")
        except Exception as err: # pylint: disable=broad-except
            print("An error occurred while deleting QR code image files: ",err)
