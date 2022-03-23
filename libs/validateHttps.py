import re
import requests

def Validate(tDomain):
    try:
        tempD = requests.head("https://"+tDomain, allow_redirects=True, timeout=8)
        Domain = tempD.url
        Domain = re.sub(":443/$|/$", "", Domain)
        return Domain
    except requests.ConnectionError:
        try:
            tempD = requests.head("http://"+tDomain, allow_redirects=True, timeout=8)
            Domain = tempD.url
            Domain = re.sub(":80/$|/$", "", Domain)
            return Domain
        except requests.ConnectionError:
            return tDomain
