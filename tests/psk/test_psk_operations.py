'''test meraki operations'''

import os
import json
import pytest
import meraki
import meraki.aio
import merakitoolkit.merakitoolkit as merakitoolkit # pylint: disable=import-error

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
    # ASYNC: mock functions had to be changed to "async def" to comply with the execution flow of the original methods
    async def mock_getOrganizations(obj,*args,**kwargs): # pylint: disable=unused-argument disable=invalid-name
        if obj._session._api_key == APIKEY_CORRECT: # pylint: disable=protected-access
            return organization_data
        else:
            raise Exception("Mock wrong Meraki API key")

    # parse the networks data file data and return only a list with matching organization ID
    # ASYNC: mock functions had to be changed to "async def" to comply with the execution flow of the original methods
    async def mock_getOrganizationNetworks(obj,org_id): # pylint: disable=unused-argument disable=invalid-name
        return [x for x in networks_data if x["organizationId"] == org_id]

    # ssid data is a dictionary with the networkID as key for a list of SSIDs
    # ASYNC: mock functions had to be changed to "async def" to comply with the execution flow of the original methods
    async def mock_getNetworkWirelessSsids(obj,net_id): # pylint: disable=unused-argument disable=invalid-name
        return ssid_data.get(net_id)

    # mock update SSID data by updating ssid_data dictionary (to be used for assertions)
    # ASYNC: mock functions had to be changed to "async def" to comply with the execution flow of the original methods
    async def mock_updateNetworkWirelessSsid(obj,net_id,ssidPosition,psk): # pylint: disable=unused-argument disable=invalid-name
        ssid_data[net_id][int(ssidPosition)]["psk"] = psk
        return ssid_data[net_id][int(ssidPosition)]

    # modify meraki methods to return mock data
    # ASYNC: mocked original classes are now referring to the async version of meraki SDK
    monkeypatch.setattr(meraki.aio.AsyncOrganizations,"getOrganizations",mock_getOrganizations)
    monkeypatch.setattr(meraki.aio.AsyncOrganizations,"getOrganizationNetworks",mock_getOrganizationNetworks)
    monkeypatch.setattr(meraki.aio.AsyncWireless,"getNetworkWirelessSsids",mock_getNetworkWirelessSsids)
    monkeypatch.setattr(meraki.aio.AsyncWireless,"updateNetworkWirelessSsid",mock_updateNetworkWirelessSsid)

