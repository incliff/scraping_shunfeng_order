from selenium import webdriver
from selenium.webdriver import ActionChains

# from selenium.webdriver.common.action_chains import ActionChains

import cv2 as cv

import urllib.request
import time, random
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
            cv.imwrite("saving.jpg", image) 
            print({'x': x, "y": y, "w": w, "h": h})
            # cv.imshow('image', image)
            return x
    return 0


def fake_drag(browser, knob, offset):
    # seconds = random.uniform(2, 6)
    # print(seconds)
    # samples = int(seconds*10)
    # diffs = sorted(random.sample(range(0, offset), samples-1))
    # diffs.insert(0, 0)
    # diffs.append(offset)
    # ActionChains(browser).click_and_hold(knob).perform()
    # for i in range(samples):
    #     ActionChains(browser).pause(seconds/samples).move_by_offset(diffs[i+1]-diffs[i], 0).perform()
    # ActionChains(browser).release().perform()

    # tracks = get_track(offset)
    offsets, tracks = easing.get_tracks(offset, 12, 'ease_out_expo')
    print(offsets)
    ActionChains(browser).click_and_hold(knob).perform()
    for x in tracks:
        ActionChains(browser).move_by_offset(x, 0).perform()
    ActionChains(browser).pause(0.5).release().perform()

    return



driver = webdriver.Chrome(executable_path="D:\DEV\chromedriver.exe")
driver.get("https://www.sf-express.com/cn/sc/dynamic_function/waybill/")

elem = driver.find_element_by_class_name("token-input")
elem.clear()
elem.send_keys("291305897906")

button = driver.find_element_by_id("queryBill")
button.click()


time.sleep(8)


driver.switch_to.frame("tcaptcha_popup")
# driver.switch_to.frame(0)
# driver.switch_to.frame(driver.find_element_by_xpath("//iframe[contains(@style,'z-index: 2000000001')]"))

img = driver.find_element_by_id("slideBkg")
src = img.get_attribute("src")

urllib.request.urlretrieve(src, "local-filename.jpg")


img0 = cv.imread('./local-filename.jpg')
# new_img = cv.resize(img0, (340, 195))
# cv.imwrite("new_img.jpg", img0) 
x_pox = get_pos(img0)


drag_button = driver.find_element_by_id("tcaptcha_drag_thumb")

action_chains = ActionChains(driver)

drag_length = x_pox / 2 - 24

print(drag_length)

# for num in range(1,3):
#     print(num)
#     action_chains.click_and_hold(drag_button).move_to_element_with_offset(drag_button, drag_length / 3, 1).perform()
#     time.sleep(random.randint(10,50)/100)
    # action_chains.move_to_element_with_offset(drag_button, 10, 1).perform()
    # drag_and_drop_by_offset

# action_chains.drag_and_drop_by_offset(drag_button, drag_length, 1).perform()
# print("移动完毕 ")
# action_chains.release(drag_button).perform()

# fake_drag(driver,drag_button,drag_length)

# div class="route-list" ul li span

driver.find_element_by_xpath("//div[@class='route-list']/ul[1]/li[1]/span").text



print("向左移动： ", x_pox/2)


