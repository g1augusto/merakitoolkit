'''tests common functionalities for merakitoolkit'''
import merakitoolkitparser # pylint: disable=import-error
import merakitoolkit # pylint: disable=import-error
import __main__ as program

def test_import_success():
    '''Verify that merakitoolkit can be imported successfully'''
    assert merakitoolkit.__license__

def test_parser_noparameters(monkeypatch):
    '''test main call with no parameters'''
    monkeypatch.setattr("sys.argv",["/merakitoolkit/__main__.py"])
    args,return_code = merakitoolkitparser.parser()
    assert args is None
    assert return_code == 1


def test_parser_psk_min_params(monkeypatch):
    '''test main call with required arguments only'''
    monkeypatch.setattr("sys.argv",
    ["/merakitoolkit/__main__.py",
    "psk",
    "--organization","Organization",
    "--network","Network1","Network2",
    "-s","SSID"
    ])
    args,return_code = merakitoolkitparser.parser()
    assert args is not None
    assert args.apikey is None
    assert args.dryrun is False
    assert args.email is None
    assert "Network1" in args.network
    assert "Network2" in args.network
    assert isinstance(args.network,list)
    assert "Organization" in args.organization
    assert isinstance(args.organization,list)
    assert args.ssid == "SSID"
    assert isinstance(args.ssid,str)
    assert args.verbose is False
    assert return_code == 0
    assert args.tags is None
    assert args.passphrase is None

def test_parser_psk_all_params(monkeypatch):
    '''
    test main call with required arguments only
    some parameters accept multiple input without argument keyword repetition
    '''
    monkeypatch.setattr("sys.argv",
    ["/merakitoolkit/__main__.py",
    "-k","123456789",
    "psk",
    "--organization","Organization1","Organization2",
    "--network","Network1","Network2",
    "-s","SSID",
    "--email","email1@domain.com","email2@domain.com",
    "-t","tag1","tag2",
    "--dryrun",
    "--verbose"
    ])
    args,return_code = merakitoolkitparser.parser()
    assert args is not None
    assert args.apikey == "123456789"
    assert args.dryrun is True
    assert "email1@domain.com" in args.email
    assert "email2@domain.com" in args.email
    assert isinstance(args.email,list)
    assert "Network1" in args.network
    assert "Network2" in args.network
    assert isinstance(args.network,list)
    assert "Organization1" in args.organization
    assert "Organization2" in args.organization
    assert isinstance(args.organization,list)
    assert "tag1" in args.tags
    assert "tag2" in args.tags
    assert isinstance(args.tags,list)
    assert args.ssid == "SSID"
    assert isinstance(args.ssid,str)
    assert args.verbose is True
    assert return_code == 0
