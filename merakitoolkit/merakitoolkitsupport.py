"""
merakitoolkitsupport
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
module for MerakiToolkit support functions
"""
import random
import string
import jinja2
import pyqrcode
from xkcdpass import xkcd_password as xp

def generate_email_body(templatename,path,ssid,psk,images=None):
    '''Generate email body from a jinja template <templatename>'''
    data = {
        "ssid":ssid,
        "psk":psk,
    }

    # Adds images to the dictionary to unpack in the jinja template
    # should be passed only for HTML email body
    if images:
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

def generate_psk(psk_list:list,randomize:bool=False):
    '''Returns a PSK given a list of words, if empty generate a random PSK'''
    psk = random.choice(psk_list)
    if psk == "":
        # Generate a psk from a dictionary
        word_file = xp.locate_wordfile()
        words = xp.generate_wordlist(wordfile=word_file, min_length=8, max_length=12)
        acrostic_word = random.choice(words)
        psk_list_generated = xp.generate_xkcdpassword(words, acrostic=acrostic_word, numwords=10, delimiter="::").split("::")
        psk = random.choice(psk_list_generated)
        randomize = True
    if randomize:
        uppercase_position = random.randint(0,len(psk)-1)
        symbols_position = [random.randint(0,len(psk)-1) for x in range(1)]
        digit_position = random.randint(0,len(psk)-1)
        psk = psk[:uppercase_position] + psk[uppercase_position].upper() + psk[uppercase_position + 1:]
        for symbol_position in symbols_position:
            psk = psk[:symbol_position] + random.choice("@#!.&()=") + psk[symbol_position:]
        psk = psk[:digit_position] + random.choice(string.digits) + psk[digit_position:]
    return psk
