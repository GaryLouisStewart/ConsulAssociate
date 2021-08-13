#!/usr/bin/env bash
# setup and configure ingress in minikube with

NAMESPACE="kube-system"
PRIV_KEY="kube-tls.pem"
CERT="kube-cert.pem"


python3 gen_tls.py

kubectl -n $NAMESPACE create secret tls mkcert --key $PRIV_KEY --cert $CERT
