#!/bin/bash
set -e
set -x

OPTIND=1
IMAGE_NAME=mattermost-bridges
IMAGE_TAG=latest
DOCKER_REGISTRY=repo.yourdomain.com/integrations
DATE_TAG=$(date "+%m-%d-%Y")

function show_help {
        echo "Use it with flags: -r (DOCKER_REGISTRY)"
        exit 0
}

while getopts "h?r:" opt; do
    case "$opt" in
    h|\?)
        show_help
        ;;
    r)  DOCKER_REGISTRY=$OPTARG
        ;;
    esac
done

shift $((OPTIND-1))
[ "${1:-}" = "--" ] && shift

docker build --pull --no-cache -t ${IMAGE_NAME}:${IMAGE_TAG} \
	   --build-arg DOCKER_REGISTRY=${DOCKER_REGISTRY} .

docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${DOCKER_REGISTRY}/${IMAGE_NAME}:latest
docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${DOCKER_REGISTRY}/${IMAGE_NAME}:${DATE_TAG}

docker push ${DOCKER_REGISTRY}/${IMAGE_NAME}:latest
docker push ${DOCKER_REGISTRY}/${IMAGE_NAME}:${DATE_TAG}
