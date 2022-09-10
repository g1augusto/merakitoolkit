'''tests common functionalities for merakitoolkit'''
import sys
import merakitoolkit.merakitoolkitparser as merakitoolkitparser # pylint: disable=import-error
import merakitoolkit.merakitoolkit as merakitoolkit # pylint: disable=import-error

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
    assert args.verbose == 0
    assert return_code == 0
    assert args.tags is None
    assert args.passphrase is None
    assert args.passrandomize is False

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
    "-pr",
    "--email","email1@domain.com","email2@domain.com",
    "-t","tag1","tag2",
    "--dryrun",
    "--verbose",
    "-et","./testtemplate",
    "--smtp-server","smtp.test.net",
    "--smtp-port","111",
    "--smtp-mode","STARTTLS",
    "--smtp-user","user-smtp",
    "--smtp-pass","pass-smtp",
    "--smtp-sender","MerakiTookit!"
    ])

    # Modify sys.exit behavior to prevent test failure
    monkeypatch.setattr(sys,"exit",print)

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
    assert args.verbose == 1
    assert args.emailtemplate == "./testtemplate/"
    assert args.smtp_server == "smtp.test.net"
    assert args.smtp_port == "111"
    assert args.smtp_mode == "STARTTLS"
    assert args.smtp_user == "user-smtp"
    assert args.smtp_pass == "pass-smtp"
    assert args.smtp_sender == "MerakiTookit!"
    assert args.passrandomize is True
    assert return_code == 0
