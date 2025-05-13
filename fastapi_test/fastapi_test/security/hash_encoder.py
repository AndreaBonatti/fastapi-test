import bcrypt


def encode(password: str) -> str:
    password_as_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password_as_bytes, salt)
    return hashed_password.decode('utf-8')  # store as str


def matches(raw_password: str, hashed_password: str) -> bool:
    password_as_bytes = raw_password.encode('utf-8')
    hashed_password_as_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_as_bytes, hashed_password_as_bytes)
