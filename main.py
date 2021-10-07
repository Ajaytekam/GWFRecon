#!/usr/bin/python3 

import sys
import libs.gitlibs as gitlibs
import libs.coloredOP as co
import signal
import enumlibs  
import argparse 

def Banner():
    print("=======================================================")
    print(co.colors.GREEN+co.BOLD+"\tGWFRecon : Github CI/CD Recon Framework\n"+co.END)
    print(co.bullets.INFO, "Author : "+co.colors.CYAN+"Ajay Kumar Tekam (github.com/ajaytekam)"+co.END)
    print(co.bullets.INFO, "Blog   : "+co.colors.CYAN+"https://sec-art.net"+co.END)
    print("=======================================================")

def main():
    # enumlibs.TestRunner.Execute()
    # enumlibs.SubDomainEnum.Execute()
    parser = argparse.ArgumentParser()
    subparser = parser.add_subparsers(dest='Module')
    SubDomainEnum = subparser.add_parser('SubDomainEnum')
    PortAndServices = subparser.add_parser('PortAndServices')
    JSScan = subparser.add_parser('JSScan')
    DirBruteforce = subparser.add_parser('DirBruteforce')
    MisConfigScan = subparser.add_parser('MisConfigScan')
    SubDomainEnum.add_argument('-d', '--domain', help="Domain name to perform Subdomain Enumeration", type=str, required=True)
    SubDomainEnum.add_argument("-p", "--passive", help="Passive subdomain Enumeration", action="store_true")
    args = parser.parse_args() 
    if args.Module == 'SubDomainEnum':
        Banner()
        enumlibs.SubDomainEnum.Execute(args.domain, args.passive)
    else:
        Banner()
        print(co.bullets.CProcess, "Available Modules : \n")
        print(co.bullets.OK, " SubDomainEnum    => Subdomain Enumeration")
        print(co.bullets.OK, " PortAndServices  => Portscanner")
        print(co.bullets.OK, " JSScan           => JavaScript Scanner")
        print(co.bullets.OK, " DirBruteForce    => Directory/Path Bruteforce")
        print(co.bullets.OK, " MisConfigScan    => Misconfiguration Scanner\n")
        parser.print_help()

if __name__ == "__main__":
    main()
