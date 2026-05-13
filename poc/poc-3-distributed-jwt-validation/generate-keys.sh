#!/bin/bash
# Genereert een RSA-keypair voor JWT-ondertekening (RS256).
#
# private.pem  -> enkel user-management gebruikt deze (Docker secret)
# public.pem   -> gateway, catalog, validator gebruiken deze (Docker secret)
#
# Conform OAuth-theorieles: asymmetrische ondertekening zodat enkel
# de authorization server tokens kan uitgeven, terwijl resource servers
# zelfstandig kunnen valideren.

set -e

cd "$(dirname "$0")"
mkdir -p keys

if [ -f keys/private.pem ] && [ -f keys/public.pem ]; then
    echo "Keys bestaan al in ./keys/. Verwijder ze eerst om opnieuw te genereren."
    exit 0
fi

openssl genrsa -out keys/private.pem 2048
openssl rsa -in keys/private.pem -pubout -out keys/public.pem

chmod 600 keys/private.pem
chmod 644 keys/public.pem

echo "RSA-keypair gegenereerd in ./keys/"
echo "  private.pem  (gevoelig - enkel user-management)"
echo "  public.pem   (gedeeld met gateway, catalog, validator)"
