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

<br><br>

## PSK Change email sample
------------------------------------------
Is possible to customize the email content and change/add images, including the logo.
QR code is automatically generated at each PSK change with the name *qrcode.png* and the related jinja2 variable is *qrcodepng*

Each image included in the template folder chosen is attached to the email template and can be inserted by referring to its filename stripped of the dot:<br>logo.png -> logopng
<br><br>
Default template to customize can be downloaded from Github : https://github.com/g1augusto/merakitoolkit/tree/master/merakitoolkit/templates/psk/default

![email sample image](https://github.com/g1augusto/merakitoolkit/raw/master/docs/emailsample.png "email sample image")

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)

## Third party libraries licenses and acknowledgements (THIRDPARTYLICENSES)
```
Apache-2.0
        'aiohttp' by None ('https://github.com/aio-libs/aiohttp')
        'aiosignal' by 'Nikolay Kim <fafhrd91@gmail.com>' ('https://github.com/aio-libs/aiosignal')
        'async-timeout' by 'Andrew Svetlov <andrew.svetlov@gmail.com> <andrew.svetlov@gmail.com>' ('https://github.com/aio-libs/async-timeout')
        'frozenlist' by None ('https://github.com/aio-libs/frozenlist')
        'multidict' by 'Andrew Svetlov <andrew.svetlov@gmail.com>' ('https://github.com/aio-libs/multidict')
        'requests' by 'Kenneth Reitz <me@kennethreitz.org>' ('https://requests.readthedocs.io')
        'yarl' by 'Andrew Svetlov <andrew.svetlov@gmail.com>' ('https://github.com/aio-libs/yarl/')

BSD-3-clause
        'idna' by 'Kim Davies <kim@cynosure.com.au>' ('https://github.com/kjd/idna')
        'xkcdpass' by 'Steven Tobin <steventtobin@gmail.com>' ('https://github.com/redacted/XKCD-password-generator')

MIT
        'attrs' by 'Hynek Schlawack <hs@ox.cx>' ('https://www.attrs.org/')
        'charset-normalizer' by 'Ahmed TAHRI @Ousret <ahmed.tahri@cloudnursery.dev>' ('https://github.com/ousret/charset_normalizer')
        'meraki' by 'Cisco Meraki <api-feedback@meraki.net>' ('https://github.com/meraki/dashboard-api-python')
        'pypng' by 'David Jones <drj@pobox.com>' ('https://gitlab.com/drj11/pypng')
        'urllib3' by 'Andrey Petrov <andrey.petrov@shazow.net>' ('https://urllib3.readthedocs.io/')

MPL-2.0
        'certifi' by 'Kenneth Reitz <me@kennethreitz.com>' ('https://github.com/certifi/python-certifi')
```