# @pytest.mark.asyncio -> necessary to define execute in a test loop any async test function (pytest-asyncio)
@pytest.mark.asyncio
async def test_pskchg_org_one_net_one_dryrun_no_psk_input(mock_meraki_dashboard): # pylint: disable=unused-argument
    '''
    test pskchangeasync method with no organization
    organizations : one
    networks : one
    dryrun : no
    MERAKITK_PSK : single
    passphrase : input
    psk randomization : no
    '''

    settings= {
        'apikey': '123456789',
        'tags': None,
        'verbose': False,
        'dryrun': False,
        'passphrase': "Pass123!",
        'passrandomize': False,
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

    # Force MERAKITK_PSK environment variable value
    os.environ["MERAKITK_PSK"] = "Abracadabra1234"

    merakiobj = merakitoolkit.MerakiToolkit(settings)
    await merakiobj.pskchangeasync()
    assert mock_meraki_dashboard_results["ssid_data"]["L_646829496481111675"][1]["psk"] == settings["passphrase"]


# @pytest.mark.asyncio -> necessary to define execute in a test loop any async test function (pytest-asyncio)
@pytest.mark.asyncio
async def test_pskchg_org_one_net_one_dryrun_no_psk_input_random(mock_meraki_dashboard): # pylint: disable=unused-argument
    '''
    test pskchangeasync method with no organization
    organizations : one
    networks : one
    dryrun : no
    MERAKITK_PSK : single
    passphrase : input
    psk randomization : yes
    '''

    settings= {
        'apikey': '123456789',
        'tags': None,
        'verbose': False,
        'dryrun': False,
        'passphrase': "Pass123!",
        'passrandomize': True,
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

    # Force MERAKITK_PSK environment variable value
    os.environ["MERAKITK_PSK"] = "Abracadabra1234"

    merakiobj = merakitoolkit.MerakiToolkit(settings)
    await merakiobj.pskchangeasync()
    assert mock_meraki_dashboard_results["ssid_data"]["L_646829496481111675"][1]["psk"] == merakiobj._current_operation["settings"]["passphrase"] # pylint: disable=protected-access,line-too-long


# @pytest.mark.asyncio -> necessary to define execute in a test loop any async test function (pytest-asyncio)
@pytest.mark.asyncio
async def test_pskchg_org_one_net_one_dryrun_no_psk_env(mock_meraki_dashboard): # pylint: disable=unused-argument
    '''
    test pskchangeasync method with no organization
    organizations : one
    networks : one
    dryrun : no
    MERAKITK_PSK : single
    passphrase : no
    psk randomization : no
    '''

    settings= {
        'apikey': '123456789',
        'tags': None,
        'verbose': False,
        'dryrun': False,
        'passphrase': None,
        'passrandomize': False,
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

    # Force MERAKITK_PSK environment variable value
    os.environ["MERAKITK_PSK"] = "Abracadabra1234"

    merakiobj = merakitoolkit.MerakiToolkit(settings)
    await merakiobj.pskchangeasync()
    assert mock_meraki_dashboard_results["ssid_data"]["L_646829496481111675"][1]["psk"] == os.environ["MERAKITK_PSK"]


# @pytest.mark.asyncio -> necessary to define execute in a test loop any async test function (pytest-asyncio)
@pytest.mark.asyncio
async def test_pskchg_org_one_net_one_dryrun_no_psk_env_multi(mock_meraki_dashboard): # pylint: disable=unused-argument
    '''
    test pskchangeasync method with no organization
    organizations : one
    networks : one
    dryrun : no
    MERAKITK_PSK : multiple
    passphrase : no
    psk randomization : no
    '''

    settings= {
        'apikey': '123456789',
        'tags': None,
        'verbose': False,
        'dryrun': False,
        'passphrase': None,
        'passrandomize': False,
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

    # Force environment variable to specific password
    os.environ["MERAKITK_PSK"] = "Pass123word1!::Pass123word2!::Pass123word3!::Pass123word4!::Pass123word5!"

    merakiobj = merakitoolkit.MerakiToolkit(settings)
    await merakiobj.pskchangeasync()
    assert mock_meraki_dashboard_results["ssid_data"]["L_646829496481111675"][1]["psk"] in os.environ["MERAKITK_PSK"].split("::")


# @pytest.mark.asyncio -> necessary to define execute in a test loop any async test function (pytest-asyncio)
@pytest.mark.asyncio
async def test_pskchg_org_one_net_one_dryrun_no_psk_env_multi_random(mock_meraki_dashboard): # pylint: disable=unused-argument
    '''
    test pskchangeasync method with no organization
    organizations : one
    networks : one
    dryrun : no
    MERAKITK_PSK : multiple
    passphrase : no
    psk randomization : yes
    '''

    settings= {
        'apikey': '123456789',
        'tags': None,
        'verbose': False,
        'dryrun': False,
        'passphrase': None,
        'passrandomize': False,
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

    # Force environment variable to specific password
    os.environ["MERAKITK_PSK"] = "Pass123word1!::Pass123word2!::Pass123word3!::Pass123word4!::Pass123word5!"

    merakiobj = merakitoolkit.MerakiToolkit(settings)
    await merakiobj.pskchangeasync()
    assert mock_meraki_dashboard_results["ssid_data"]["L_646829496481111675"][1]["psk"] == merakiobj._current_operation["settings"]["passphrase"] # pylint: disable=protected-access,line-too-long


# @pytest.mark.asyncio -> necessary to define execute in a test loop any async test function (pytest-asyncio)
@pytest.mark.asyncio
async def test_pskchg_org_one_net_one_dryrun_no_psk_env_random(mock_meraki_dashboard): # pylint: disable=unused-argument
    '''
    test pskchangeasync method with no organization
    organizations : one
    networks : one
    dryrun : no
    '''

    settings= {
        'apikey': '123456789',
        'tags': None,
        'verbose': False,
        'dryrun': False,
        'passphrase': None,
        'passrandomize': True,
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
    await merakiobj.pskchangeasync()
    assert mock_meraki_dashboard_results["ssid_data"]["L_646829496481111675"][1]["psk"] == merakiobj._current_operation["settings"]["passphrase"] # pylint: disable=protected-access,line-too-long


# @pytest.mark.asyncio -> necessary to define execute in a test loop any async test function (pytest-asyncio)
@pytest.mark.asyncio
async def test_pskchg_org_one_net_one_dryrun_no_psk_no_env_no(mock_meraki_dashboard): # pylint: disable=unused-argument
    '''
    test pskchangeasync method with no organization
    organizations : one
    networks : one
    dryrun : no
    MERAKITK_PSK : no
    passphrase : no
    psk randomization : no
    should genereate a passphrase automatically
    '''

    settings= {
        'apikey': '123456789',
        'tags': None,
        'verbose': False,
        'dryrun': False,
        'passphrase': None,
        'passrandomize': False,
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

    # Force MERAKITK_PSK to be absent
    if "MERAKITK_PSK" in os.environ:
        del os.environ["MERAKITK_PSK"]

    merakiobj = merakitoolkit.MerakiToolkit(settings)
    await merakiobj.pskchangeasync()
    assert mock_meraki_dashboard_results["ssid_data"]["L_646829496481111675"][1]["psk"] == merakiobj._current_operation["settings"]["passphrase"] # pylint: disable=protected-access,line-too-long


# @pytest.mark.asyncio -> necessary to define execute in a test loop any async test function (pytest-asyncio)
@pytest.mark.asyncio
async def test_pskchg_org_one_net_one_dryrun_yes(mock_meraki_dashboard): # pylint: disable=unused-argument
    '''
    test pskchangeasync method with no organization
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
        'passrandomize': False,
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
    await merakiobj.pskchangeasync()
    assert mock_meraki_dashboard_results["ssid_data"]["L_646829496481111675"][1]["psk"] == "testtest"
    assert mock_meraki_dashboard_results["ssid_data"]["L_636829496481105433"][3]["psk"] == "testtest"


# @pytest.mark.asyncio -> necessary to define execute in a test loop any async test function (pytest-asyncio)
@pytest.mark.asyncio
async def test_pskchg_org_one_net_two_dryrun_no_tags_no(mock_meraki_dashboard): # pylint: disable=unused-argument
    '''
    test pskchangeasync method with no organization
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
        'passrandomize': False,
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
    await merakiobj.pskchangeasync()
    assert mock_meraki_dashboard_results["ssid_data"]["L_646829496481111675"][1]["psk"] == settings["passphrase"]
    assert mock_meraki_dashboard_results["ssid_data"]["L_646829496481105433"][3]["psk"] == settings["passphrase"]


# @pytest.mark.asyncio -> necessary to define execute in a test loop any async test function (pytest-asyncio)
@pytest.mark.asyncio
async def test_pskchg_org_one_net_all_dryrun_no_tags_no(mock_meraki_dashboard): # pylint: disable=unused-argument
    '''
    test pskchangeasync method with no organization
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
        'passrandomize': False,
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
    await merakiobj.pskchangeasync()
    assert mock_meraki_dashboard_results["ssid_data"]["L_646829496481111675"][1]["psk"] == settings["passphrase"]
    assert mock_meraki_dashboard_results["ssid_data"]["L_646829496481105433"][3]["psk"] == settings["passphrase"]
    assert mock_meraki_dashboard_results["ssid_data"]["L_646829496481111545"][5]["psk"] == settings["passphrase"]


# @pytest.mark.asyncio -> necessary to define execute in a test loop any async test function (pytest-asyncio)
@pytest.mark.asyncio
async def test_pskchg_org_one_net_all_dryrun_no_tags_two(mock_meraki_dashboard): # pylint: disable=unused-argument
    '''
    test pskchangeasync method with no organization
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
        'passrandomize': False,
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
    await merakiobj.pskchangeasync()
    assert mock_meraki_dashboard_results["ssid_data"]["L_646829496481111675"][1]["psk"] == settings["passphrase"]
    assert mock_meraki_dashboard_results["ssid_data"]["L_646829496481105433"][3]["psk"] == "testtest"
    assert mock_meraki_dashboard_results["ssid_data"]["L_646829496481111545"][5]["psk"] == settings["passphrase"]


# @pytest.mark.asyncio -> necessary to define execute in a test loop any async test function (pytest-asyncio)
@pytest.mark.asyncio
async def test_pskchg_org_two_net_all_dryrun_no_tags_no(mock_meraki_dashboard): # pylint: disable=unused-argument
    '''
    test pskchangeasync method with no organization
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
        'passrandomize': False,
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
    await merakiobj.pskchangeasync()
    assert mock_meraki_dashboard_results["ssid_data"]["L_646829496481111675"][1]["psk"] == settings["passphrase"]
    assert mock_meraki_dashboard_results["ssid_data"]["L_646829496481105433"][3]["psk"] == settings["passphrase"]
    assert mock_meraki_dashboard_results["ssid_data"]["L_646829496481111545"][5]["psk"] == settings["passphrase"]
    assert mock_meraki_dashboard_results["ssid_data"]["L_636829496481105433"][3]["psk"] == settings["passphrase"]
    assert mock_meraki_dashboard_results["ssid_data"]["L_636829496481111675"][1]["psk"] == settings["passphrase"]


# @pytest.mark.asyncio -> necessary to define execute in a test loop any async test function (pytest-asyncio)
@pytest.mark.asyncio
async def test_pskchg_org_all_net_all_dryrun_no_tags_no(mock_meraki_dashboard): # pylint: disable=unused-argument
    '''
    test pskchangeasync method with no organization
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
        'passrandomize': False,
        'email': ['email1@domain.com', 'email2@domain.com'],
        'emailtemplate': './templates/psk/default/',
        'smtp_server': None,
        'smtp_port': None,
        'smtp_mode': 'TLS',
        'smtp_user': None,
        'smtp_pass': None,
        'organization': ["ALL"],
        'network': ["ALL"],
        "ssid":"Test SSID1",
        "command":"psk",
        }

    merakiobj = merakitoolkit.MerakiToolkit(settings)
    await merakiobj.pskchangeasync()
    assert mock_meraki_dashboard_results["ssid_data"]["L_646829496481111675"][1]["psk"] == settings["passphrase"]
    assert mock_meraki_dashboard_results["ssid_data"]["L_646829496481105433"][3]["psk"] == settings["passphrase"]
    assert mock_meraki_dashboard_results["ssid_data"]["L_646829496481111545"][5]["psk"] == settings["passphrase"]
    assert mock_meraki_dashboard_results["ssid_data"]["L_636829496481105433"][3]["psk"] == settings["passphrase"]
    assert mock_meraki_dashboard_results["ssid_data"]["L_636829496481111675"][1]["psk"] == settings["passphrase"]


# @pytest.mark.asyncio -> necessary to define execute in a test loop any async test function (pytest-asyncio)
@pytest.mark.asyncio
async def test_pskchg_org_two_net_all_dryrun_no_tags_two(mock_meraki_dashboard): # pylint: disable=unused-argument
    '''
    test pskchangeasync method with no organization
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
        'passrandomize': False,
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
    await merakiobj.pskchangeasync()
    assert mock_meraki_dashboard_results["ssid_data"]["L_646829496481111675"][1]["psk"] == settings["passphrase"]
    assert mock_meraki_dashboard_results["ssid_data"]["L_646829496481105433"][3]["psk"] == "testtest"
    assert mock_meraki_dashboard_results["ssid_data"]["L_646829496481111545"][5]["psk"] == "testtest"
    assert mock_meraki_dashboard_results["ssid_data"]["L_636829496481105433"][3]["psk"] == settings["passphrase"]
    assert mock_meraki_dashboard_results["ssid_data"]["L_636829496481111675"][1]["psk"] == "testtest"


# @pytest.mark.asyncio -> necessary to define execute in a test loop any async test function (pytest-asyncio)
@pytest.mark.asyncio
async def test_pskchg_org_two_net_two_dryrun_no_tags_one(mock_meraki_dashboard): # pylint: disable=unused-argument
    '''
    test pskchangeasync method with no organization
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
        'passrandomize': False,
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
    await merakiobj.pskchangeasync()
    assert mock_meraki_dashboard_results["ssid_data"]["L_646829496481111675"][1]["psk"] == settings["passphrase"]
    assert mock_meraki_dashboard_results["ssid_data"]["L_646829496481105433"][3]["psk"] == "testtest"
    assert mock_meraki_dashboard_results["ssid_data"]["L_646829496481111545"][5]["psk"] == "testtest"
    assert mock_meraki_dashboard_results["ssid_data"]["L_636829496481105433"][3]["psk"] == "testtest"
    assert mock_meraki_dashboard_results["ssid_data"]["L_636829496481111675"][1]["psk"] == settings["passphrase"]


# @pytest.mark.asyncio -> necessary to define execute in a test loop any async test function (pytest-asyncio)
@pytest.mark.asyncio
async def test_pskchg_org_one_net_one_dryrun_no_email(mock_meraki_dashboard): # pylint: disable=unused-argument
    '''
    test pskchangeasync method with no organization
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
        'passrandomize': False,
        'email': ['youremail@yourdomain.com', 'youremail2@yourdomain.com'],
        'emailtemplate': './merakitoolkit/templates/psk/default/',
        "smtp_sender":"MerakiToolkit",
        'smtp_server': None,
        'smtp_port': None,
        'smtp_mode': "TLS",
        'smtp_user': None,
        'smtp_pass': None,
        'organization': ['DevNet Sandbox'],
        'network': ["DNSMB3-gxxxxxxonscom.com"],
        "ssid":"Test SSID1",
        "command":"psk",
        }

    merakiobj = merakitoolkit.MerakiToolkit(settings)
    await merakiobj.pskchangeasync()
    merakiobj.send_email_psk()
    assert mock_meraki_dashboard_results["ssid_data"]["L_646829496481111675"][1]["psk"] == settings["passphrase"]


# @pytest.mark.asyncio -> necessary to define execute in a test loop any async test function (pytest-asyncio)
@pytest.mark.asyncio
async def test_pskchg_org_one_net_one_dryrun_no_email2(mock_meraki_dashboard): # pylint: disable=unused-argument
    '''
    test pskchangeasync method with no organization
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
        'passrandomize': False,
        'email': ['youremail@yourdomain.com', 'youremail2@yourdomain.com'],
        'emailtemplate': './tests/psk/email/default/',
        "smtp_sender":"MerakiToolkit",
        'smtp_server': None,
        'smtp_port': None,
        'smtp_mode': "TLS",
        'smtp_user': None,
        'smtp_pass': None,
        'organization': ['DevNet Sandbox'],
        'network': ["DNSMB3-gxxxxxxonscom.com"],
        "ssid":"Test SSID1",
        "command":"psk",
        }

    merakiobj = merakitoolkit.MerakiToolkit(settings)
    await merakiobj.pskchangeasync()
    merakiobj.send_email_psk()
    assert mock_meraki_dashboard_results["ssid_data"]["L_646829496481111675"][1]["psk"] == settings["passphrase"]
