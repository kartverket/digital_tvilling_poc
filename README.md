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
