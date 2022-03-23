import sys
import libs.gitlibs as gitlibs
import libs.workflowlibs as wflibs
import libs.validateHttps as validateHttps
import libs.coloredOP as co

#========
# Workflow Template : SubDomainEnum.yml
TemplateName = "JSScan.yml"
TemplateData = """
name: CI

# Environment variables 
env: 
  DOMAIN: {}
  HTTPS_DOMAIN: {}  

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
      - uses: actions/setup-python@v2 
        with:
          python-version: '3.x'
      - uses: actions/setup-go@v2
        with:
          go-version: '1.17.x'

      # Runs a set of commands using the runners shell
      - name: Prepare System
        run: sudo apt-get update -y;
 
      - name: Install gau, subjs, hackrawler, httpx  
        run: |
          go install github.com/lc/gau/v2/cmd/gau@latest
          go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest
          go install github.com/hakluke/hakrawler@latest
          GO111MODULE=on go get -u -v github.com/lc/subjs@latest  

      - name: Install linkfinder, scretfinder 
        run: |
          python -m pip install --upgrade pip
          git clone https://github.com/GerbenJavado/LinkFinder.git linkfinder
          pushd linkfinder
          pip install -r requirements.txt  
          popd
          git clone https://github.com/m4ll0k/SecretFinder.git secretfinder
          pushd secretfinder
          pip install -r requirements.txt  
          popd   

      - name: Collect javascript urls with gau 
        run: gau ${{{{ env.DOMAIN }}}} | grep -iE "\.js$" >> tempgau   

      - name: Collect javascript urls with subjs 
        run: echo ${{{{ env.HTTPS_DOMAIN }}}} | subjs -c 10 -ua "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)" >> tempsubjs    

      - name: Collect javascript urls with hackrawler 
        run: echo ${{{{ env.HTTPS_DOMAIN }}}} | hakrawler -d 3 -insecure | grep -iE "\.js$" >> temphakrawler  

      - name: Filtering alive urls 
        run: |
          cat tempgau tempsubjs temphakrawler | sort -u >> jsurls
          cat jsurls | httpx -silent -mc 200 >> js_200
          rm tempsubjs tempgau temphakrawler jsurls 
        
      - name: Running scretfinder on JS urls 
        run: |
          while read -r jsurl
          do
              python secretfinder/SecretFinder.py -i $jsurl -o cli >> secretfinderResults.txt
              printf "\\n\\n" >> secretfinderResults.txt
          done < js_200

      - name: Running linkfinder on JS urls 
        run: |
          while read -r jsurl
          do 
              echo "[ + ] URL: $jsurl" >> linkfinderResult.txt
              python linkfinder/linkfinder.py -d -i $jsurl -o cli >> linkfinderResult.txt 
              printf "\\n\\n" >> linkfinderResult.txt
          done < js_200

      - name: Cleaning data Housekeeping
        run: |
          rm -rf linkfinder
          rm -rf secretfinder 

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

def Execute(domain):
    global TemplateName
    global TemplateData
    # Preparing template 
    https_domain = validateHttps.Validate(domain)
    TemplateData = TemplateData.format(domain, https_domain) 
    # Setting up the github repository 
    repoName = gitlibs.SetRepoName()
    if gitlibs.CreateRemoteRepo(repoName):
        print(co.bullets.ERROR, co.colors.BRED+"Could not create repository: Exiting Program."+co.END)
        sys.exit(1)
    # pushing workflow yml file 
    TemplatePath = '.github/workflows/{}'.format(TemplateName) 
    commitMessage = "github sample workflow added"
    if gitlibs.CommitFile(repoName, TemplateData, TemplatePath, commitMessage):
        print(co.bullets.ERROR, co.colors.BRED+"Could not commit config files on the repository.!!."+co.END)
        sys.exit(1)
    # initiate the workflow if everything is OK
    wflibs.WorkflowController(repoName, TemplateName)
