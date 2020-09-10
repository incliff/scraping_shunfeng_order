#!D:\DEV\Python\Python38-32
import logging
import random

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import crack


def scraping_oder_time(num_str, lock, retry_num=3):
    chrome_options = Options()
    # chrome_options.binary_location = '/usr/bin/chromium-browser'

    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')

    chrome_options.add_argument("window-size=1024,768")
    chrome_options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(executable_path="./driver/chromedriver_80.exe", options=chrome_options)
    driver.get(
        "https://www.sf-express.com/cn/sc/dynamic_function/waybill/#search/bill-number/" + num_str)

    try:
        lock.acquire()
        crack.crack(driver, 3)
    finally:
        lock.release()

    result = {}
    try:
        deliveries = WebDriverWait(driver, 25).until(
            EC.presence_of_all_elements_located(
                (By.XPATH, "//div[@class='delivery-wrapper']/div[@class='delivery']"))
        )

        # 点击关闭地图模式
        driver.find_element_by_xpath("//div[@class='fr openMapModel']/input").click()

        if is_element_exist(driver, "//div[@class='searchMore']"):
            deliveries = search_more_order(driver, lock)

        result = extract_order_data(deliveries)

    except TimeoutException as e:
        logging.exception(e)

        width = driver.execute_script("return document.documentElement.scrollWidth")
        height = driver.execute_script("return document.documentElement.scrollHeight")
        driver.set_window_size(width, height)
        driver.save_screenshot("./output/img/screenshot/scraping_{}.png".format(random.randint(1000, 9999)))

        print("TimeoutException retry_num: {}".format(retry_num))
        if retry_num > 0:
            driver.quit()
            scraping_oder_time(num_str, lock, --retry_num)
    except WebDriverException as e:
        logging.exception(e)
    finally:
        print("查询到数据{}条".format(len(result)) + "，关闭浏览器")
        # driver.quit()
    return result


def extract_order_data(deliveries):
    result = {}
    for delivery in deliveries:
        bill_num = delivery.find_element_by_xpath(".//div[@class='bill-num']/span[@class='number']").text

        start_time = delivery.find_element_by_xpath(
            ".//div[@class='route-list']/ul[last()]/li[@class='route-date-time']/span").text

        end_time = delivery.find_element_by_xpath(
            ".//div[@class='route-list']/ul[1]/li[@class='route-date-time']/span").text

        result[bill_num] = {"start_time": start_time, "end_time": end_time}
    return result


def search_more_order(driver, lock):
    driver.find_element_by_xpath("//div[@class='searchMore']").click()
    print("点击查看更多按钮")

    try:
        lock.acquire()
        crack.crack(driver, 3)
        print("破解图片")
    finally:
        lock.release()

    WebDriverWait(driver, 25).until(
        EC.presence_of_element_located(
            (By.XPATH, "//div[@class='delivery-wrapper']/div[@class='noMore']"))
    )

    deliveries = WebDriverWait(driver, 25).until(
        EC.presence_of_all_elements_located(
            (By.XPATH, "//div[@class='delivery-wrapper']/div[@class='delivery']"))
    )
    return deliveries


def is_element_exist(driver, element):
    flag = True
    try:
        driver.find_element_by_xpath(element)
        return flag

    except WebDriverException:
        flag = False
        return flag
