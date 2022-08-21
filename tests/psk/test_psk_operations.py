'''test meraki operations'''

import json
import pytest
import meraki
import merakitoolkit # pylint: disable=import-error

# Assume that the correct Meraki API key is the following
APIKEY_CORRECT = "123456789"

# Will contain the updated data at each call of mocked functions
mock_meraki_dashboard_results = {}

@pytest.fixture(name="mock_meraki_dashboard")
def fixture_mock_meraki_dashboard(monkeypatch):
    '''fixture to return offline dashboard data'''

    # load organization JSON data file previously extracted from Devnet Sandbox
    try:
        with open("./tests/psk/organizations.json","r",encoding="utf-8") as organizations_file:
            organization_data = json.load(organizations_file)
        with open("./tests/psk/networks_org1.json","r",encoding="utf-8") as networks_file:
            networks_data = json.load(networks_file)
        with open("./tests/psk/networks_org1_ssids.json","r",encoding="utf-8") as ssid_file:
            ssid_data = json.load(ssid_file)
    except Exception as err: # pylint: disable=broad-except
        print("An error occurred while  loading mock data: ",err)

    # initialize mock data results with json data
    mock_meraki_dashboard_results["organization_data"] = organization_data
    mock_meraki_dashboard_results["networks_data"] = networks_data
    mock_meraki_dashboard_results["ssid_data"] = ssid_data

    # mock function to get organizations
    # verify if API key is correct and return fake organization data
    def mock_getOrganizations(obj,*args,**kwargs): # pylint: disable=unused-argument disable=invalid-name
        if obj._session._api_key == APIKEY_CORRECT: # pylint: disable=protected-access
            return organization_data
        else:
            raise Exception("Mock wrong Meraki API key")

    # parse the networks data file data and return only a list with matching organization ID
    def mock_getOrganizationNetworks(obj,org_id): # pylint: disable=unused-argument disable=invalid-name
        return [x for x in networks_data if x["organizationId"] == org_id]

    # ssid data is a dictionary with the networkID as key for a list of SSIDs
    def mock_getNetworkWirelessSsids(obj,net_id): # pylint: disable=unused-argument disable=invalid-name
        return ssid_data.get(net_id)

    # mock update SSID data by updating ssid_data dictionary (to be used for assertions)
    def mock_updateNetworkWirelessSsid(obj,net_id,ssidPosition,psk): # pylint: disable=unused-argument disable=invalid-name
        ssid_data[net_id][int(ssidPosition)]["psk"] = psk

    # modify meraki methods to return mock data
    monkeypatch.setattr(meraki.Organizations,"getOrganizations",mock_getOrganizations)
    monkeypatch.setattr(meraki.Organizations,"getOrganizationNetworks",mock_getOrganizationNetworks)
    monkeypatch.setattr(meraki.Wireless,"getNetworkWirelessSsids",mock_getNetworkWirelessSsids)
    monkeypatch.setattr(meraki.Wireless,"updateNetworkWirelessSsid",mock_updateNetworkWirelessSsid)


def test_pskchg_org_one_net_one_dryrun_no(mock_meraki_dashboard): # pylint: disable=unused-argument
    '''
    test pskchange method with no organization
    organizations : one
    networks : one
    dryrun : no
    '''

    settings= {
        'apikey': '123456789',
        'tags': None,
        'verbose': False,
        'dryrun': False,
        'passphrase': "psk12345",
        'email': ['email1@domain.com', 'email2@domain.com'],
        'emailtemplate': './templates/psk/default/',
        'smtp_server': None,
        'smtp_port': None,
        'smtp_mode': 'TLS',
        'smtp_user': None,
        'smtp_pass': None,
        'organization': ['DevNet Sandbox'],
        'network': ["DNSMB3-gxxxxxxonscom.com"],
        "ssid":"Test SSID1",
        "command":"psk",
        }

    merakiobj = merakitoolkit.MerakiToolkit(settings)
    merakiobj.get_organizations()
    merakiobj.pskchange()
    assert mock_meraki_dashboard_results["ssid_data"]["L_646829496481111675"][1]["psk"] == settings["passphrase"] # pylint: disable=line-too-long



def test_pskchg_org_one_net_one_dryrun_yes(mock_meraki_dashboard): # pylint: disable=unused-argument
    '''
    test pskchange method with no organization
    organizations : one
    networks : one
    dryrun : yes
    '''

    settings= {
        'apikey': '123456789',
        'tags': None,
        'verbose': False,
        'dryrun': True,
        'passphrase': "psk12345",
        'email': ['email1@domain.com', 'email2@domain.com'],
        'emailtemplate': './templates/psk/default/',
        'smtp_server': None,
        'smtp_port': None,
        'smtp_mode': 'TLS',
        'smtp_user': None,
        'smtp_pass': None,
        'organization': ['DevNet Sandbox'],
        'network': ["DNSMB3-gxxxxxxonscom.com"],
        "ssid":"Test SSID1",
        "command":"psk",
        }

    merakiobj = merakitoolkit.MerakiToolkit(settings)
    merakiobj.pskchange()
    assert mock_meraki_dashboard_results["ssid_data"]["L_646829496481111675"][1]["psk"] == "testtest" # pylint: disable=line-too-long
    assert mock_meraki_dashboard_results["ssid_data"]["L_636829496481105433"][3]["psk"] == "testtest" # pylint: disable=line-too-long


