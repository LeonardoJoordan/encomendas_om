import hashlib

def hash_pin(pin: str) -> str:
    # Utilizando SHA-256 nativo para evitar dependências pesadas (como bcrypt) na compilação do Nuitka
    return hashlib.sha256(pin.encode()).hexdigest()

def verify_pin(plain_pin: str, hashed_pin: str) -> bool:
    return hash_pin(plain_pin) == hashed_pin