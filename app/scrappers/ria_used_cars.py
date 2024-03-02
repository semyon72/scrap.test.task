import functools
import re

import requests
from bs4 import BeautifulSoup, SoupStrainer, Tag, NavigableString


# Pagination (last page, in the middle of pagination) behaves weird. It can show 29xxx pages instead as on start.
# For example on https://auto.ria.com/uk/car/used/?page=777 will show 29944 pages
# Next strategy is more reliable
# https://auto.ria.com/uk/car/used/?page=14968 -> last page 200 but no information
# https://auto.ria.com/uk/car/used/?page=14969 -> 404
def get_content(url, s: requests.Session = None, params: dict = None):
    if hasattr(url, 'read'):
        content = url.read()
    else:
        response = s.get(url, params=params or {})
        if response.status_code != 200:
            raise ValueError(f"{url} responds {response.status_code}", response)
        content = response.content
    return content


def page_item_parser(url, s: requests.Session = None, params: dict = None) -> list[str]:
    # div.content-bar a.m-link-ticket[href="https://auto.ria.com/uk/auto_volkswagen_passat_alltrack_35662955.html"]
    # BAD link: div.content-bar a.m-link-ticket[href="https://auto.ria.com/uk/newauto/auto-mg-4-1958318.html"]
    content = get_content(url, s, params=params or {})

    only_a_tags = SoupStrainer("div", attrs={'class': 'content-bar'})
    soup = BeautifulSoup(content, 'lxml', parse_only=only_a_tags)
    return [
        a['href'] for a in soup.find_all("a", attrs={'class': 'm-link-ticket', 'href': True})
        if '/newauto/' not in a['href']
    ]


class ItemInfo:
    # example https://auto.ria.com/uk/auto_volkswagen_passat_alltrack_35662955.html
    #
    # url: str  # url (строка)
    # title: str  # title (строка) -> div#heading-cars a#addToBookmarks + h1.head
    # price_usd: int  # price_usd (число) ->
    # odometer: int  # odometer (число, нужно перевести 95 тыс. в 95000 и записать как число)
    # username: str  # username (строка)
    # phone_number: int  # phone_number (число, пример структуры: +38063……..) ? it does not fit into int32
    # image_url: str  # image_url (строка)
    # images_count: int  # images_count (число)
    # car_number: str  # car_number (строка)
    # car_vin: str  # car_vin (строка)
    # datetime_found: datetime.date  # datetime_found (дата сохранения в базу)

    def __init__(self, url, s: requests.Session = None) -> None:
        self._s = s
        self._url = '' if hasattr(url, 'read') else url
        self._content = get_content(url, self._s)
        self._bs = BeautifulSoup(self._content, 'lxml')

    @property
    def url(self) -> str:
        return self._url

    @property
    def title(self) -> str:
        title = self._bs.select_one('div#heading-cars a#addToBookmarks + h1.head')
        return '' if not title else str(title.string).strip()

    @functools.cached_property
    def _showLeftBarView(self) -> Tag:
        return self._bs.find(id='showLeftBarView')

    @property
    def price_usd(self) -> int:
        price_usd = self._showLeftBarView.select_one('div.price_value > strong:nth-child(1)')
        return int(''.join(price_usd.string.split()[:-1]))

    @property
    def odometer(self) -> int:
        odometer = self._showLeftBarView.select_one('.base-information > span:nth-child(1)')
        return int(odometer.string) * 1000

    @functools.cached_property
    def _userInfoBlock(self) -> Tag:
        return self._showLeftBarView.find(id='userInfoBlock')

    @property
    def username(self) -> str:
        res = ''
        if self._userInfoBlock:
            username = self._userInfoBlock.select_one('div.seller_info_area .seller_info_name')
            if username:
                res = username.text.strip()
        return res

    @property
    def phone_number(self) -> int:
        # GET https://auto.ria.com/users/phones/35662955?hash=PLvPbBbLNsmKNd_HYCMfog&expires=2592000
        # <script class="js-user-secure-3916367" data-hash="PLvPbBbLNsmKNd_HYCMfog" data-expires="2592000"></script>
        if not isinstance(self._s, requests.Session):
            return 0

        if not self.url:
            auto_id = self._bs.find('body', attrs={'data-auto-id': True})
            auto_id = auto_id['data-auto-id']
        else:
            auto_id = self.url.split('_')[-1].split('.')[0]

        js_user_secure = self._bs.find('script', class_=lambda c: c and c.startswith('js-user-secure-'))
        params = {
            'hash': js_user_secure['data-hash'],
            'expires': js_user_secure['data-expires']
        }
        phones_resp = self._s.get(f'https://auto.ria.com/users/phones/{auto_id}', params=params)
        if phones_resp.status_code == 200:
            phones = phones_resp.json()
            return int(re.sub(r'[(,)\s]', '', phones['phones'][0]['phoneFormatted'], flags=re.IGNORECASE))
        else:
            return 0

    @functools.cached_property
    def _photos_block(self) -> Tag:
        return self._bs.find(id='photosBlock')

    @property
    def image_url(self):
        res = ''
        css = 'div.gallery-order.carousel div.carousel-inner > div[class^="photo-"] picture img'
        photos = self._photos_block.select(css)
        if photos:
            res = photos[0]['src']
        return res

    @property
    def images_count(self):
        el = self._photos_block.select_one('a.show-all')
        if el:
            return int(re.search(r'(\d+)', str(el.string))[0])
        else:
            css = 'div.preview-gallery div.wrapper[photocontainer="photo"] > a[class^="photo-"] img'
            return len(self._photos_block.select(css))

    @functools.cached_property
    def _technicalInfo(self):
        return self._bs.find('main', class_='auto-content').select_one(
            'div.vin-checked.full div.technical-info.ticket-checked div.t-check')

    @property
    def car_number(self):
        res = []
        if self._technicalInfo:
            plate_num = self._technicalInfo.select_one('span.state-num')
            if plate_num:
                res = [''.join(str(el).split()) for el in plate_num.contents if isinstance(el, NavigableString)]
        return '@'.join(res)

    @property
    def car_vin(self):
        res = ''
        if self._technicalInfo:
            vin_el = self._technicalInfo.select_one('span.label-vin, span.vin-code')
            if vin_el:
                res = ''.join(vin_el.get_text().split())
        return res

    @functools.cached_property
    def as_dict(self) -> dict:
        return {
            'url': self.url,
            'title': self.title,
            'price_usd': self.price_usd,
            'odometer': self.odometer,
            'username': self.username,
            'phone_number': self.phone_number,
            'image_url': self.image_url,
            'images_count': self.images_count,
            'car_number': self.car_number,
            'car_vin': self.car_vin,
        }
