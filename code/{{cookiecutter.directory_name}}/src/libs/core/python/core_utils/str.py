import base64
import json

def encode_b64(last_evaluated_key: dict | str) -> str:
    """Encodes a last evaluated key into a base64 string."""
    if isinstance(last_evaluated_key, str):
        return base64.urlsafe_b64encode(last_evaluated_key.encode()).decode()
    json_str = json.dumps(last_evaluated_key)
    return base64.urlsafe_b64encode(json_str.encode()).decode()

def decode_b64(encoded_str: str) -> dict | str:
    """Decodes a base64 string into a dictionary or string."""
    decoded_bytes = base64.urlsafe_b64decode(encoded_str.encode())
    try:
        return json.loads(decoded_bytes.decode())
    except json.JSONDecodeError:
        return decoded_bytes.decode()  # Return as string if JSON decoding fails