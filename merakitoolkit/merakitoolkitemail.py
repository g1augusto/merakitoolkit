"""
merakitoolkitemail
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Email module for MerakiToolkit
"""
import jinja2
import pyqrcode

def generate_email_body(templatename,path,ssid,psk,images=[]):
    data = {
        "ssid":ssid,
        "psk":psk,
    }

    # Adds images to the dictionary to unpack in the jinja template
    # should be passed only for HTML email body
    for image in images:
        data[image] = image
    environment = jinja2.Environment(loader=jinja2.FileSystemLoader(path))
    template = environment.get_template(templatename)
    content = template.render(**data)
    return content

def generate_qrcode(ssid,psk,path,wifi_protocol="WPA2"):
    '''generate a QRcode from a given SSID and PSK and save it to QRcode.png file'''
    qrcode = pyqrcode.create(F'WIFI:S:{ssid};T:{wifi_protocol};P:{psk};;')
    qrcode.png (path+'qrcode.png', scale=4)
    return qrcode
