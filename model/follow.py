# coding=utf-8
__author__ = 'phithon'
from model.base import BaseModel

try:
    type(u"a") is unicode
except:
    # PY3
    unicode = str


class FollowModel(BaseModel):
    __table__ = "follow_product"
    __invalid__ = {
        "username": {
            "_name": "用户名",
            "_need": True,
            "type": unicode,
            "max_length": 36,
            "min_length": 1,
            "pattern": ur"^[a-zA-Z0-9_\-\u4e00-\u9fa5]+$"
        },
        "site": {
            "_name": "站点",
            "type": unicode,
            "max_length": 128,
        },
        "asin": {
            "_name": "asin",
            "type": unicode,
            "max_length": 128,
        },
        "link": {
            "_name": "产品链接",
            "type": unicode,
            "max_length": 128,
            "url": True
        },
        "offer_link": {
            "_name": "卖家列表",
            "type": unicode,
            "max_length": 128,
            "url": True
        },
        "status": {
            "_name": "状态",
            "type": unicode,
            "max_length": 128,
        }
    }
    __msg__ = {
        "type": "%s类型错误",
        "max_length": "%s长度太长",
        "min_length": "%s长度太短",
        "max": "%s过大",
        "min": "%s过小",
        "email": "%s格式错误",
        "number": "%s必须是数字",
        "url": "%s格式错误",
        "pattern": "%s格式错误"
    }
    error_msg = ""
