import re

def sanitize_filename(filename):
    return re.sub(r'[<>:"/\\|?*]', '', filename).strip()
