#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

import logging
from waveshare_epd import epd1in54_V2
import time
from PIL import Image,ImageDraw,ImageFont
import traceback
import smbus2
import bme280
import socket
import uuid
import subprocess
from decimal import Decimal

logging.basicConfig(level=logging.DEBUG)

try:
    # 环境检测模块常量
    port = 1
    address = 0x77
    bus = smbus2.SMBus(port)
    calibration_params = bme280.load_calibration_params(bus, address)

    # 初始化墨水屏
    epd = epd1in54_V2.EPD()
    epd.init(0)
    # epd.Clear(0xFF)
    
    # image = Image.new('1', (epd.width, epd.height), 255)
    # draw = ImageDraw.Draw(image)
    fontS = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 14)
    font = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)
    font36 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 36)
    # 200*200
    # draw.text((8, 55), u'智能总控台', font = font36, fill = 0)
    # draw.text((8, 100), u'正在启动...', font = font, fill = 0)
    # image = image.transpose(Image.ROTATE_180) 
    # epd.display(epd.getbuffer(image.rotate(90)))
    # time.sleep(1)

    image1 = Image.new('1', (epd.width, epd.height), 255)
    time_image = image1
    epd.displayPartBaseImage(epd.getbuffer(time_image))
    time_image = time_image.transpose(Image.ROTATE_180)
    epd.init(1)
    time_draw = ImageDraw.Draw(time_image)
    # 获取MAC地址
    def get_mac_address():
        mac = uuid.UUID(int=uuid.getnode()).hex[-12:]
        return ":".join([mac[e:e + 2] for e in range(0, 11, 2)])
    # 获取IP地址
    def get_host_ip():
        try:
            my = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            my.connect(('8.8.8.8', 80))
            ip = my.getsockname()[0]
        finally:
            my.close()
        return ip
    # 获取CPU温度
    def get_cpu_temp():
        tempFile = open( "/sys/class/thermal/thermal_zone0/temp" )
        cpu_temp = tempFile.read()
        tempFile.close()
        return str(int(cpu_temp) / 1000)
    # 四舍五入
    def rounding(int,numStr):
        return Decimal(int).quantize(Decimal(numStr), rounding = "ROUND_HALF_UP")
    while (True):
        # 读取环境数据
        data = bme280.sample(bus, address, calibration_params)
        # print(data.timestamp) # 时间戳
        # print(data.temperature) # 温度
        # print(data.pressure) # 气压 hPa
        # print(data.humidity) # 湿度 ％
        time_draw.rectangle((0, 0, 200, 200), fill = 255)
        time_draw.text((36, 3), time.strftime('%Y-%m-%d'), font = font, fill = 0)
        time_draw.text((25, 30), time.strftime('%H:%M:%S'), font = font36, fill = 0)
        time_draw.line((0, 72, 200, 72), fill = 0)
        time_draw.text((10, 75), u'温度：'+str(rounding(data.temperature,'0.1'))+u'度', font = font, fill = 0)
        time_draw.line((0, 102, 200, 102), fill = 0)
        time_draw.text((10, 105), u'湿度：'+str(rounding(data.humidity,'0.1'))+u'％', font = font, fill = 0)
        time_draw.line((0, 132, 200, 132), fill = 0)
        time_draw.text((10, 135), u'气压：'+str(rounding(data.pressure,'1.'))+u'hPa', font = font, fill = 0)
        time_draw.line((0, 165, 200, 165), fill = 0)
        time_draw.text((10, 168), u'本机IP地址'+get_host_ip(), font = fontS, fill = 0)
        time_draw.text((10, 186), u'本机CPU当前温度：'+str(rounding(get_cpu_temp(),'0.1'))+u'度', font = fontS, fill = 0)
        newimage = time_image.crop([10, 10, 120, 50])
        time_image.paste(newimage, (10,10)) 
        epd.displayPart(epd.getbuffer(time_image))
        # time.sleep(0.5)
    
    # epd.sleep()
        
except IOError as e:
    logging.info(e)
    
except KeyboardInterrupt:    
    logging.info("ctrl + c:")
    epd1in54_V2.epdconfig.module_exit()
    exit()
