from bs4 import BeautifulSoup
from price.utils.download_utils import standard_request
from price.utils.download_utils import SmallResponseObject


def get_soup_from_url(url: str) -> SmallResponseObject:
    resp = standard_request(url)
    soup = BeautifulSoup(resp.get_contents(), features="html.parser")
    return soup
