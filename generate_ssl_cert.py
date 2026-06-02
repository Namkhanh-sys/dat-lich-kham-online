#!/usr/bin/env python3
"""Generate self-signed SSL certificate with proper SAN for local HTTPS development."""

import os
from datetime import datetime, timedelta
from cryptography import x509
from cryptography.x509.oid import NameOID, ExtensionOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from ipaddress import IPv4Address

# Create certs directory
os.makedirs('certs', exist_ok=True)

# Generate private key
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
    backend=default_backend()
)

# Create certificate with SAN for IP addresses and hostnames
subject = issuer = x509.Name([
    x509.NameAttribute(NameOID.COMMON_NAME, u"MedBooking"),
])

# Create Subject Alternative Names
san_list = [
    x509.DNSName(u"localhost"),
    x509.DNSName(u"127.0.0.1"),
    x509.DNSName(u"192.168.100.233"),
    x509.IPAddress(IPv4Address(u"127.0.0.1")),
    x509.IPAddress(IPv4Address(u"192.168.100.233")),
]

cert = x509.CertificateBuilder().subject_name(
    subject
).issuer_name(
    issuer
).public_key(
    private_key.public_key()
).serial_number(
    x509.random_serial_number()
).not_valid_before(
    datetime.utcnow()
).not_valid_after(
    datetime.utcnow() + timedelta(days=36500)
).add_extension(
    x509.SubjectAlternativeName(san_list),
    critical=False,
).add_extension(
    x509.BasicConstraints(ca=False, path_length=None),
    critical=True,
).sign(private_key, hashes.SHA256(), default_backend())

# Write private key
with open('certs/key.pem', 'wb') as f:
    f.write(private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    ))

# Write certificate
with open('certs/cert.pem', 'wb') as f:
    f.write(cert.public_bytes(serialization.Encoding.PEM))

print("✓ Chứng chỉ SSL đã được tạo lại với SAN:")
print("  - certs/cert.pem")
print("  - certs/key.pem")
print("\nChứng chỉ hỗ trợ:")
print("  - https://127.0.0.1:5000")
print("  - https://192.168.100.233:5000")
print("  - https://localhost:5000")
print("\nLưu ý: Trên điện thoại, chấp nhận cảnh báo 'Connection Not Private'")
