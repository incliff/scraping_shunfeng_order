from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

import time



driver = webdriver.Chrome(executable_path="D:\DEV\chromedriver.exe")
# driver.get("https://www.sf-express.com/cn/sc/dynamic_function/waybill/#search/bill-number/291305897906")
driver.get("https://www.sf-express.com/cn/sc/dynamic_function/waybill/#search/bill-number/SF1071817875791,SF1071817875904,SF1071817875861,SF1071817875959,288218304352,SF1071817875898,SF1071817875782,288218304264,SF1071817875870,SF1071817875825,SF1071817876025,SF1071817876016,SF1071817876034,SF1071817876122,SF1071817876061,SF1071817876140,SF1071817876104,SF1071817876186,SF1071817876201,288313684364")


try:

    deliveries = WebDriverWait(driver, 15).until(
        EC.presence_of_all_elements_located((By.XPATH, "//div[@class='delivery-wrapper']/div[@class='delivery']"))
    )

    # open_map_checkbox = WebDriverWait(driver, 3).until(
    #     EC.presence_of_element_located((By.XPATH, "//div[@class='fr openMapModel']/input"))
    # )
    # open_map_checkbox.click()
    driver.find_element_by_xpath("//div[@class='fr openMapModel']/input").click()

    for index, delivery in enumerate(deliveries):

        bill_num = delivery.find_element_by_xpath(".//div[@class='bill-num']/span[@class='number']").text
        print("===================={}、{}==================".format(index + 1, bill_num))
        print(bill_num)

        text = delivery.find_element_by_xpath(".//div[@class='route-list']/ul[1]/li[1]/span").text
        time = delivery.find_element_by_xpath(".//div[@class='route-list']/ul[1]/li[@class='route-date-time']/span").text  
        print({"text": text, "time": time})

        text = delivery.find_element_by_xpath(".//div[@class='route-list']/ul[last()]/li[1]/span").text
        time = delivery.find_element_by_xpath(".//div[@class='route-list']/ul[last()]/li[@class='route-date-time']/span").text  
        print({"text": text, "time": time})
    print("打印完毕")

except TimeoutException as e:
    print("等待超时")

finally:
    print("准备退出")
    driver.quit()

# time.sleep(10)

# deliveries = driver.find_elements_by_xpath("//div[@class='delivery-wrapper']/div[@class='delivery']")

# for index, delivery in enumerate(deliveries):

#     bill_num = delivery.find_element_by_xpath(".//div[@class='bill-num']/span[@class='number']").text
#     print("===================={}、{}==================".format(index + 1, bill_num))
#     print(bill_num)

#     text = delivery.find_element_by_xpath(".//div[@class='route-list']/ul[1]/li[1]/span").text
#     time = delivery.find_element_by_xpath(".//div[@class='route-list']/ul[1]/li[@class='route-date-time']/span").text  
#     print({"text": text, "time": time})

#     text = delivery.find_element_by_xpath(".//div[@class='route-list']/ul[last()]/li[1]/span").text
#     time = delivery.find_element_by_xpath(".//div[@class='route-list']/ul[last()]/li[@class='route-date-time']/span").text  
#     print({"text": text, "time": time})


    