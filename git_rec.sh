#!/bin/bash

if [ $# -eq 0 ]
then
    echo "you need to pass an argument"
    exit 1
fi


update_main () {
    git submodule update --remote --merge --recursive  
    git pull 
}

# recursive checkout
if [ $1 = "checkout" ]
then 

    if [[ $2 == -* ]]
    then 
        git submodule foreach --recursive "git checkout $2 $3"
        git checkout $2 $3
    else 
        git submodule foreach --recursive "git checkout $2"
        git checkout $2
    fi

# recursive branch
elif [ $1 == "branch" ]
then 

    if [[ $2 == -* ]]
    then 
        git submodule foreach --recursive "git branch $2 $3"
        git branch $2 $3
    else 
        git submodule foreach --recursive "git branch $2"
        git branch $2
    fi

elif [ $1 == "update" ]
then    
     
    update_main

elif [ $1 == "addstash" ]
then 

    git submodule foreach --recursive 'git add -A'
    git submodule foreach --recursive 'git stash'
    git add -a
    git stash

elif [ $1 == "applystash" ]
then 

    git submodule foreach --recursive 'git stash apply'
    git stash apply

elif [ $1 == "status" ]
then
    cd TerriaMap/packages/terriajs
    printf "\nTerriaJS\n"
    git status
    cd ../..
    printf "\nTerriaMap\n"
    git status
    cd ..
    printf "\ndigital_tvilling_poc\n"
    git status

else
    echo "$1 is not a valid command"
fi