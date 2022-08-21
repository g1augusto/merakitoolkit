# merakitoolkit

merakitoolkit is a Python application to automate specific tasks with Meraki Cloud networks.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install merakitoolkit.

```bash
pip install merakitoolkit
```

## Usage
### Pre Shared Key change
```bash
usage: merakitoolkit psk [-h] [-t TAGS] [-e EMAIL [EMAIL ...]] [-v] [-d] -o ORGANIZATION -n NETWORK [NETWORK ...] -s SSID

optional arguments:
  -h, --help            show this help message and exit
  -t TAGS, --tags TAGS  Specify a list of tags
  -e EMAIL [EMAIL ...], --email EMAIL [EMAIL ...]
                        Specify a recipient Email or multiple recipients
  -v, --verbose         Enable logging (also for Meraki API)
  -d, --dryrun          Enable a failsafe run by only listing actions without applying them

required arguments:
  -o ORGANIZATION, --organization ORGANIZATION
                        Specify an Organization
  -n NETWORK [NETWORK ...], --network NETWORK [NETWORK ...]
                        Specify one or more networks (ALL for all networks)
  -s SSID, --ssid SSID  Specify an SSID

# SIMULATE a PSK change for an SSID in all networks for an organization, print a report of what would have happened
merakitoolkit psk \ 
--dryrun \
--organization MyOrganization \
--network ALL \
-s "My SSID" \
--email,"name.surname1@domain.net" "name.surname2@domain.net" \


# change PSK for SSID in all networks for an organization and sends email aftwerwards
merakitoolkit psk \ 
--organization MyOrganization \
--network ALL \
-s "My SSID" \
--email,"name.surname1@domain.net" "name.surname2@domain.net"


# change PSK for SSID in all networks with a specific tag in an organization
merakitoolkit psk \ 
--organization MyOrganization \
--network ALL \
-s "My SSID" \
-t tag
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)