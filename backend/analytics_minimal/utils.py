from base64 import b64decode

from django.http import HttpResponse


def anonymize_ip(ip: str) -> str:
    split_ip = '.'.join(ip.split('.')[:-1])
    return f'{split_ip}.0'


def get_gif_response(status_code: int = 200) -> HttpResponse:
    """
    This method returns a 1x1 gif that shouldn't be cached, ever. That way we return a valid thing!
    Thanks https://css-tricks.com/snippets/html/base64-encode-of-1x1px-transparent-gif/
    :return: GIF!
    """
    response = HttpResponse()
    response['Tk'] = 'N'
    response['Content-Type'] = 'image/gif'
    response['Expires'] = 'Mon, 01 Jan 1990 00:00:00 GMT'
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response.status_code = status_code
    response.write(b64decode('R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7'))
    return response
