#!D:\DEV\Python\Python38-32

import datetime

import xlrd
from xlutils.copy import copy

import scraping_oder_time


def main():
    start_time = datetime.datetime.now()

    # 读取excel单号数据
    workbook = xlrd.open_workbook("order.xls", formatting_info=True)
    sheet = workbook.sheet_by_index(0)
    num_list = sheet.col_values(0)
    date_list = sheet.col_values(1)

    filter_order = []
    for num in enumerate(num_list):
        if date_list[num[0]] == '' and num[1] != '':
            print(num)
            filter_order.append(num)

    # 将每20条数据分组
    group_list = []
    for i in range(0, len(num_list), 20):
        group_list.append(num_list[i:i+20])

    copy_workbook = ""

    for i, order_list in enumerate(group_list):

        # 顺丰官网获取数据
        result_list = scraping_oder_time.scraping_oder_time(
            ",".join(str(v) for v in order_list))

        # 未获取到数据
        if len(result_list) == 0:
            print("数据为空，行号为{}".format(0))
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

            copy_sheet.col(0).width = 5000
            copy_sheet.col(1).width = 5000
            copy_sheet.col(2).width = 5000
            copy_sheet.col(3).width = 5000

            print("第{}行写入数据".format(j + 1))

        copy_workbook.save('order.xls')

    end_time = datetime.datetime.now()
    print((end_time - start_time).seconds)


if __name__ == "__main__":
    main()
