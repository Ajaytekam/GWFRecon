#!/usr/bin/python3 

import sys
import libs.gitlibs as gitlibs
import libs.coloredOP as co
import signal
import enumlibs  
import argparse 
import os 

def Banner():
    print("=======================================================")
    print(co.colors.GREEN+co.BOLD+"\tGWFRecon : Github CI/CD Recon Framework\n"+co.END)
    print(co.bullets.INFO, "Author : "+co.colors.CYAN+"Ajay Kumar Tekam (github.com/ajaytekam)"+co.END)
    print(co.bullets.INFO, "Blog   : "+co.colors.CYAN+"https://sec-art.net"+co.END)
    print("=======================================================")

def main():
    parser = argparse.ArgumentParser()
    subparser = parser.add_subparsers(dest='Module')
    SubDomainEnum = subparser.add_parser('SubDomainEnum')
    PortAndServices = subparser.add_parser('PortAndServices')
    JSScan = subparser.add_parser('JSScan')
    DirBruteforce = subparser.add_parser('DirBruteforce')
    MisConfigScan = subparser.add_parser('MisConfigScan')
    SubDomainEnum.add_argument('-d', '--domain', help="Domain name to perform Subdomain Enumeration", type=str, required=True)
    SubDomainEnum.add_argument("-p", "--passive", help="Passive subdomain Enumeration", action="store_true")
    PortAndServices.add_argument('--mdfile', help="Massdns result file", type=str, required=True)
    JSScan.add_argument('-d', '--domain', help="Domain name to perform JavaScript file enumeration", type=str, required=True)
    DirBruteforce.add_argument("-d", "--domain", help="Domain name to perform Bruteforce", type=str)
    DirBruteforce.add_argument("--subdfile", help="Subdomain file list", type=str)
    DirBruteforce.add_argument("--wordlist", help="Provide a custom wordlist file", type=str)
    MisConfigScan.add_argument("--subdfile", help="subdomain file list", type=str, required=True)
    args = parser.parse_args() 
    if args.Module == 'SubDomainEnum':
        Banner()
        enumlibs.SubDomainEnum.Execute(args.domain, args.passive)
    elif args.Module == 'PortAndServices':
        Banner()
        if os.path.isfile(args.mdfile):
            enumlibs.PortAndServices.Execute(args.mdfile)
        else:
            print(co.bullets.ERROR, co.colors.RED+"Supplied massdns result file does not exists.\n"+co.END)
            PortAndServices.print_help()
            sys.exit(1)
    elif args.Module == 'JSScan':
        Banner()
        enumlibs.JSScan.Execute(args.domain)
    elif args.Module == 'DirBruteforce':
        Banner()
        target = ''
        DType = ''
        wordlist = ''
        if args.domain:
            DType = "single_domain"
            target = args.domain
        else:
            DType = "multiple_domain"
            if args.subdfile:
                if os.path.isfile(args.subdfile):
                    target = args.subdfile
                else:
                    print(co.bullets.ERROR, co.colors.RED+"Supplied subdomain file does not exists.\n"+co.END)
                    DirBruteforce.print_help()
                    sys.exit(1)
        if args.wordlist:
            if os.path.isfile(args.wordlist):
                wordlist = args.wordlist
            else: 
                print(co.bullets.ERROR, co.colors.RED+"Supplied wordlist file does not exists.\n"+co.END)
                DirBruteforce.print_help()
                sys.exit(1)
        else:
            wordlist = "default"
        if DType == '' or target == '' or wordlist == '':
            DirBruteforce.print_help()
        else:
            enumlibs.DirBrute.Execute(DType, target, wordlist)
    elif args.Module == 'MisConfigScan':
        Banner()
        if os.path.isfile(args.subdfile):
            enumlibs.MisConfigScan.Execute(args.subdfile)
        else:
            print(co.bullets.ERROR, co.colors.RED+"Supplied subdomain file does not exists.\n"+co.END)
            MisConfigScan.print_help()
            sys.exit(1)
    else:
        Banner()
        print(co.bullets.CProcess, "Available Modules : \n")
        print(co.bullets.OK, " SubDomainEnum    => Subdomain Enumeration")
        print(co.bullets.OK, " PortAndServices  => Portscanner")
        print(co.bullets.OK, " JSScan           => JavaScript Scanner")
        print(co.bullets.OK, " DirBruteforce    => Directory/Path Bruteforce")
        print(co.bullets.OK, " MisConfigScan    => Misconfiguration Scanner\n")
        parser.print_help()

if __name__ == "__main__":
    main()
