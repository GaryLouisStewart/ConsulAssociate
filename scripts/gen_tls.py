#!/usr/bin/env python3

"""
Generates a self signed tls certificate bundle for use with kubernetes clusters and ingress controllers.
Author: Gary Louis Stewart
maintained by @GaryLouisStewart
gary-stewart@outlook.com
"""
import datetime
import json

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes


def read_json_file(json_file=None):
    """
    :param json_file: the json file to be passed to this function :return: returns a dictionary with the key-value
    pairs for us to use to set variables up, if file doesn't exist returns an exception and None.
    """
    try:
        with open(json_file) as file:
            data_dict = json.load(file)
    except FileNotFoundError:
        print("The following file: {0}, does not exist or is in the wrong directory.".format(json_file))
        return
    return data_dict


def generate_tls_bundle(json_file_path=str):
    """
    takes the optional path for the json file, if left empty than
    generates a private key for us.
    :return: returns key and csr objects.
    """

    json_data = read_json_file("config/tls-config.json")
    pub_key_path = json_data['pub_key_path']
    priv_key_size = json_data['priv_key_size']
    priv_key_path = json_data['priv_key_path']
    priv_key_pass = json_data['priv_key_pass']
    country_name = json_data['country_name']
    email_address = json_data['email_address']
    state_province_name = json_data['state_province_name']
    locality_name = json_data['locality_name']
    organisation_name = json_data['organisation_name']
    common_name = json_data['common_name']
    dns_name_1 = json_data['dns_names']
    csr_file_path = json_data['csr_file_path']
    certificate_file_path = json_data['certificate_file_path']
    validity_period = json_data['certificate_validity_period']

    with open(priv_key_path, "wb") as f:
        key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=priv_key_size
        )

        password = f'{priv_key_pass}'.encode()
        f.write(key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.BestAvailableEncryption(b"%s" % password),
        ))
    with open(pub_key_path, "wb") as pb:
        pb.write(key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        ))

    csr = x509.CertificateSigningRequestBuilder().subject_name(x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, u"%s" % country_name),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"%s" % state_province_name),
        x509.NameAttribute(NameOID.EMAIL_ADDRESS, u"%s" % email_address),
        x509.NameAttribute(NameOID.LOCALITY_NAME, u"%s" % locality_name),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"%s" % organisation_name),
        x509.NameAttribute(NameOID.COMMON_NAME, u"%s" % common_name),
    ])).add_extension(
        x509.SubjectAlternativeName([
            x509.DNSName(u"%s" % dns_name_1[0]),
            x509.DNSName(u"%s" % dns_name_1[1]),
            x509.DNSName(u"%s" % dns_name_1[2]),
        ]),
        critical=False,
    ).sign(key, hashes.SHA256())
    with open("%s" % csr_file_path, "wb") as f:
        f.write(csr.public_bytes(serialization.Encoding.PEM))

    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, u"%s" % country_name),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"%s" % state_province_name),
        x509.NameAttribute(NameOID.LOCALITY_NAME, u"%s" % locality_name),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"%s" % organisation_name),
        x509.NameAttribute(NameOID.COMMON_NAME, u"%s" % common_name),
    ])

    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.datetime.utcnow()
    ).not_valid_after(
        datetime.datetime.utcnow() + datetime.timedelta(days=validity_period)
    ).add_extension(
        x509.SubjectAlternativeName([x509.DNSName(u"localhost")]),
        critical=False,
    ).sign(key, hashes.SHA256())
    with open("%s" % certificate_file_path, "wb") as certificate:
        certificate.write(cert.public_bytes(serialization.Encoding.PEM))


generate_tls_bundle("config/tls-config.json")
