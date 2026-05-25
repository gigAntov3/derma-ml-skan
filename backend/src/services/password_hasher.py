import bcrypt


class PasswordHasherService:
    def hash(self, password: str) -> str:
        """Хэширует пароль с обрезкой до 72 байт"""
        password_bytes = password.encode('utf-8')
        if len(password_bytes) > 72:
            password_bytes = password_bytes[:72]
        
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode('utf-8')
    
    def verify(self, plain_password: str, hashed_password: str) -> bool:
        """Проверяет пароль с обрезкой до 72 байт"""
        plain_bytes = plain_password.encode('utf-8')
        if len(plain_bytes) > 72:
            plain_bytes = plain_bytes[:72]
        
        hashed_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(plain_bytes, hashed_bytes)