"""
merakitoolkitemail
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Email module for MerakiToolkit
"""
import jinja2
import pyqrcode

def generate_email_body(templatename,path,data):
    '''
    data = {
        "ssid":ssidname,
        "psk":passphrase,
        "logo":name,
        "qrcode":name,
        "image1":name,
        "image2",name,
        ...
        "imageN",name
    }
    '''
    environment = jinja2.Environment(loader=jinja2.FileSystemLoader(path))
    template = environment.get_template(templatename)
    content = template.render(**data)
    return content

def generate_qrcode(ssid,psk,path,wifi_protocol="WPA2"):
    '''generate a QRcode from a given SSID and PSK and save it to QRcode.png file'''
    QRCode = pyqrcode.create(F'WIFI:S:{ssid};T:{wifi_protocol};P:{psk};;')
    QRCode.png (path+'QRCode.png', scale=4)
    return QRCode
