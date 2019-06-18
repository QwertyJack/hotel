#!/bin/bash
#
# main.sh
# Copyright (C) 2019 jack <jack@6k>
#
# Distributed under terms of the MIT license.
#

scrapy crawl -t csv hotel -o ./qj.csv -a k1=全季酒店
# scrapy crawl -t csv hotel -o ./wyn.csv -a k1=维也纳