def test_pskchg_org_one_net_two_dryrun_no_tags_no(mock_meraki_dashboard): # pylint: disable=unused-argument
    '''
    test pskchange method with no organization
    organizations : one
    networks : two
    dryrun : no
    '''

    settings= {
        'apikey': '123456789',
        'tags': None,
        'verbose': False,
        'dryrun': False,
        'passphrase': "psk12345",
        'email': ['email1@domain.com', 'email2@domain.com'],
        'emailtemplate': './templates/psk/default/',
        'smtp_server': None,
        'smtp_port': None,
        'smtp_mode': 'TLS',
        'smtp_user': None,
        'smtp_pass': None,
        'organization': ['DevNet Sandbox'],
        'network': ["DNSMB3-gxxxxxxonscom.com", "DevNet Sandbox ALWAYS ON"],
        "ssid":"Test SSID1",
        "command":"psk",
        }

    merakiobj = merakitoolkit.MerakiToolkit(settings)
    merakiobj.pskchange()
    assert mock_meraki_dashboard_results["ssid_data"]["L_646829496481111675"][1]["psk"] == settings["passphrase"] # pylint: disable=line-too-long
    assert mock_meraki_dashboard_results["ssid_data"]["L_646829496481105433"][3]["psk"] == settings["passphrase"] # pylint: disable=line-too-long

def test_pskchg_org_one_net_all_dryrun_no_tags_no(mock_meraki_dashboard): # pylint: disable=unused-argument
    '''
    test pskchange method with no organization
    organizations : one
    networks : ALL
    dryrun : no
    tags : no
    '''

    settings= {
        'apikey': '123456789',
        'tags': None,
        'verbose': False,
        'dryrun': False,
        'passphrase': "psk12345",
        'email': ['email1@domain.com', 'email2@domain.com'],
        'emailtemplate': './templates/psk/default/',
        'smtp_server': None,
        'smtp_port': None,
        'smtp_mode': 'TLS',
        'smtp_user': None,
        'smtp_pass': None,
        'organization': ['DevNet Sandbox'],
        'network': ["ALL"],
        "ssid":"Test SSID1",
        "command":"psk",
        }

    merakiobj = merakitoolkit.MerakiToolkit(settings)
    merakiobj.pskchange()
    assert mock_meraki_dashboard_results["ssid_data"]["L_646829496481111675"][1]["psk"] == settings["passphrase"] # pylint: disable=line-too-long
    assert mock_meraki_dashboard_results["ssid_data"]["L_646829496481105433"][3]["psk"] == settings["passphrase"] # pylint: disable=line-too-long
    assert mock_meraki_dashboard_results["ssid_data"]["L_646829496481111545"][5]["psk"] == settings["passphrase"] # pylint: disable=line-too-long

def test_pskchg_org_one_net_all_dryrun_no_tags_two(mock_meraki_dashboard): # pylint: disable=unused-argument
    '''
    test pskchange method with no organization
    organizations : one
    networks : ALL
    dryrun : no
    tags : two
    '''

    settings= {
        'apikey': '123456789',
        'tags': ["tag3","tag4"],
        'verbose': False,
        'dryrun': False,
        'passphrase': "psk12345",
        'email': ['email1@domain.com', 'email2@domain.com'],
        'emailtemplate': './templates/psk/default/',
        'smtp_server': None,
        'smtp_port': None,
        'smtp_mode': 'TLS',
        'smtp_user': None,
        'smtp_pass': None,
        'organization': ['DevNet Sandbox'],
        'network': ["ALL"],
        "ssid":"Test SSID1",
        "command":"psk",
        }


    merakiobj = merakitoolkit.MerakiToolkit(settings)
    merakiobj.pskchange()
    assert mock_meraki_dashboard_results["ssid_data"]["L_646829496481111675"][1]["psk"] == settings["passphrase"] # pylint: disable=line-too-long
    assert mock_meraki_dashboard_results["ssid_data"]["L_646829496481105433"][3]["psk"] == "testtest" # pylint: disable=line-too-long
    assert mock_meraki_dashboard_results["ssid_data"]["L_646829496481111545"][5]["psk"] == settings["passphrase"] # pylint: disable=line-too-long

