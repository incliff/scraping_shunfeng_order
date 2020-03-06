#!D:\DEV\Python\Python38-32
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import WebDriverException

import crack


def scraping_oder_time(num_str):

    driver = webdriver.Chrome(
        executable_path="D:\\MyWorkspace\\Python\\shunfeng_order\\chromedriver.exe")
    driver.get(
        "https://www.sf-express.com/cn/sc/dynamic_function/waybill/#search/bill-number/" + num_str)

    crack.crack(driver, 3)

    result = {}
    try:

        deliveries = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located(
                (By.XPATH, "//div[@class='delivery-wrapper']/div[@class='delivery']"))
        )
        print("第一次查询出订单")

        # 点击关闭地图模式
        driver.find_element_by_xpath(
            "//div[@class='fr openMapModel']/input").click()

        # 点击查看更多按钮
        driver.find_element_by_xpath("//div[@class='searchMore']").click()
        print("点击查看更多按钮")

        crack.crack(driver, 3)
        print("破解图片")

        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located(
                (By.XPATH, "//div[@class='delivery-wrapper']/div[@class='noMore']"))
        )
        print("第二次查询出订单")

        deliveries = WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located(
                (By.XPATH, "//div[@class='delivery-wrapper']/div[@class='delivery']"))
        )

        for delivery in deliveries:
            bill_num = delivery.find_element_by_xpath(".//div[@class='bill-num']/span[@class='number']").text
            start_time = delivery.find_element_by_xpath(".//div[@class='route-list']/ul[last()]/li[@class='route-date-time']/span").text
            end_time = delivery.find_element_by_xpath(".//div[@class='route-list']/ul[1]/li[@class='route-date-time']/span").text

            result[bill_num] = {"start_time": start_time, "end_time": end_time}

    except TimeoutException as e:
        print("等待超时：", e)
    except WebDriverException as e:
        print("WebDriverException：", e)
    finally:
        print("准备退出")
        if len(result) != 0:
            driver.quit()
    return result

        
