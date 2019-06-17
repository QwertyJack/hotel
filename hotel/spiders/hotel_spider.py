#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2019 jack <jack@6k>
#
# Distributed under terms of the MIT license.

"""
crawl hotels from ctrip.com
"""

from collections import namedtuple

import scrapy

from data import city, city_data

City = namedtuple('City', ["name", "url", "id"])


class HotelSpider(scrapy.Spider):
    name = "hotel"
    __host = "https://hotels.ctrip.com"
    _k1 = "全季酒店"

    def start_requests(self):
        cc = []
        for c in city:
            x = next(x for x in city_data if x['name'] == c)
            cc.append(City(
                name=c,
                url=HotelSpider.__host + '/hotel/' + x['py'] + x['n'] + '/k1' + HotelSpider._k1 ,
                id=x['n'],
            ))
        for c in cc:
            yield scrapy.Request(url=c.url, meta={'city': c}, callback=self.parse_city)

    def parse_city(self, response):
        city = response.meta['city']

        page_btn = response.xpath('//div[@class="c_page_list layoutfix"]/a[@rel="nofollow"]/text()').get()
        pages = int(page_btn) if page_btn else 1

        yield {
            'pages': pages
        }
        self.log(pages)

        return

        urls = response.xpath('//div[@id="hotel_list"]//h2/a/@href').extract()
        for url in urls:
            yield scrapy.Request(url=HotelSpider.__host + url, callback=self.parse)
        response.xpath('//a[@id="downHerf"]/p/text()').get().strip().split('\xc2\xa0\xc2\xa0'.decode('utf8'))
        yield scrapy.Request()

    def parse(self, response):
        desc = response.xpath('//div[@id="htlDes"]/p/text()').get().strip().split('\xc2\xa0\xc2\xa0'.decode('utf8'))
        yield {
            'name': response.xpath('//h2[@class="cn_n"]/text()').get(),
            'en': response.xpath('//h2[@class="en_n"]/text()').get(),
            'start_year': desc[0],
            'size': desc[1],
        }

    def debug(self):
        __import__('IPython').embed()
