# digital_tvilling_poc
Repo for terriajs digitaltvilling POC

# Cloning the repo

The repo uses git submodules, so to clone the repo without running git submodule init, you can simply write:

*git clone --recursive \[link to repo\]*

# For å kjøre TerriaMap applikasjonen:

**Notering:**  
This repo uses yarn package manager, not npm. Yarn can be installed with npm by running npm install -g yarn
*yarn install* på TerriaMap bruker .sh script, og trenger derfor å bli kjørt med Bash (PuTTY, git bash eller WSL på windows. Bash på Linux eller Mac), ikke windows kommandolinje eller PowerShell.

cd TerriaMap  
yarn install  
yarn run gulp  
yarn start  

Da skal man kunne åpne visningsklienten i localhost:3001
