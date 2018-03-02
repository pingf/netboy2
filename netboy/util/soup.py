import re
from bs4 import BeautifulSoup


class Soup:
    def __init__(self, *args, **kwargs):
        self.soup = BeautifulSoup(*args, **kwargs)

    def get_title(self):

        if self.soup.title is None:
            text = str(self.soup.get_text())
            if len(text) > 400:
                return None
            else:
                if len(text)>128:
                    return text[:128]
                return text

        text = str(self.soup.title.get_text())
        text = re.sub('\s+', ' ', text)
        return text

    def get_text(self):
        texts = self.soup.findAll(text=True)

        def visible(element):
            if element.parent.name in ['style', 'script', '[document]', 'head', 'title']:
                return False
            elif re.match('<!--.*-->', str(element)):
                return False
            return True

        visible_texts = filter(visible, texts)
        return ' '.join(visible_texts)

    def get_links(self):
        data = list(set([link['href'] for link in self.soup.find_all('a', href=True) if
                         isinstance(link['href'], str) and
                         link['href'] != '/' and link['href'] != '' and not link['href'].startswith('java')]))
        return data

    def get_links2(self):
        data = list(
            set([style.get('href') or style.get('innerHTML') for style in self.soup.find_all('link', href=True) if
                 isinstance(style.get('href'), str) and isinstance(style.get('innerHTML'), str) and
                 (style.get('href') or style.get('innerHTML')) != '/' and
                 (style.get('href') or style.get('innerHTML')) != '' and
                 (style.get('href') or style.get('innerHTML')).startswith('java')]))
        return data

    def get_images(self):
        srcs = [img['src'] for img in self.soup.find_all('img', src=True) if img.get('src') is not None]
        data_srcs = [img.get('data.src') for img in self.soup.find_all('img', src=False) if
                     img.get('data-src') is not None]
        return list(set(srcs + data_srcs))

    def get_scripts(self):
        return list(set([script['src'] for script in self.soup.find_all('script', src=True)]))

    def get_metas(self):
        return list(set([meta.get('content') for meta in self.soup.find_all('meta', content=True)]))
