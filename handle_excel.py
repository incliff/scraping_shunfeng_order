#!D:\DEV\Python\Python38-32
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

import xlrd
from xlutils.copy import copy

import cv2 as cv

import urllib.request
import datetime, time, random
import easing

def get_pos(image):
    blurred = cv.GaussianBlur(image, (5, 5), 0)
    canny = cv.Canny(blurred, 200, 400)
    contours, hierarchy = cv.findContours(canny, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    for i, contour in enumerate(contours):
        M = cv.moments(contour)
        if M['m00'] == 0:
            cx = cy = 0
        else:
            cx, cy = M['m10'] / M['m00'], M['m01'] / M['m00']
        if 6000 < cv.contourArea(contour) < 8000 and 370 < cv.arcLength(contour, True) < 390:
            if cx < 400:
                continue
            x, y, w, h = cv.boundingRect(contour)  # 外接矩形
            cv.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)
            cv.imwrite("done.jpg", image) 
            print({'x': x, "y": y, "w": w, "h": h})
            # cv.imshow('image', image)
            return x
    return 0


def fake_drag(browser, knob, offset):
    offsets, tracks = easing.get_tracks(offset, 1, 'ease_out_expo')
    print(offsets)
    ActionChains(browser).click_and_hold(knob).perform()
    for x in tracks:
        ActionChains(browser).move_by_offset(x, 0).perform()
    ActionChains(browser).pause(0.5).release().perform()

    return

def crack(driver, retry_num):

    try:

        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "tcaptcha_popup"))
        )

        driver.switch_to.frame("tcaptcha_popup")
        # driver.switch_to.frame(0)
        # driver.switch_to.frame(driver.find_element_by_xpath("//iframe[contains(@style,'z-index: 2000000001')]"))

        img = driver.find_element_by_id("slideBkg")
        src = img.get_attribute("src")

        urllib.request.urlretrieve(src, "origin.jpg")

        img0 = cv.imread('./origin.jpg')
        # new_img = cv.resize(img0, (340, 195))
        # cv.imwrite("new_img.jpg", img0) 
        
        x_pox = get_pos(img0)

        # 如果识别图片失败，将刷新图片重新识别
        if x_pox == 0 and retry_num > 0:
            print("识别图片失败，程序将刷新图片并重新识别")
            driver.find_element_by_xpath("//div[@class='tcaptcha-action tcaptcha-action--refresh']").click()
            driver.switch_to.default_content() 
            crack(driver, retry_num - 1)

        drag_button = driver.find_element_by_id("tcaptcha_drag_thumb")

        action_chains = ActionChains(driver)

        drag_length = x_pox / 2 - 24

        fake_drag(driver,drag_button,drag_length)

    finally:
        pass
        


def scraping_oder_time(num_str):

    driver = webdriver.Chrome(executable_path="D:\MyWorkspace\Python\shunfeng_order\chromedriver.exe")
    driver.get("https://www.sf-express.com/cn/sc/dynamic_function/waybill/#search/bill-number/" + num_str)

    crack(driver, 3)

    result = {}
    try:

        deliveries = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, "//div[@class='delivery-wrapper']/div[@class='delivery']"))
        )
        print("第一次查询出订单")

        # 点击关闭地图模式
        driver.find_element_by_xpath("//div[@class='fr openMapModel']/input").click()

        # 点击查看更多按钮
        driver.find_element_by_xpath("//div[@class='searchMore']").click()
        print("点击查看更多按钮")

        crack(driver, 3)
        print("破解图片")

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@class='delivery-wrapper']/div[@class='noMore']"))
        )
        print("第二次查询出订单")

        deliveries = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, "//div[@class='delivery-wrapper']/div[@class='delivery']"))
        )

        print(deliveries)

        for index, delivery in enumerate(deliveries):

            bill_num = delivery.find_element_by_xpath(".//div[@class='bill-num']/span[@class='number']").text
            print("===================={}、{}==================".format(index + 1, bill_num))

            text = delivery.find_element_by_xpath(".//div[@class='route-list']/ul[last()]/li[1]/span").text
            start_time = delivery.find_element_by_xpath(".//div[@class='route-list']/ul[last()]/li[@class='route-date-time']/span").text  
            print({"text": text, "start_time": start_time})

            text = delivery.find_element_by_xpath(".//div[@class='route-list']/ul[1]/li[1]/span").text
            end_time = delivery.find_element_by_xpath(".//div[@class='route-list']/ul[1]/li[@class='route-date-time']/span").text  
            print({"text": text, "end_time": end_time})
            
            result[bill_num] = {"start_time": start_time, "end_time": end_time}

        print("打印完毕")

    # except TimeoutException as e:
    #     print("等待超时")

    finally:
        print("准备退出")
        if len(result) != 0:
            driver.quit()
        return result


start = datetime.datetime.now()

# 读取excel单号数据
workbook = xlrd.open_workbook("order.xls")
sheet = workbook.sheet_by_index(0)
num_list = sheet.col_values(0)


# 将每20条数据分组
group_list = []
for i in range(0, len(num_list), 20):
    group_list.append(num_list[i:i+20])


row = 0 
copy_workbook = ""

for i, order_list in enumerate(group_list):

    # 顺丰官网获取数据
    result_list = scraping_oder_time(",".join(str(v) for v in order_list))

    # 未获取到数据
    if len(result_list) == 0:
        print("数据为空，行号为{}".format(row))
        continue

    if copy_workbook == "":
        copy_workbook = copy(workbook)

    copy_sheet = copy_workbook.get_sheet(0)

    for j, num in enumerate(num_list):
        order = result_list.get(num, -1)
        if order == -1:
            continue
        copy_sheet.write(j, 1, num)
        copy_sheet.write(j, 2, order['start_time'])
        copy_sheet.write(j, 3, order['end_time'])
        print("第{}行写入数据".format(j + 1))

    copy_workbook.save('order.xls')

end = datetime.datetime.now()

print((end-start).seconds)

