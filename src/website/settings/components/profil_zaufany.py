import logging
from email.utils import getaddresses

from . import core
from . import python_social_auth as psa

log = logging.getLogger(__name__)

core.AUTHENTICATION_BACKENDS += (
    'social_core.backends.saml.SAMLAuth',
)

psa.SOCIAL_AUTH_AUTHENTICATION_BACKENDS += (
    'social_core.backends.saml.SAMLAuth',
)

SOCIAL_AUTH_SAML_SP_ENTITY_ID = core.env("SOCIAL_AUTH_SAML_SP_ENTITY_ID", default=None)
SOCIAL_AUTH_SAML_SP_PRIVATE_KEY = core.env("SOCIAL_AUTH_SAML_SP_PRIVATE_KEY", default=None)
SOCIAL_AUTH_SAML_SP_PUBLIC_CERT = core.env("SOCIAL_AUTH_SAML_SP_PUBLIC_CERT", default=None)

SOCIAL_AUTH_SAML_ORG_INFO = {
    "pl-PL": {
        "name": core.env("SOCIAL_AUTH_SAML_ORG_INFO_NAME", default=None),
        "displayname": core.env("SOCIAL_AUTH_SAML_ORG_INFO_DISPLAYNAME", default=None),
        "url": core.env("SOCIAL_AUTH_SAML_ORG_INFO_URL", default=None),
    }
}


technical = getaddresses([core.env("SOCIAL_AUTH_SAML_TECHNICAL_CONTACT", default="")])
support = getaddresses([core.env("SOCIAL_AUTH_SAML_SUPPORT_CONTACT", default="")])

SOCIAL_AUTH_SAML_TECHNICAL_CONTACT = {
    "givenName": technical[0][0],
    "emailAddress": technical[0][1],
}

SOCIAL_AUTH_SAML_SUPPORT_CONTACT = {
    "givenName": support[0][0],
    "emailAddress": support[0][1],
}

SOCIAL_AUTH_SAML_ENABLED_IDPS = {
    "pzgovpl": {
        "entity_id": "https://pz.gov.pl/",
        "url": "https://pz.gov.pl/dt/SingleSignOnService",
        "x509cert": """MIIFSjCCBDKgAwIBAgIQDlXTvHm3lhzgt2KFQl2I/DANBgkqhkiG9w0BAQsFADCBijELMAkGA1UE
BhMCUEwxIjAgBgNVBAoMGVVuaXpldG8gVGVjaG5vbG9naWVzIFMuQS4xJzAlBgNVBAsMHkNlcnR1
bSBDZXJ0aWZpY2F0aW9uIEF1dGhvcml0eTEuMCwGA1UEAwwlQ2VydHVtIERpZ2l0YWwgSWRlbnRp
ZmljYXRpb24gQ0EgU0hBMjAeFw0xODA4MjcxODEyMzZaFw0yMTA4MjYxODEyMzZaMHwxCzAJBgNV
BAYTAlBMMSAwHgYDVQQKDBdNaW5pc3RlcnN0d28gQ3lmcnl6YWNqaTEgMB4GA1UECwwXTWluaXN0
ZXJzdHdvIEN5ZnJ5emFjamkxDDAKBgNVBAMMA1dTMTEbMBkGCSqGSIb3DQEJARYMbWNAbWMuZ292
LnBsMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAvSy8WrZOVrzB5D6Q1TXiXO0a6Ph1
ckxRgTX/bcCkNoF90aLJ/OYhc6rr7KfQ5wQV2XHQePuA6obEPIYmXat6y//WbyYJcoWal4lyOcnc
lP0hM3cQCXJcd636OYQqn4EW0Yvro0CHlwVTH0SouA/HJbu5dK+Cba5DTGemB7NaMUJaHwyXMPSQ
zFMuBSjaxXltnYg9YRhXmwu9VPUj5OrJX5B1+0fwdHu7Ojx/+d+prJgudTrm8YvD4JWjfRKzzzU3
mpQpC/a8aYZd5ICajkvZ17GsXGY12YrhXtE+aCEDBcrdGOa4mqHzIDdkOa7ckWFk6jZPqZV+N42F
TngdUckTzwIDAQABo4IBtzCCAbMwDAYDVR0TAQH/BAIwADAyBgNVHR8EKzApMCegJaAjhiFodHRw
Oi8vY3JsLmNlcnR1bS5wbC9kaWNhc2hhMi5jcmwwcQYIKwYBBQUHAQEEZTBjMCsGCCsGAQUFBzAB
hh9odHRwOi8vZGljYXNoYTIub2NzcC1jZXJ0dW0uY29tMDQGCCsGAQUFBzAChihodHRwOi8vcmVw
b3NpdG9yeS5jZXJ0dW0ucGwvZGljYXNoYTIuY2VyMB8GA1UdIwQYMBaAFD/KWOrxyQl+bjPBI61O
rT49bEWnMB0GA1UdDgQWBBSuYrH8DXPRzIeYo3GM7mq6uYNZ7zAdBgNVHRIEFjAUgRJkaWNhc2hh
MkBjZXJ0dW0ucGwwDgYDVR0PAQH/BAQDAgTwMEIGA1UdIAQ7MDkwNwYMKoRoAYb2dwIFAQYOMCcw
JQYIKwYBBQUHAgEWGWh0dHBzOi8vd3d3LmNlcnR1bS5wbC9DUFMwHQYDVR0lBBYwFAYIKwYBBQUH
AwIGCCsGAQUFBwMEMBEGCWCGSAGG+EIBAQQEAwIFoDAXBgNVHREEEDAOgQxtY0BtYy5nb3YucGww
DQYJKoZIhvcNAQELBQADggEBAKiQL0OMRPU6EyZYGe41EHuC+dB6huBuO2YQXOR9SKoHVvAlj2Tf
wIUjfXtSCcMYC5ygPWRJKMeJEzShwgzk6IbF2KXZ1N8GRx4F446FQnpYej/FBMBJjixyxA1/0RY2
o14DhpMH8yn2IljkFNw6FuqTlr7aYqKxlSKeyRloyGYgXFCZrZ7/X0CMxgK4C8x+qkIIAHvf27e/
sOTil1wbl6iTgJ+pb7wn7wMZWmDU33fYGYV/zPNABXBCpBowiuPY2NfNXTpz8qE7pQp8c6cEpdF3
yVlHH/1vJFrS1u1S0/yEb18tBaZ0/0Fcg4OfL5+sAiOcqeg01nMbklj6bndN9zY=""",
    }
}
