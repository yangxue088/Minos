# coding=utf-8
import datetime
import json
import shutil
import time

import os
import pymongo
import re
import requests
from lxml import html

from model.follow import FollowModel
from util.function import intval, humantime

__author__ = 'phithon'
import tornado.web
from tornado import gen

from controller.base import BaseHandler


class FollowHandler(BaseHandler):
    def initialize(self):
        super(FollowHandler, self).initialize()
        self.topbar = "跟卖监控"

    def get(self, *args, **kwargs):
        method = "%s_page" % args[0]
        if len(args) == 3:
            arg = args[2]
        else:
            arg = None
        if hasattr(self, method):
            getattr(self, method)(arg)
        else:
            self.custom_error('不存在这个方法')

    def post(self, *args, **kwargs):

        method = "%s_action" % args[0]
        if len(args) == 3:
            arg = args[2]
        else:
            arg = None
        if hasattr(self, method):
            getattr(self, method)(arg)
        else:
            self.custom_error('不存在这个方法')

    @tornado.web.asynchronous
    @gen.coroutine
    def setting_page(self, arg):
        cursor = self.db.follow_product.find({
            "username": self.current_user["username"]
        })
        count = yield cursor.count()
        follow_products = yield cursor.to_list(count)
        self.render("amazon/follow.htm", follow_products=follow_products)

    @tornado.web.asynchronous
    @gen.coroutine
    def delete_action(self, arg):
        username = self.current_user["username"]
        site = self.get_argument('site')
        asin = self.get_argument('asin')

        self.db.follow_product.remove({
            "$and": [
                {'username': username},
                {'site': site},
                {'asin': asin},
            ]})

        self.write({
            "status": 'success',
        })
        raise tornado.web.Finish()

    @tornado.web.asynchronous
    @gen.coroutine
    def add_action(self, arg):
        try:
            username = self.get_current_user()['username']
            choose_site = self.get_body_argument('choose_site')
            batch_asins = self.get_body_argument('batch_asins').split('\r\n')

            cursor = self.db.follow_product.find({
                "username": username
            })
            count = yield cursor.count()
            follow_products = yield cursor.to_list(count)
            exist_asins = [follow_product['link'] for follow_product in follow_products]
            batch_asins = [asin for asin in batch_asins if
                           u'https://{}/dp/{}'.format(choose_site, asin) not in exist_asins]

            if len(batch_asins) + len(exist_asins) > 10:
                self.custom_error('资源限制, 一个用户只能监控10个产品')

            for batch_asin in batch_asins:
                follow = {}

                follow['username'] = username
                follow['site'] = choose_site
                follow['asin'] = batch_asin
                follow['link'] = u'https://{}/dp/{}'.format(choose_site, batch_asin)
                follow['offer_link'] = u'https://{}/gp/offer-listing/{}?ie=UTF8&f_all=true'.format(choose_site,
                                                                                                   batch_asin)
                follow['status'] = u'green'
                follow['image'] = unicode(self.save_image_local(self.get_image_link(follow['link'])))
                follow['check_time'] = datetime.datetime(2000, 1, 1)

                model = FollowModel()

                if not model(follow):
                    self.custom_error(model.error_msg)

                self.db.follow_product.insert(follow)

            self.redirect("setting")
        except:
            self.custom_error('输入有误')

    @tornado.web.asynchronous
    @gen.coroutine
    def detail_page(self, arg):
        site = arg.split('/')[0]
        asin = arg.split('/')[1]

        limit = 20
        page = intval(self.get_argument("page", default=1))
        if not page or page <= 0:
            page = 1

        product_cursor = self.db.follow_product.find({
            "$and": [
                {'username': self.get_current_user()['username']},
                {'site': site},
                {'asin': asin},
            ]})
        products = yield product_cursor.to_list(1)
        image = products[0]['image']

        cursor = self.db.follow_monitor.find({
            "$and": [
                {'site': site},
                {'asin': asin},
            ]})
        count = yield cursor.count()
        cursor.sort([('time', pymongo.DESCENDING)]).limit(limit).skip((page - 1) * limit)

        monitors = yield cursor.to_list(length=limit)
        for monitor in monitors:
            monitor['follows'] = json.loads(monitor['follows'])
            monitor['time'] = monitor['time'].strftime("%Y-%m-%d %H:%M:%S")

        self.render("amazon/follow_detail.htm", image=image, site=site, asin=asin, monitors=monitors, page=page,
                    each=limit, count=count)

    def get_image_link(self, url):
        link = u'404'

        r = requests.get(url)

        if r.status_code == requests.codes.ok:
            tree = html.fromstring(r.content)
            results = tree.xpath('''//li[contains(@class, 'itemNo0')]//img/@src''')
            link = unicode(results[0])
            link = re.sub(r'_.+_', '_SS160_', link)
            print 'url: {}, image: {}'.format(url, link)
        else:
            print 'error in get image, url: {}'.format(url)

        return link

    def save_image_local(self, url):
        if url == '404':
            return '{}/face/404.png'.format(self.settings["static_path"])
        else:
            now = time.time()
            folder = "%s/%s/%s" % (self.settings["imagepath"], humantime(now, "%Y%m"),
                                   humantime(now, "%d"))
            if not os.path.isdir(folder):
                os.makedirs(folder)

            filename = url[url.rfind('/') + 1:]
            image = '{}/{}'.format(folder, filename)

            r = requests.get(url, stream=True)
            if r.status_code == 200:
                with open(image, 'wb') as f:
                    r.raw.decode_content = True
                    shutil.copyfileobj(r.raw, f)

            return image
