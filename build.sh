#!/bin/bash

yum -y install python3 python3-devel
pip3 install -r requirements.txt -i https://mirrors.tencent.com/pypi/simple/
export LC_ALL="en_US.utf8"

