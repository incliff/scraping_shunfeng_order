#!D:\DEV\Python\Python38-32
import logging
import random
import urllib.request

import cv2 as cv
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import easing


def crack(driver, retry_num):
    print("start crack")
    try:
        WebDriverWait(driver, 25).until(
            EC.presence_of_element_located((By.ID, "tcaptcha_popup"))
        )

        driver.switch_to.frame("tcaptcha_popup")

        img = driver.find_element_by_id("slideBkg")
        src = img.get_attribute("src")

        urllib.request.urlretrieve(src, "output/img/origin.jpg")

        origin_img = cv.imread('output/img/origin.jpg')

        x_pox = get_pos(origin_img)

        # 如果识别图片失败，将刷新图片重新识别
        if x_pox == 0 and retry_num > 0:
            print("识别图片失败，程序将刷新图片并重新识别")
            driver.find_element_by_xpath(
                "//div[@class='tcaptcha-action tcaptcha-action--refresh']").click()
            driver.switch_to.default_content()
            crack(driver, retry_num - 1)
            return

        drag_button = driver.find_element_by_id("tcaptcha_drag_thumb")

        action_chains = ActionChains(driver)

        drag_length = x_pox / 2 - 24

        fake_drag(driver, drag_button, drag_length)

    except BaseException as e:
        print("破解图片出错: ", e)
        logging.exception(e)

        width = driver.execute_script("return document.documentElement.scrollWidth")
        height = driver.execute_script("return document.documentElement.scrollHeight")
        driver.set_window_size(width, height)
        driver.save_screenshot("./output/img/screenshot/{}.png".format(random.randint(1000, 9999)))
    finally:
        print("破解图片结束")
        print("end crack")


def get_pos(image):
    blurred = cv.GaussianBlur(image, (5, 5), 0)
    canny = cv.Canny(blurred, 200, 400)
    contours, hierarchy = cv.findContours(
        canny, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
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
            cv.imwrite("output/img/done.jpg", image)
            # cv.imshow('image', image)
            return x
    return 0


def fake_drag(browser, knob, offset):
    offsets, tracks = easing.get_tracks(offset, 1, 'ease_out_expo')
    ActionChains(browser).click_and_hold(knob).perform()
    for x in tracks:
        ActionChains(browser).move_by_offset(x, 0).perform()
    ActionChains(browser).pause(0.2).release().perform()
