import random

from django.utils.text import slugify

from core.consts import SLUG_TOKEN_LENGTH, TOKEN_CHARS, TOKEN_LENGTH


def gen_token(token_length: int = TOKEN_LENGTH) -> str:
    return ''.join([random.choice(TOKEN_CHARS) for _ in range(token_length)])


def gen_slug(attr: str, max_length: int = 32) -> str:
    token = gen_token(token_length=SLUG_TOKEN_LENGTH)
    slug = slugify(attr)[:max_length - SLUG_TOKEN_LENGTH]
    slug += f'-{token}'
    return slug
