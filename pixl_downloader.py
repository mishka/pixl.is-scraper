from shutil import copyfileobj
from datetime import datetime
from os import getcwd

from requests import get
from bs4 import BeautifulSoup
from termcolor import colored


class pixlr:
    def __init__(self):
        self.path = getcwd() + '/output/'
        self.headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'}
        self.link_to_posts = []
        self.next_page = None


    def log(self, text, colour):
        current_time = datetime.now().strftime('%H:%M:%S.%f')[:-3]
        print(colored(f'| {current_time} |', 'white'),  colored(f'{text}', colour))


    def fetch_page(self, url):
        return get(url, headers = self.headers).text


    def download_media(self, url, filename):
        with open(self.path + filename, 'wb') as file:
            req = get(url = url, headers= self.headers, stream = True)
            req.raw.decode_content = True
            copyfileobj(req.raw, file)


    def soup(self, content, album = False):
        soup = BeautifulSoup(content, 'html.parser')

        if album:
            self.log('Parsing current album page..', 'yellow')
            all_imgs = soup.find_all('div', attrs = {'class': 'list-item-image fixed-size'})

            for entry in all_imgs:
                self.link_to_posts.append(entry.find('a', attrs ={'class': 'image-container --media'})['href'])
            
            try:
                self.next_page = soup.find('a', attrs = {'data-pagination': 'next'})['href']
            except KeyError:
                self.next_page = None
        else:
            self.log('Parsing current picture page..', 'yellow')
            return soup.find('input', attrs = {'id': 'embed-code-2', 'class': 'text-input'})['value']


    def process(self, url):
        self.log(f'Fetching: {url}', 'magenta')
        self.soup(self.fetch_page(url), True)

        while self.next_page:
            self.log(f'Fetching: {self.next_page}', 'magenta')
            self.soup(self.fetch_page(self.next_page), True)

        for post in self.link_to_posts:
            picture_url = self.soup(self.fetch_page(post))
            filename = picture_url.split('i.pixl.is/')[1]
            self.download_media(picture_url, filename)
            self.log(f'Downloaded: {filename}', 'cyan')