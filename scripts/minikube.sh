#!/usr/bin/env bash
# spawns minikube optionally with Podman on Ubuntu 20.04 and above.

USAGE="$(cat usage.txt)"
DEFAULT_NODE_AMOUNT=2

if [ "$#" == "0" ]; then
	echo "$USAGE"
	exit 1
fi

if [[ "$1" == "podman" ]]; then
  read -rp "Please enter your username: " USER_NAME
  # check to see if podman is installed on our distro, if not install it.
  if ! command -v podman &> /dev/null
  then
    echo "Podman not installed, command not found installing podman now...."
    apt-get -y update
    apt-get -y install podman
  else
    echo "Podman command found continuing..."
  fi

  # check and see if permissions have been setup for podman
  result=$(grep -i "${USERNAME} ALL=(ALL) NOPASSWD: /usr/bin/podman" -f /etc/sudoers)
  if [ -z "${result}" ]; then
    echo "permissions not setup, setting permissions now..."
    if [ -z "${USER_NAME}" ]; then
      echo "username not set or empty.. aborting to avoid breaking sudoers..."
    else
      echo "${USER_NAME} ALL=(ALL) NOPASSWD: /usr/bin/podman" >> /etc/sudoers
    fi
  else
    echo "Podman Permissions found."
  fi
fi

# tbc confirm this part is working.
if [ "$1" == "view" ]; then
  echo "Showing the current minikube config file located at ${HOME}/.minikube/config/config.json"
  minikube config "$1"
elif [ "$1" == "config" ]; then
  echo "setting up config for minikube from ${HOME}/.minikube/config/config.json"
  shift
  cp -r "$1"-config.json ~/.minikube/config/config.json
fi


if [ "$1" == "run" ]; then
  echo "Running cluster"
  if [ "$2" == "nodes" ]; then
    (( DEFAULT_NODE_AMOUNT = $3))
  fi
  minikube start --nodes "${DEFAULT_NODE_AMOUNT}" --cri-socket="/var/run/crio/crio.sock" -p cluster
fi


if [ "$1" == "start" ]; then
  cluster="$2"
  echo "Starting cluster ${cluster}"
  minikube start --cri-socket="/var/run/crio/crio.sock" -p "${cluster}"
fi


if [ "$1" == "list-clusters" ]; then
  echo "Listing all available minikube profiles"
  minikube profile list
fi


if [ "$1" == "stop" ]; then
  echo "stopping minikube cluster $2"
  minikube stop -p "$2"
fi