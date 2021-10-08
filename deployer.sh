#!/bin/bash


if [ $# -eq 0 ]
then
    echo "you need to pass an argument"
    exit 1
fi


flask () {
    cd FlaskServer
    aws ecr get-login-password --region eu-north-1 | docker login --username AWS --password-stdin 844069736237.dkr.ecr.eu-north-1.amazonaws.com
    docker build -t digtvil-flask .
    docker tag digtvil-flask:latest 844069736237.dkr.ecr.eu-north-1.amazonaws.com/digtvil-flask:latest
    docker push 844069736237.dkr.ecr.eu-north-1.amazonaws.com/digtvil-flask:latest
    aws ecs update-service --service flask-server-service --cluster digtvil-cluster --force-new-deployment
    cd ..
}

terriamap () {
    cd TerriaMap
    aws ecr get-login-password --region eu-north-1 | docker login --username AWS --password-stdin 844069736237.dkr.ecr.eu-north-1.amazonaws.com
    yarn docker-build-prod
    docker tag digtvil-kartverket:0.0.1 844069736237.dkr.ecr.eu-north-1.amazonaws.com/digtvil-kartverket:latest
    docker push 844069736237.dkr.ecr.eu-north-1.amazonaws.com/digtvil-kartverket:latest
    aws ecs update-service --service digtvil-kartverket-container-service --cluster digtvil-cluster --force-new-deployment
    cd ..
}

if [ $1 = "flask" ]
then 

    flask

elif [ $1 == "terriamap" ]
then

    terriamap

elif [ $1 == "all" ]
then

    flask
    terriamap

else 
    echo "$1 is not a valid command"
fi