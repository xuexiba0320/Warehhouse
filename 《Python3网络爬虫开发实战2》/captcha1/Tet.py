import time, random
import PIL.Image as image
from io import BytesIO
from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests, json, re, urllib
from bs4 import BeautifulSoup
from urllib.request import urlretrieve


import ssl
ssl._create_default_https_context = ssl._create_unverified_context



class Crack():
    def __init__(self):
        self.url = 'https://www.zdao.com/captcha?redirect_url=https://www.zdao.com%2F'
        self.browser = webdriver.Chrome()
        self.wait = WebDriverWait(self.browser, 100)
        self.BORDER = 6

    def __del__(self):
        time.sleep(5)
        self.browser.close()

    def get_screenshot(self):
        """
        获取网页截图
        :return: 截图对象
        """
        screenshot = self.browser.get_screenshot_as_png()
        screenshot = Image.open(BytesIO(screenshot))
        return screenshot

    def get_position(self):
        """
        获取验证码位置
        :return: 验证码位置元组
        """
        img = self.browser.find_element_by_class_name("gt_box")
        time.sleep(2)
        location = img.location
        size = img.size
        top, bottom, left, right = location['y'], location['y'] + size['height'], location['x'], location['x'] + size[
            'width']
        return (top, bottom, left, right)



    def get_images(self, bg_filename='bg.jpg', fullbg_filename='fullbg.jpg'):
        """
        获取验证码图片
        :return: 图片的location信息
        """
        bg = []
        fullgb = []
        while bg == [] and fullgb == []:

            bf = BeautifulSoup(self.browser.page_source, 'lxml')
            bg = bf.find_all('div', class_='gt_cut_bg_slice')
            fullgb = bf.find_all('div', class_='gt_cut_fullbg_slice')


        print("re前缺口图list",bg)
        print("re前完整的图list",fullgb)

        bg_url = re.findall('url\(\"(.*)\"\);', bg[0].get('style'))[0].replace('webp', 'jpg')
        fullgb_url = re.findall('url\(\"(.*)\"\);', fullgb[0].get('style'))[0].replace('webp', 'jpg')

        print("re后缺口图list", bg_url)
        print("re后完整的图list", fullgb_url)

        bg_location_list = []
        fullbg_location_list = []

    # 取得图片坐标
        for each_bg in bg:
            location = {}
                                         #background-position: -157px -58px;
            location['x'] = int(re.findall('background-position: (.*)px (.*)px;', each_bg.get('style'))[0][0])
            location['y'] = int(re.findall('background-position: (.*)px (.*)px;', each_bg.get('style'))[0][1])
            bg_location_list.append(location)
    #取得图片坐标列表
        for each_fullgb in fullgb:
            location = {}
            location['x'] = int(re.findall('background-position: (.*)px (.*)px;', each_fullgb.get('style'))[0][0])
            location['y'] = int(re.findall('background-position: (.*)px (.*)px;', each_fullgb.get('style'))[0][1])
            fullbg_location_list.append(location)

    #使用urlretrieve下载图片并保存

        urlretrieve(url=bg_url, filename=bg_filename)
        print('缺口图片下载完成')

        urlretrieve(url=fullgb_url, filename=fullbg_filename)
        print('背景图片下载完成')

    #返回坐标列表
        return bg_location_list, fullbg_location_list

    def get_merge_image(self, filename, location_list):
        """
        根据位置对图片进行合并还原
        :filename:图片
        :location_list:图片位置
        """
        im = image.open(filename)

    #浏览器生成的图片规格是260px * 116px , 所以指定image.new('RGB', (260, 116))·
        new_im = image.new('RGB', (260, 116))
        im_list_upper = []
        im_list_down = []

        for location in location_list:
            if location['y'] == -58:
                im_list_upper.append(im.crop((abs(location['x']), 58, abs(location['x']) + 10, 166)))
            if location['y'] == 0:
                im_list_down.append(im.crop((abs(location['x']), 0, abs(location['x']) + 10, 58)))
        new_im = image.new('RGB', (260, 116))
        x_offset = 0
        for im in im_list_upper:
            new_im.paste(im, (x_offset, 0))
            x_offset += im.size[0]
        x_offset = 0
        for im in im_list_down:
            new_im.paste(im, (x_offset, 58))
            x_offset += im.size[0]
        new_im.save(filename)
        return new_im

    def open(self):
        self.browser.get(self.url)

    def get_slider(self):
        """
        获取滑块
        :return: 滑块对象
        """
        while True:
            try:
                slider = self.browser.find_element_by_xpath("//div[@class='gt_slider_knob gt_show']")
                break
            except:
                time.sleep(0.5)
        return slider

    def get_gap(self, img1, img2):
        """
        获取缺口偏移量
        :param img1: 不带缺口图片
        :param img2: 带缺口图片
        :return:
        """
        left = 43
        for i in range(left, img1.size[0]):
            for j in range(img1.size[1]):
                if not self.is_pixel_equal(img1, img2, i, j):
                    left = i
                    return left
        return left

    def is_pixel_equal(self, img1, img2, x, y):
        """
        判断两个像素是否相同
        :param image1: 图片1
        :param image2: 图片2
        :param x: 位置x
        :param y: 位置y
        :return: 像素是否相同
        """
        # 取两个图片的像素点
        pix1 = img1.load()[x, y]
        pix2 = img2.load()[x, y]
        threshold = 60
        if (abs(pix1[0] - pix2[0] < threshold) and abs(pix1[1] - pix2[1] < threshold) and abs(
                        pix1[2] - pix2[2] < threshold)):
            return True
        else:
            return False

    def get_track(self, distance):
        """
        根据偏移量获取移动轨迹
        :param distance: 偏移量
        :return: 移动轨迹
        """
        print("="*10,distance)
        # 移动轨迹
        track = []
        # 当前位移
        current = 0
        # 减速阈值
        mid = distance * 4 / 5
        print(mid)
        # 计算间隔
        t = 0.2
        # 初速度
        v = 0

        while current < distance:
            if current < mid:
                # 加速度为正2
                a = 4
            else:
                # 加速度为负3
                a = -3.5
            # 初速度v0
            v0 = v
            # 当前速度v = v0 + at
            v = v0 + a * t
            # 移动距离x = v0t + 1/2 * a * t^2
            move = v0 * t + 1 / 2 * a * t * t
            # 当前位移
            current += move
            # 加入轨迹
            track.append(round(move))
        return track

    def move_to_gap(self, slider, track):
        """
        拖动滑块到缺口处
        :param slider: 滑块
        :param track: 轨迹
        :return:
        """
        ActionChains(self.browser).click_and_hold(slider).perform()
        a = []
        b = track
        for x in track:

            ActionChains(self.browser).move_by_offset(xoffset=x, yoffset=0).perform()

        time.sleep(0.5)
        ActionChains(self.browser).release().perform()

    def crack(self):
        # 打开浏览器，访问指定网页

        self.open()

        # 保存的图片名字
        bg_filename = 'bg.jpg'
        fullbg_filename = 'fullbg.jpg'

        # 获取图片
        bg_location_list, fullbg_location_list = self.get_images(bg_filename, fullbg_filename)

        # 根据位置对图片进行合并还原
        bg_img = self.get_merge_image(bg_filename, bg_location_list)
        fullbg_img = self.get_merge_image(fullbg_filename, fullbg_location_list)
        print(fullbg_img,"&&&&&&&&&&&&")

        # 点按呼出缺口
        slider = self.get_slider()
        #
        # 获取缺口位置
        gap = self.get_gap(fullbg_img, bg_img)

        print('缺口位置', gap)
        #gap - self.BORDER 是定义了一个调试数值，看__init__里有BORDER，gap减去调试值
        track = self.get_track(gap - self.BORDER)
        print('滑动滑块')
        print(track)
        self.move_to_gap(slider, track)



if __name__ == '__main__':
    print('开始验证')
    crack = Crack()
    crack.crack()
    print('验证成功')

