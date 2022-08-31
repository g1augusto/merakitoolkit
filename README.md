# merakitoolkit

merakitoolkit is a Python application to automate specific tasks with Meraki Cloud networks.<br>
Currently supported operations are
- Pre Shared Key Change (**psk**) on a specific SSID
  - filter by Organization (multiple)
  - filter Networks by Network Tags (multiple)
  - filter Networks by Network names (multiple)
  - send an email with the PSK change information
    - email based on jinja2 template
    - attach any image in the template folder selected
    - generate a QR code to attach to the email template

<br>


## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install merakitoolkit.

```bash
pip install merakitoolkit
```
<br>

## Usage
### Pre Shared Key change
```bash
usage: merakitoolkit psk [-h] [-t TAGS [TAGS ...]] [-v] [-d] [-p PASSPHRASE] [-pr] [-e EMAIL [EMAIL ...]] [-et EMAILTEMPLATE] [--smtp-sender SMTP_SENDER] [--smtp-server SMTP_SERVER] [--smtp-port SMTP_PORT] [--smtp-mode {TLS,STARTTLS,SMTP}]
                         [--smtp-user SMTP_USER] [--smtp-pass SMTP_PASS] -o ORGANIZATION [ORGANIZATION ...] -n NETWORK [NETWORK ...] -s SSID

Changes a Meraki SSID Pre Shared Key

optional arguments:
  -h, --help            show this help message and exit
  -t TAGS [TAGS ...], --tags TAGS [TAGS ...]
                        Specify a list of tags
  -v, --verbose         Enable logging (also for Meraki API)
  -d, --dryrun          Enable a failsafe run by only listing actions without applying them
  -p PASSPHRASE, --passphrase PASSPHRASE
                        PSK, can be loaded from env MERAKITK_PSK
  -pr, --passrandomize  if PSK is given in input, ap
  -e EMAIL [EMAIL ...], --email EMAIL [EMAIL ...]
                        Specify a recipient Email or multiple recipients
  -et EMAILTEMPLATE, --emailtemplate EMAILTEMPLATE
                        template folder for email, valid only if --email is set
  --smtp-sender SMTP_SENDER
                        specify a sender for the email delivery
  --smtp-server SMTP_SERVER
                        specify a mailserver, or env MERAKITK_SMTP=<server>:<port>:<mode>:<user>:<pass>
  --smtp-port SMTP_PORT
                        specify a mailserver server port
  --smtp-mode {TLS,STARTTLS,SMTP}
                        specify connection mode to the mailserver [TLS|STARTTLS|SMTP] default=TLS
  --smtp-user SMTP_USER
                        specify an username for SMTP connection
  --smtp-pass SMTP_PASS
                        specify a password for SMTP connection

required arguments:
  -o ORGANIZATION [ORGANIZATION ...], --organization ORGANIZATION [ORGANIZATION ...]
                        Specify an Organization
  -n NETWORK [NETWORK ...], --network NETWORK [NETWORK ...]
                        Specify one or more networks (ALL for all networks)
  -s SSID, --ssid SSID  Specify an SSID

# SIMULATE a PSK change for an SSID in all networks for an organization, print a report of what would have happened (API KEY, email, PSK are set via env variables)
merakitoolkit psk \ 
--dryrun \
--organization MyOrganization \
--network ALL \
-s "My SSID" \
--email,"name.surname1@domain.net" "name.surname2@domain.net" \


# change PSK for SSID in all networks for an organization and sends email aftwerwards (API KEY, email, PSK are set via env variables)
merakitoolkit psk \ 
--organization MyOrganization \
--network ALL \
-s "My SSID" \
--email,"name.surname1@domain.net" "name.surname2@domain.net"


# change PSK for SSID in all networks with a specific tag in two organizations (API KEY, email, PSK are set via env variables)
merakitoolkit psk \ 
--organization MyOrganization1 MyOrganization2 \
--network ALL \
-s "My SSID" \
-t tag
```
<br>

## Using environment variables
------------------------------------------
### MerakiToolKit can be used with all its parameters passed in input via the command line but for some sensible information is better to use the environment variables listed below
| variable      | Description |
| ----------- | ------------------------------------------ |
| MERAKI_DASHBOARD_API_KEY      | [API key generated in Meraki Dashboard](https://documentation.meraki.com/General_Administration/Other_Topics/Cisco_Meraki_Dashboard_API#Enable_API_Access)<br>**MERAKI_DASHBOARD_API_KEY=123456789abcdefghi**       |
| MERAKITK_SMTP   | SMTP server informations separated by double colon :: in the form: <br>**MERAKITK_SMTP=SMTP_SERVER::PORT::MODE::USERNAME::PASSWORD** |
|MERAKITK_PSK| Passphrase or list of possible words.<br>When multiple passhprases are available, entropy is always added to the final PSK<br>**MERAKITK_PSK=your_password123**<br>or<br>**MERAKITK_PSK=pass1::pass2:pass3:pass4:pass5**


## PSK Change email sample
------------------------------------------
![email sample image](/docs/emailsample.png "email sample image")

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)