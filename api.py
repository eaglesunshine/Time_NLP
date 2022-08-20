# -*- coding: utf-8 -*-
# @author: linwanpeng
# @software: PyCharm
# @file: api.py
# @time: 2022/3/8 14:41
# 对外http接口

import json
import os
import requests

from TimeNormalizer import TimeNormalizer
from flask import Blueprint, redirect
from flask import current_app
from flask import make_response
from flask import request

from my_redis import RedisClient

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


@api.route("/relay/login", methods=['GET'])
def index():
    """
    前端第一次登录需要重定向跳转，来获取用户信息
    """
    redirect_uri = "http://www.alarmclock.com.cn/relay/user"

    # 获取SuiteID
    suite_id = os.getenv('SuiteID', '')
    current_app.logger.info('SuiteID：{}'.format(suite_id))

    if not suite_id:
        return make_response('Internal Server Error', 500)

    # 跳转链接
    login_url = "https://open.weixin.qq.com/connect/oauth2/authorize?appid={suite_id}&redirect_uri={redirect_uri}&" \
                "response_type=code&scope=snsapi_userinfo&state=STATE#wechat_redirect"
    login_url = login_url.format(
        suite_id=suite_id,
        redirect_uri=redirect_uri
    )

    current_app.logger.info('login_url：{}'.format(login_url))

    return redirect(login_url)

@api.route("/relay/user", methods=['GET'])
def userinfo():
    """
    解析用户信息
    """

    # 获取code
    code = request.args.get('code')
    current_app.logger.info('code：{}'.format(code))

    if not code:
        return make_response("Bad Request", 400)

    # 获取suite_access_token
    url="http://127.0.0.1:8000/api/suite_access_token"
    res = requests.get(url=url, timeout=60)
    res_info = res.json()

    current_app.logger.info('urle：{}'.format(url))
    current_app.logger.info('res：{}'.format(str(res)))
    current_app.logger.info('res_info：{}'.format(res_info))

    suite_access_token=res_info.get('suite_access_token', '')

    # 获取访问用户信息
    req_param = {
        "code": code,
        "suite_access_token": suite_access_token,
    }

    url="https://qyapi.weixin.qq.com/cgi-bin/service/getuserinfo3rd"
    res = requests.post(url=url, data=req_param, timeout=60)
    user_info = res.json()

    current_app.logger.info('url：{}'.format(url))
    current_app.logger.info('req_param：{}'.format(str(req_param)))
    current_app.logger.info('user_info：{}'.format(user_info))

    if res_info.get('errcode') !=0:
        return make_response('Internal Server Error', 500)

    # 解析user id
    user_id = user_info.get('UserId','')
    corp_id = user_info.get('CorpId','')

    # 完整的用户信息可以缓存起来，可能后续有用，信息包括了：CorpId、UserId、DeviceId、user_ticket、open_userid
    key = "{}-userinfo".format(user_id)
    alive = int(user_info.get('expires_in', 1800))

    r = RedisClient()
    r.setex(name=key, time=alive, value=json.dumps(user_info))
    current_app.logger.info('save userinfo in redis, userid={}, alive:{}'.format(user_id, str(alive)))

    # 跳转至web端
    redirect_url = "http://www.alarmclock.com.cn/remind/home?user_id={}&corp_id={}".format(user_id, corp_id)

    current_app.logger.info('redirect_url：{}'.format(redirect_url))

    return redirect(redirect_url)