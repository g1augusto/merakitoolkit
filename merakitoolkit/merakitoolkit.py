"""
merakitoolkit
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Define MerakiToolKit class to ease operations with Meraki Cloud
"""

# standard libraries
import asyncio
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
import meraki.aio
from . import merakitoolkitsupport

__author__ = "Giovanni Augusto"
__copyright__ = "Copyright (C) 2022 Giovanni Augusto"
__license__ = "MIT"
__version__ = "1.1.5"


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
        self.dashboard = None


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
        ASYNC : returns an initialized meraki.aio.AsyncDashboardAPI object
        object is to be used with 'async with' in calling methods (pskchangeasync)
        and reference 'as' is to be self.dashboard
        '''
        if self.current_operation["settings"]["verbose"] >= 3:
            logging = True
        else :
            logging = False
        try:
            return meraki.aio.AsyncDashboardAPI(
                api_key=self.apikey,
                suppress_logging=not logging,
                simulate=False,
                caller="merakitoolkit"
                )
        except meraki.exceptions.AsyncAPIError as err:
            print(f'operation: {err.operation} error: {err.message["errors"]}')
        except meraki.exceptions.APIError as err:
            print(f'operation: {err.operation} error: {err.message["errors"]}')
        except Exception as err: # pylint: disable=broad-except
            print("An error occurred while connecting to Meraki Dashboard: ",err)
            sys.exit(2)


    async def get_organizations(self):
        '''
        Retrieve organizations from Meraki dashboard and return them
        '''
        try:
            if self.current_operation["settings"]["verbose"]>=2:
                print("START: getting Organizations")
            organizations = await self.dashboard.organizations.getOrganizations()
            if self.current_operation["settings"]["verbose"]>=2:
                print("END: getting Organizations")
            return organizations
        except meraki.exceptions.AsyncAPIError as err:
            # Too many requests
            if err.response.status == 429:
                # wait for the time indicated in reponse header Retry-After and then retry
                await asyncio.sleep(int(err.response.headers["Retry-After"]))
                return await self.get_organizations()
            else:
                print(f'operation: {err.operation} error: {err.message["errors"]}')
                return None
        except Exception as err: # pylint: disable=broad-except
            print("An error occurred while retrieving Organizations: ",err)
            sys.exit(2)


    async def get_network_wireless_ssids(self,network):
        '''
        Retrieve SSIDs from a Network in Meraki dashboard and return them
        '''
        try:
            if self.current_operation["settings"]["verbose"]>=2:
                print(f"START: getting SSIDs for Network: {network['name']}")
            ssids = await self.dashboard.wireless.getNetworkWirelessSsids(network["id"])
            if self.current_operation["settings"]["verbose"]>=2:
                print(f"END: getting SSIDs for Network: {network['name']}")
            return ssids
        except meraki.exceptions.AsyncAPIError as err:
            # Too many requests
            if err.response.status == 429:
                # wait for the time indicated in reponse header Retry-After and then retry
                await asyncio.sleep(int(err.response.headers["Retry-After"]))
                return await self.get_network_wireless_ssids(network)
            else:
                print(f'operation: {err.operation} error: {err.message["errors"]} network: {network["name"]}')
                return None
        except meraki.exceptions.APIError as err:
            print(f'operation: {err.operation} error: {err.message["errors"]} network: {network["name"]}')
            return None
        except Exception as err: # pylint: disable=broad-except
            print("An error occurred while retrieving Organizations: ",err)
            sys.exit(2)


    async def get_organization_networks(self,organization):
        '''
        Retrieve Networks from an organization in Meraki dashboard and return them
        '''
        try:
            if self.current_operation["settings"]["verbose"]>=2:
                print(f"START: getting networks for org: {organization['name']}")
            networks = await self.dashboard.organizations.getOrganizationNetworks(organization["id"])
            if self.current_operation["settings"]["verbose"]>=2:
                print(f"END: getting networks for org: {organization['name']}")
            return networks
        except meraki.exceptions.AsyncAPIError as err:
            # Too many requests
            if err.response.status == 429:
                # wait for the time indicated in reponse header Retry-After and then retry
                await asyncio.sleep(int(err.response.headers["Retry-After"]))
                return await self.get_organization_networks(organization)
            else:
                print(f'operation: {err.operation} error: {err.message["errors"]} Organization: {organization["name"]}')
                return None
        except meraki.exceptions.APIError as err:
            print(f'operation: {err.operation} error: {err.message["errors"]} Organization: {organization["name"]}')
            return None
        except Exception as err: # pylint: disable=broad-except
            print("An error occurred while retrieving Networks: ",err)
            sys.exit(2)


    async def update_network_wireless_ssid(self,network,passphrase):
        '''
        update Wireless SSID in a network and return outcome of the operation
        '''
        try:
            if self.current_operation["settings"]["verbose"]>=2:
                print(f"START: updating PSK for network: {network['name']}")
            ssid = await self.dashboard.wireless.updateNetworkWirelessSsid(network["id"],network["ssidPosition"],psk=passphrase)
            if self.current_operation["settings"]["verbose"]>=2:
                print(f"END: updating PSK for network: {network['name']}")
            if ssid["psk"] == passphrase:
                return True
            else:
                raise ValueError(f"PSK change : {ssid['name']} passhprase was not changed!")
        except meraki.exceptions.AsyncAPIError as err:
            # Too many requests
            if err.response.status == 429:
                # wait for the time indicated in reponse header Retry-After and then retry
                await asyncio.sleep(int(err.response.headers["Retry-After"]))
                return await self.update_network_wireless_ssid(network,passphrase)
            else:
                print(f'operation: {err.operation} error: {err.message["errors"]} Network: {network["id"]} SSID: {network["ssidName"]}') # pylint: disable=line-too-long
                return False
        except meraki.exceptions.APIError as err:
            print(f'operation: {err.operation} error: {err.message["errors"]} Network: {network["id"]} SSID: {network["ssidName"]}') # pylint: disable=line-too-long
            return False
        except Exception as err: # pylint: disable=broad-except
            print("An error occurred while retrieving Networks: ",err)
            sys.exit(2)


    async def pskchangeasync(self):
        '''
        Change Pre Shared Key for an SSID in specified network name in organizations
        '''

        # Coroutine to process Networks in an organization for PSK change
        # returns data of a network to process (if parameters has a match)
        # returns None if there is no match -> needs to explicitly cleanup later 'None' entries from networks list
        async def process_network(organization,network,settings):
            if (network["name"] not in settings["network"]) and ("ALL" not in settings["network"]):
                return None
            # verify that at least one of the TAGs is in the list of network tags
            if settings["tags"]:
                if not any( tag in settings["tags"] for tag in network["tags"]):
                    return None
            # retrieve SSIDs of the evaluated network
            # uses awaitable method that will be leveraged later by asyncio.gather()
            network_ssids = await self.get_network_wireless_ssids(network)
            # some networks has no SSIDs (camera,appliance,etc) so we skip those
            if not network_ssids:
                return None
            network_to_process = None
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
                    break # SSID was found -> exit the loop
            return network_to_process

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

            # Create context manager for the async mereaki.aio.AsyncDashboardAPI object (necessary to ensure a proper closure)
            # Standard in MerakiToolKit is to store context manager variable in self.dashboard
            # connect() method is used to aggregate all settings centrally
            async with self.connect() as self.dashboard:
                # async tasks collection:
                # collect organizations->collect networks in organization->collect SSID->add item to list of networks to process

                # async collect organizations (create task->await task)
                task_organizations = asyncio.create_task(self.get_organizations())
                organizations = await task_organizations
                # process_networks_tasks -> list of coroutines for networks to process
                process_networks_tasks = []
                # in each organization retrieve list of networks
                for organization in organizations:
                    # Verify that the current organization is in the list of organizations to process
                    if organization["name"] in settings["organization"] or "ALL" in settings["organization"]:
                        # async collect list of networks (create task->await task)
                        task_networks = asyncio.create_task(self.get_organization_networks(organization))
                        networks = await task_networks
                        # create a coroutine to process each network and add it to process_networks_tasks list
                        for network in networks:
                            process_networks_tasks.append(process_network(organization,network,settings))

                # Collection happened through an iteration with async awaits
                # here we process all coroutines collected asynchronously with asyncio.gather
                # asyncio.gather -> returns values when all coroutines are completed
                current_networks_to_process = await asyncio.gather(*process_networks_tasks)
                # Clean current networks list of the null entries and keep only networks to process
                # extend the final networks_to_process list with the interesting networks for the current org
                networks_to_process.extend([x for x in current_networks_to_process if x is not None])



                # Execution code : at this point data is being changed (or simulated) on Meraki Cloud
                # NOTE : this portion could be extracted into a standalone executor method for multiple tasks
                if settings["dryrun"] or settings["verbose"]>=1:
                    if settings["dryrun"]:
                        data_has_changed = True
                        print("\033[91m","\nDRYRUN Enabled: Changes below will not be applied")
                        print("\033[0m","-"*110)
                    print(f'{"Organization:":<25} {"Network:":<45} {"SSID:":<20} {"PSK:":<20}')
                    for network in networks_to_process:
                        print("-"*110)
                        print(f"{network['organization']:<25} {network['name']:<45} {network['ssidName']:<20} {settings['passphrase']:<20}") # pylint: disable=line-too-long
                else:
                    update_networks_tasks = []
                    for network in networks_to_process:
                        update_networks_tasks.append(self.update_network_wireless_ssid(network,settings["passphrase"]))
                        #data_has_changed = self.update_network_wireless_ssid(network,settings["passphrase"])
                    data_has_changed = True in await asyncio.gather(*update_networks_tasks)

                # save last operation data only if a change (real or simulated) happened
                if data_has_changed:
                    self.current_operation["networks_to_process"] = networks_to_process
                    self.current_operation["success"] = True

        except Exception as err: # pylint: disable=broad-except
            print("An error occurred while running PSK change: ",err)
            sys.exit(2)



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
