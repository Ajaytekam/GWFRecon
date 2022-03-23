import sys
import libs.gitlibs as gitlibs
import libs.workflowlibs as wflibs
import libs.validateHttps as validateHttps
import libs.coloredOP as co

#========
# Workflow Template : SubDomainEnum.yml
TemplateName = "DirBrute.yml"
TemplateData = """
name: CI

env:
  TYPE: {}
  DOMAIN: {}
  WORDLIST: {}

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
      - uses: actions/setup-go@v2
        with:
          go-version: '1.17.x'

      # Runs a set of commands using the runners shell
      - name: Prepare System
        run: sudo apt-get update -y;
 
      - name: Install ffuf, jq, httpx and download wordlist 
        run: |
          sudo apt install jq wget -y
          go install github.com/ffuf/ffuf@latest
          go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest
          if ${{{{ env.WORDLIST == 'default' }}}}; then
              wget https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/Web-Content/common.txt -O wordlist.txt 
          fi

      - name: Perform Bruteforce Attack 
        run: |
          if ${{{{ env.TYPE == 'single_domain' }}}}; then 
              TDomain=${{{{ env.DOMAIN }}}} 
              domain=${{TDomain##*/}}
              ffuf -c -H "X-Forwarded-For: 127.0.0.1" -H "User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:72.0) Gecko/20100101 Firefox/72.0" -u "${{{{ env.DOMAIN }}}}/FUZZ" -t 50 -D -e js,php,bak,txt,asp,aspx,jsp,html,zip,jar,sql,json,old,gz,shtml,log,swp,yaml,yml,config,save,rsa,ppk -ac -se -w wordlist.txt -o $domain.json 
              sed 's/content-type/contentType/g' $domain.json | jq '.results[]|"url:\(.url) status:\(.status) length:\(.length) [content-type:\(.contentType)] redirect:\(.redirectlocation)"' >> $domain.txt
              rm $domain.json
          else 
              cat subdomains.txt | httpx -silent >> aliveSubs.txt
              while read -r url
              do
                  domain=${{url##*/}}
                  ffuf -c -H "X-Forwarded-For: 127.0.0.1" -H "User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:72.0) Gecko/20100101 Firefox/72.0" -u "$url/FUZZ" -t 50 -D -e js,php,bak,txt,asp,aspx,jsp,html,zip,jar,sql,json,old,gz,shtml,log,swp,yaml,yml,config,save,rsa,ppk -ac -se -w wordlist.txt -o $domain.json
                  sed 's/content-type/contentType/g' $domain.json | jq '.results[]|"url:\(.url) status:\(.status) length:\(.length) [content-type:\(.contentType)] redirect:\(.redirectlocation)"' >> $domain.txt
                  rm $domain.json
              done < aliveSubs.txt
          fi

      - name: Cleaning data Housekeeping
        run: |
          rm wordlist.txt
          if ${{{{ env.TYPE == 'multiple_domain' }}}}; then
              rm subdomains.txt
              rm aliveSubs.txt
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

def Execute(DType, target, worldList):
    global TemplateName
    global TemplateData
    # Preparing template 
    if DType == "single_domain":
        https_domain = validateHttps.Validate(target) 
    else:
        https_domain = None
    if worldList == "default":
        wl = worldList
    else:
        wl = "Custom"
    TemplateData = TemplateData.format(DType, https_domain, wl) 
    # Setting up the github repository 
    repoName = gitlibs.SetRepoName()
    if gitlibs.CreateRemoteRepo(repoName):
        print(co.bullets.ERROR, co.colors.BRED+"Could not create repository: Exiting Program."+co.END)
        sys.exit(1)
    # pushing subdomain list 
    if DType == "multiple_domain":
        try:
            SubDFileContent = open(target, "r").read()
        except:
            print("Error in reading subdomains input file!!!")
            sys.exit(1)
        if gitlibs.CommitFile(repoName, SubDFileContent, "subdomains.txt", "subdomains list file commited."): 
            print(co.bullets.ERROR, co.colors.BRED+"Could not commit subdomains file on the repository.!!."+co.END)
            sys.exit(1)
    # pushing custom worldList file
    if worldList != "default":
        try:
            wlFileContent = open(worldList, "r").read()
        except:
            print("Error in reading wordlist input file!!!")
            sys.exit(1)
        if gitlibs.CommitFile(repoName, wlFileContent, "wordlist.txt", "wordlist file commited."): 
            print(co.bullets.ERROR, co.colors.BRED+"Could not commit provided wordlist file on the repository.!!."+co.END)
            sys.exit(1)
    # pushing workflow yml file 
    TemplatePath = '.github/workflows/{}'.format(TemplateName) 
    commitMessage = "github sample workflow added"
    if gitlibs.CommitFile(repoName, TemplateData, TemplatePath, commitMessage):
        print(co.bullets.ERROR, co.colors.BRED+"Could not commit config files on the repository.!!."+co.END)
        sys.exit(1)
    # initiate the workflow if everything is OK
    wflibs.WorkflowController(repoName, TemplateName)
