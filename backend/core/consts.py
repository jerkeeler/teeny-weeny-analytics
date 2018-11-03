import string

SLUG_TOKEN_LENGTH = 4
TOKEN_CHARS = string.ascii_letters + string.digits
TOKEN_LENGTH = 16
TOKEN_REGEX = r'([a-zA-Z0-9]{})'.format('{' + str(TOKEN_LENGTH) + '}')
VARCHAR_LENGTH = 256
