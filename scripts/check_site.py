"""Check local generated HTML links and required distribution files without network."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT/'_site'


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = []

    def handle_starttag(self, tag, attrs):
        for name, value in attrs:
            if name in {'href', 'src'} and value:
                self.urls.append(value)


def main():
    errors, checked = [], 0
    # JupyterLite's app routes are application-generated; test its required files separately.
    files = [SITE/'index.html'] + list((SITE/'book').glob('*.html'))
    for folder in ['maps', 'globe', 'scenes']:
        files.extend((SITE/folder).glob('*.html'))
    for path in files:
        parser = Links()
        parser.feed(path.read_text(encoding='utf-8'))
        for url in parser.urls:
            split = urlsplit(url)
            if split.scheme or split.netloc or not split.path or split.path.startswith('/'):
                continue
            target = path.parent/unquote(split.path)
            if not target.exists():
                errors.append(f'{path.relative_to(SITE)} -> {url}')
            checked += 1
    for required in ['lite/lab/index.html', 'lite/api/contents/all.json', 'book/index.html',
                     'maps/plot.html', 'globe/plot.html', 'scenes/plot.html', 'assets/plotly.min.js']:
        if not (SITE/required).is_file():
            errors.append('Missing: '+required)
    if errors:
        raise SystemExit('\n'.join(errors))
    print(f'PASS: {checked} relative HTML links/assets and required distribution files.')


if __name__ == '__main__':
    main()
