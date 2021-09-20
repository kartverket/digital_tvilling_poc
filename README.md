# digital_tvilling_poc
Repo for terriajs digitaltvilling POC

# Cloning the repo

The repo uses git submodules, so to clone the repo without running git submodule init, you can simply write:

*git clone --recursive \[link to repo\]*

# To run the TerriaMap application:

**Notes:**  
This repo uses yarn package manager, not npm. Yarn can be installed with npm by running npm install -g yarn
*yarn install* in TerriaMap uses .sh script, and therefore needs to be run with Bash (PuTTY, git bash eller WSL på windows. Bash på Linux eller Mac), not windows command line or PowerShell.

cd TerriaMap  
yarn install  
yarn run gulp  
yarn start  

Then you should be able to open the client in localhost:3001

# For development

When the repo is first cloned, the sub-modules are in a detached state. This means that they point to a single commit, but not to a branch that can be used to push any additional changes. To create branches for development, use the following commands while in the digital_tvilling_poc folder:

~~~
git checkout -b "my_new_branch"
git submodule foreach --recursive 'git checkout -b "my_new_branch"'
~~~

**Configuring push:**  
If a pointer to a new commit in a submodule is pushed before the commit itself, this causes problems. To make sure this does not happen, use the following command in every directory that has a submodule:  

~~~
git config push.recurseSubmodules check  
~~~

**Pulling and merging changes from remote branches:**  
Run the following command from the main repository:

~~~
git submodule update --remote --merge --recursive  
git pull  
~~~

**--remote** tells git that you want to get changes from the remote branch (default is the main branch), **--merge** tells git you want to merge the remote changes with your local commits, and **--recursive** tells git that you want to update intenal submodules.  

**git pull** needs to be called in the main reposiry, to pull the new pointer to the state of the submodule


# To run the python server
Make sure that pip and python are installed. Then do as follows:

~~~
cd FlaskServer
pip install -r requirements.txt
python flask_server.py
~~~

The server is now running on localhost on the port 5000


**Adding and commiting changes:**  
If you want to add and commit changes to a submodule, then the change has to be commited first in the submodule. Then you need to add and commit the change to the pointer to the submodule in the outer repo. 