from passlib.context import CryptContext
from fastapi import HTTPException, status  # add this

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    pw_bytes = password.encode("utf-8")
    # TEMP: log what we’re actually hashing
    print("hash_password len(bytes) =", len(pw_bytes), "value repr=", repr(password))

    if len(pw_bytes) > 72:
        # Fail with a clear client error instead of 500
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password too long; must be at most 72 bytes.",
        )
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)
