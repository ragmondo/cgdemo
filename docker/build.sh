#!/bin/bash -x

local_registry="registry.reneo.io" # Replace this with your preferred registry
repository="cgdemo"

docker_build_command="docker build .. -f ./Dockerfile"
docker_build_command+=" -t $local_registry/$repository:latest"

eval $docker_build_command
echo "build.sh complete."
