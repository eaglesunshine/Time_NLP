# -*- coding: utf-8 -*-
# @author: linwanpeng
# @software: PyCharm
# @file: api.py
# @time: 2022/3/8 14:41
# 对外http接口

import json
import os

from TimeNormalizer import TimeNormalizer
from flask import Blueprint, redirect
from flask import current_app
from flask import make_response
from flask import request

api = Blueprint('nlp_api', __name__)

# 创建实例
client = TimeNormalizer()


def response(resp_data, message: str = "", code: int = 200):
    """
    构造响应对象
    """

    # 返回json
    data = {
        "output": resp_data,
        "message": message
    }

    resp = make_response(json.dumps(data), code)
    resp.headers['Content-type'] = 'application/json'

    return resp


@api.route("/nlp", methods=['POST'])
def nlp():
    """
    请求格式：
    {
        "content": "xxx"    //待解析字符串
    }

    返回格式：
    {
        "output": xxx,              //调用方法返回的内容
        "message": "success or err_info"
    }
    """

    try:

        # 解析请求数据
        try:
            data = request.get_data()
            req_data = json.loads(data)
            current_app.logger.info('req_data：{}'.format(str(req_data)))
        except Exception as err:  # pylint: disable=broad-except
            current_app.logger.error('err_info：{}'.format(str(err)))
            return response(None, "request data parse failed", 200)

        # 获取参数信息
        content = req_data.get('content')
        if not content:
            return response(None, "content is empty", 200)

        # Time_NLP执行解析
        resp_data = client.parse(target=content)
        current_app.logger.info('resp_data：{}'.format(str(resp_data)))

        return response(resp_data=resp_data)

    except Exception as err:  # pylint: disable=broad-except
        current_app.logger.error('err_info：{}'.format(str(err)))
        return response(None, "service error, {}".format(str(err)), 200)


@api.route("/test", methods=['GET'])
def test():
    """
    测试nlp
    """
    content = u'测试：今年儿童节晚上九点一刻'
    current_app.logger.info('resp_data：{}'.format(str(content)))
    resp_data = client.parse(target=content)
    current_app.logger.info('resp_data：{}'.format(str(resp_data)))
    return response(resp_data=resp_data)


@api.route("/remind/login", methods=['GET', 'POST'])
def index():
    """
    前端第一次登录需要重定向跳转，来获取用户信息
    """
    redirect_uri = "http://www.alarmclock.com.cn/login"

    # 获取SuiteID
    suite_id = os.getenv('SuiteID', '')

    # 跳转链接
    login_url = "https://open.weixin.qq.com/connect/oauth2/authorize?appid={suite_id}&redirect_uri={redirect_uri}&" \
                "response_type=code&scope=snsapi_userinfo&state=STATE#wechat_redirect"
    login_url = login_url.format(
        suite_id=suite_id,
        redirect_uri=redirect_uri
    )

    return redirect(login_url)
