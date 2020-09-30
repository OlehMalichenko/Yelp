import scrapy
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError, TCPTimedOutError

from ..util import *
from ..items import YelpItem
from ..data_provider import *


class YelpSpider(scrapy.Spider):
    name = 'yelpspider'
    allowed_domains = ['yelp.com']

    def __init__(self, url=None, file=None, *args, **kwargs):
        """
        Preparation url from command line or urls from file
        @param url string from command line
        @param file string from command line, absolute path to file
        """
        super(YelpSpider, self).__init__(*args, **kwargs)

        self.urls = []

        if url and not file:
            self.urls.append(url_preparation(url))
        elif file and not url:
            self.urls = read_urls_from_file_csv(file)
        elif not file and not url:
            self.logger.warning('Input url or path to file')
        elif file and url:
            self.logger.warning('Input only one parameter')

        self.urls = list(filter(None, self.urls))
        if not self.urls:
            self.logger.warning('Invalid urls')


    def start_requests(self):
        """Create requests"""
        for url in self.urls:
            yield scrapy.Request(url=url,
                                 callback=self.parse,
                                 errback=self.errback_httpbin)


    def parse(self, response, **kwargs):
        """Main method for collect all data and yield item"""

        item = YelpItem()

        # Dictionary from JSON
        json_dict = get_dict_from_scriptjson(response.text)
        if not json_dict:
            self.logger.error(f'Problem with create dict from json\nURL:{response.url}')
            return

        # Server Modules List
        well_done, server_modules_list = get_the_server_modules_list_in_(json_dict)
        if not well_done:
            self.logger.error(f'Problems with keys on this way: {"->".join(server_modules_list)}')
            return

        # Data from Server Modules List
        infobox = find_component_for_(Key.component_infobox_name, server_modules_list)
        if infobox:
            item['name'] = infobox.get(Key.name, '')
            item['rating'] = infobox.get(Key.rating, '')
            item['review_count'] = infobox.get(Key.review_count, '')
            item['categories'] = infobox.get(Key.categories, [])
        action_buttons = find_component_for_(Key.component_actionbuttons_name, server_modules_list)
        if action_buttons:
            item['site'] = get_site(action_buttons)

        # Address andTelephone
        item['address'], item['tel'], item['img_link'] = get_address_telephone_image(json_dict)

        # Email
        item['email'] = get_email(json_dict)

        # Business ID
        item['biz_id'] = get_bizid(json_dict)

        # URL
        item['url'] = get_url(response.url)

        # Amenities
        item['amenities'] = get_amenities(json_dict)

        # Hours
        item['hours'] = get_hours(json_dict)

        # About Biz
        item['about_biz'] = get_about_biz(json_dict)

        yield item


    def errback_httpbin(self, failure):
        # log all failures
        self.logger.error(repr(failure))
        if failure.check(HttpError):
            response = failure.value.response
            self.logger.error('HttpError on %s', response.url)
        elif failure.check(DNSLookupError):
            request = failure.request
            self.logger.error('DNSLookupError on %s', request.url)
        elif failure.check(TimeoutError, TCPTimedOutError):
            request = failure.request
            self.logger.error('TimeoutError on %s', request.url)

