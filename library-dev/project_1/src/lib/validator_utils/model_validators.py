def check_password_match(password1: str, password2: str) -> bool:
    if (password1 is not None) and (password2 is not None) and (password1 != password2):
        raise ValueError('password do not match')
    return True