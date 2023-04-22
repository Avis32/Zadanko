from django.core.signing import Signer


def encode_value(value: str) -> str:
    signer = Signer(key=value)
    return signer.sign("anonymized").split(":")[1]