def test_pskchg_org_two_net_all_dryrun_no_tags_no(mock_meraki_dashboard): # pylint: disable=unused-argument
    '''
    test pskchange method with no organization
    organizations : two
    networks : ALL
    dryrun : no
    tags : no
    '''

    settings= {
        'apikey': '123456789',
        'tags': None,
        'verbose': False,
        'dryrun': False,
        'passphrase': "psk12345",
        'email': ['email1@domain.com', 'email2@domain.com'],
        'emailtemplate': './templates/psk/default/',
        'smtp_server': None,
        'smtp_port': None,
        'smtp_mode': 'TLS',
        'smtp_user': None,
        'smtp_pass': None,
        'organization': ["DevNet Sandbox","Test Organization"],
        'network': ["ALL"],
        "ssid":"Test SSID1",
        "command":"psk",
        }

    merakiobj = merakitoolkit.MerakiToolkit(settings)
    merakiobj.pskchange()
    assert mock_meraki_dashboard_results["ssid_data"]["L_646829496481111675"][1]["psk"] == settings["passphrase"] # pylint: disable=line-too-long
    assert mock_meraki_dashboard_results["ssid_data"]["L_646829496481105433"][3]["psk"] == settings["passphrase"] # pylint: disable=line-too-long
    assert mock_meraki_dashboard_results["ssid_data"]["L_646829496481111545"][5]["psk"] == settings["passphrase"] # pylint: disable=line-too-long
    assert mock_meraki_dashboard_results["ssid_data"]["L_636829496481105433"][3]["psk"] == settings["passphrase"] # pylint: disable=line-too-long
    assert mock_meraki_dashboard_results["ssid_data"]["L_636829496481111675"][1]["psk"] == settings["passphrase"] # pylint: disable=line-too-long

def test_pskchg_org_two_net_all_dryrun_no_tags_two(mock_meraki_dashboard): # pylint: disable=unused-argument
    '''
    test pskchange method with no organization
    organizations : two
    networks : ALL
    dryrun : no
    tags : two
    '''

    settings= {
        'apikey': '123456789',
        'tags': ["tag3","tagA"],
        'verbose': False,
        'dryrun': False,
        'passphrase': "psk12345",
        'email': ['email1@domain.com', 'email2@domain.com'],
        'emailtemplate': './templates/psk/default/',
        'smtp_server': None,
        'smtp_port': None,
        'smtp_mode': 'TLS',
        'smtp_user': None,
        'smtp_pass': None,
        'organization': ["DevNet Sandbox","Test Organization"],
        'network': ["ALL"],
        "ssid":"Test SSID1",
        "command":"psk",
        }

    merakiobj = merakitoolkit.MerakiToolkit(settings)
    merakiobj.pskchange()
    assert mock_meraki_dashboard_results["ssid_data"]["L_646829496481111675"][1]["psk"] == settings["passphrase"] # pylint: disable=line-too-long
    assert mock_meraki_dashboard_results["ssid_data"]["L_646829496481105433"][3]["psk"] == "testtest" # pylint: disable=line-too-long
    assert mock_meraki_dashboard_results["ssid_data"]["L_646829496481111545"][5]["psk"] == "testtest" # pylint: disable=line-too-long
    assert mock_meraki_dashboard_results["ssid_data"]["L_636829496481105433"][3]["psk"] == settings["passphrase"] # pylint: disable=line-too-long
    assert mock_meraki_dashboard_results["ssid_data"]["L_636829496481111675"][1]["psk"] == "testtest" # pylint: disable=line-too-long

def test_pskchg_org_two_net_two_dryrun_no_tags_one(mock_meraki_dashboard): # pylint: disable=unused-argument
    '''
    test pskchange method with no organization
    organizations : two
    networks : ALL
    dryrun : no
    tags : two
    '''

    settings= {
        'apikey': '123456789',
        'tags': ["tag1"],
        'verbose': False,
        'dryrun': False,
        'passphrase': "psk12345",
        'email': ['email1@domain.com', 'email2@domain.com'],
        'emailtemplate': './templates/psk/default/',
        'smtp_server': None,
        'smtp_port': None,
        'smtp_mode': 'TLS',
        'smtp_user': None,
        'smtp_pass': None,
        'organization': ["DevNet Sandbox","Test Organization"],
        'network': ["DNSMB3-gxxxxxxonscom.com","DNSMB3-gxxxxxxoascom.com"],
        "ssid":"Test SSID1",
        "command":"psk",
        }

    merakiobj = merakitoolkit.MerakiToolkit(settings)
    merakiobj.pskchange()
    assert mock_meraki_dashboard_results["ssid_data"]["L_646829496481111675"][1]["psk"] == settings["passphrase"] # pylint: disable=line-too-long
    assert mock_meraki_dashboard_results["ssid_data"]["L_646829496481105433"][3]["psk"] == "testtest" # pylint: disable=line-too-long
    assert mock_meraki_dashboard_results["ssid_data"]["L_646829496481111545"][5]["psk"] == "testtest" # pylint: disable=line-too-long
    assert mock_meraki_dashboard_results["ssid_data"]["L_636829496481105433"][3]["psk"] == "testtest" # pylint: disable=line-too-long
    assert mock_meraki_dashboard_results["ssid_data"]["L_636829496481111675"][1]["psk"] == settings["passphrase"] # pylint: disable=line-too-long
