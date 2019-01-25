# https://www.cryptosys.net/pki/manpki/pki_Keystorage-ecc.html
# https://tools.ietf.org/html/rfc5480
# https://tools.ietf.org/html/rfc5915
# https://tools.ietf.org/html/rfc5208

# -----BEGIN EC PRIVATE KEY-----
# ECPrivateKey ::= SEQUENCE {
#      version        INTEGER { ecPrivkeyVer1(1) } (ecPrivkeyVer1),
#      privateKey     OCTET STRING,
#      parameters [0] ECParameters {{ NamedCurve }} OPTIONAL,
#      publicKey  [1] BIT STRING OPTIONAL
#    }
# -----END EC PRIVATE KEY-----
# .pem file -> base64 encoding