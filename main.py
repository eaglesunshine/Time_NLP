# -*- coding: utf-8 -*-
# @author: linwanpeng
# @software: PyCharm
# @file: main.py
# @time: 2022/3/8 14:41
# 对外http服务

import logging

from api import api
from flask import Flask

LOG_FILE_PATH = "/data/log/flask.log"

logging.basicConfig(level=logging.DEBUG)
app = Flask(__name__)

# 注册蓝图
app.register_blueprint(api)

if __name__ == "__main__":
    # 设置日志
    handler = logging.FileHandler(LOG_FILE_PATH, encoding='UTF-8')
    logging_format = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(lineno)s - %(message)s')
    handler.setFormatter(logging_format)
    app.logger.addHandler(handler)

    # 启动服务
    app.run(debug=False, host="0.0.0.0", port=5001)
