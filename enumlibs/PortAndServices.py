import sys
import libs.gitlibs as gitlibs
import libs.workflowlibs as wflibs
import libs.coloredOP as co

# This is a simple test runner
# which runs some simple command
# on the CICD 

#========
# Workflow Template : PortAndServices.yml
TemplateName = "PortAndServices.yml"
TemplateData = """name: CI

# Controls when the workflow will run
on:
  # Allows you to run this workflow manually from the Actions tab
  workflow_dispatch:

# A workflow run is made up of one or more jobs that can run sequentially or in parallel
jobs:
  # This workflow contains a single job called "build"
  build:
    # The type of runner that the job will run on
    runs-on: ubuntu-latest

    # Steps represent a sequence of tasks that will be executed as part of the job
    steps:
      # Checks-out your repository under $GITHUB_WORKSPACE, so your job can access it
      - uses: actions/checkout@v2

      # Runs a set of commands using the runners shell
      - name: Prepare System
        run: |
          sudo apt-get update -y;

      - name: Install masscan
        run: |
          sudo apt-get --assume-yes install git make gcc
          git clone https://github.com/robertdavidgraham/masscan
          pushd masscan
          make
          popd

      - name: Install nmap
        run: sudo apt-get --assume-yes install nmap

      - name: Run masscan
        run: |
          # get ip from massdnsResult file
          cat {} | egrep -o "([0-9]{{1,3}}[\.]){{3}}[0-9]{{1,3}}" | sort -u >> ips.txt
          sudo masscan/bin/masscan -iL ips.txt --rate 10000 --top-ports 1000 -oL masscanResults.txt
          rm -rf masscan

      - name: Parsing Masscan Result
        run: |
          # store the result on ip:port order
          cat masscanResults.txt | grep open | awk '{{print $4":"$3}}' | sort -u >> parsedResult.txt
          # filter and sort the IP from parsedResult.txt file into a new file
          cat parsedResult.txt | cut -d: -f1 | sort -u >> aliveIPs.txt
          # parse uniqe IPs and their port numbers in ip:port1,port2,port3...,portN format
          for ip in `cat aliveIPs.txt`
          do
            ports=`cat parsedResult.txt | grep $ip | cut -d: -f2`
            ptlist=`echo $ports`
            echo "$ip:$ptlist" | tr " " , >> ip_ports.txt
          done

      - name: Nmap Scan
        run: |
          # Variables for html result file
          OPTemplateHEAD='<html><head><title>PortAndServices Scan Result</title><link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.11.1/css/jquery.dataTables.css"><script src="https://code.jquery.com/jquery-3.6.0.slim.min.js" integrity="sha256-u7e5khyithlIdTpu22PHhENmPcRdFiHRjhAuHcs05RI=" crossorigin="anonymous"></script><script type="text/javascript" charset="utf8" src="https://cdn.datatables.net/1.11.1/js/jquery.dataTables.js"></script><style>h1{{text-align: center;color: blue;}}td{{text-align: center;}}</style></head><body><h1>Port and Service Scan Result</h1><table id="result" class="display" style="width:100%"></table><script>var dataSet = ['
          OPTemplateTAIL='];$(document).ready(function(){{$("#result").DataTable({{data:dataSet,columns:[{{title:"IP Address"}},{{title:"Domain|s"}},{{title:"Open Ports"}},{{title:"Scan Details"}}]}});}});</script></body></html>'
          # nmap scan from file ip_ports.txt
          echo $OPTemplateHEAD >> result.html
          mkdir results
          while IFS=: read -r ip ports
            nmap -sV -p$ports $ip -oN results/$ip
            # grep domains
            DOMAINSTEMP=`cat massdnsResults.txt | grep $ip | awk '{{print $1}}' | sed 's/.$//g'`
            DOMAINS=`echo $DOMAINSTEMP | tr " " ,`
            echo "[\"$ip\",\"$DOMAINS\",\"$ports\",\"<a href='results/$ip'><button>Result</button></a>\"]," >> result.html
          done < ip_ports.txt
          echo $OPTemplateTAIL >> result.html
          # Scan completed cleaning the files
          rm masscanResults.txt
          rm parsedResult.txt
          rm aliveIPs.txt
          rm ip_ports.txt
          tar -cvf PortScanResult.tar result.html massdnsResults.txt results
          rm result.html
          rm massdnsResults.txt
          rm -rf results

      # Code for splitting file which are +99MB
      - name: Splitting big files
        run: |
          if [ `du -m PortScanResult.tar | cut -d" " -f1 | tr -d -c 0-9` -gt 99 ]
          then
            split -d -b20971520 PortScanResult.tar PortScanResult
          fi

      # github doesn't allow you to commit files > 100M
      - name: Pruning files greater than 100MB
        run: find . -size +99M -delete

      - name: Commit and push
        uses: stefanzweifel/git-auto-commit-action@v4.2.0
        with:
          commit_message: Commit output files
          commit_user_name: 'Basic Shell'
          commit_user_email: 'github-actions.shell@github.com'
"""
### 
#========

def Execute(massdnsfile):
    global TemplateName
    global TemplateData
    Filename = massdnsfile.split('/')[-1]
    TemplateData = TemplateData.format(Filename)
    # Setting up the github repository 
    repoName = gitlibs.SetRepoName()
    if gitlibs.CreateRemoteRepo(repoName):
        print(co.bullets.ERROR, co.colors.BRED+"Could not create repository: Exiting Program."+co.END)
        sys.exit(1)
    # push massdns file 
    try:
        MassdnsFile = open(massdnsfile, "r").read()
    except:
        print("Error in reading input file!!!")
        sys.exit(1)
    # pushing massdns result file 
    if gitlibs.CommitFile(repoName, MassdnsFile, Filename, "massdns result file commited"):
        print(co.bullets.ERROR, co.colors.BRED+"Could not commit massdns result file on the repository.!!."+co.END)
        sys.exit(1)
    # pushing workflow yml file 
    TemplatePath = '.github/workflows/{}'.format(TemplateName) 
    commitMessage = "github sample workflow added"
    if gitlibs.CommitFile(repoName, TemplateData, TemplatePath, commitMessage):
        print(co.bullets.ERROR, co.colors.BRED+"Could not commit config files on the repository.!!."+co.END)
        sys.exit(1)
    # initiate the workflow if everything is OK
    wflibs.WorkflowController(repoName, TemplateName)
