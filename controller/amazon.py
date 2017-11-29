# coding=utf-8
__author__ = 'phithon'
import tornado.web
from tornado import gen

from controller.base import BaseHandler


class FollowHandler(BaseHandler):
    def initialize(self):
        super(FollowHandler, self).initialize()
        self.topbar = "跟卖监控"

    @tornado.web.asynchronous
    @gen.coroutine
    def get(self, *args, **kwargs):
        user = yield self.db.member.find_one({
            "username": self.current_user["username"]
        })

        follow_products = [{'username': 'mike', 'name': '五金桌脚', 'site': 'www.amazon.com', 'asin': 'B075NXSZXL',
                            'link': 'https://www.amazon.com/dp/B075NXSZXL',
                            'offer_link': 'https://www.amazon.com/gp/offer-listing/B075NXSZXL/ref=dp_olp_new_mbc?ie=UTF8&condition=new',
                            'status': '运行中'}]

        self.render("follow_product.htm", user=user, follow_products=follow_products)
