from core.consts import TOKEN_REGEX


class TokenConverter(object):
    regex = TOKEN_REGEX

    def to_python(self, value: str) -> str:
        return str(value)

    def to_url(self, value: str) -> str:
        return str(value)
