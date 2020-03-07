#!D:\DEV\Python\Python38-32

import datetime

import xlrd
from xlutils.copy import copy

import scraping


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
            filter_order.append(num)

    # 将每20条数据分组
    group_list = [filter_order[i:i + 20] for i in range(0, len(filter_order), 20)]

    copy_workbook = ""

    for i, order_list in enumerate(group_list):

        # 顺丰官网获取数据
        num_list = map(lambda x: x[1], order_list)
        result_list = scraping.scraping_oder_time(",".join(str(v) for v in num_list))

        # 未获取到数据
        if len(result_list) == 0:
            print("数据为空，行号为{}".format(0))
            continue

        if copy_workbook == "":
            copy_workbook = copy(workbook)

        copy_sheet = copy_workbook.get_sheet(0)

        for j, num in enumerate(order_list):
            order = result_list.get(num[1].strip(), -1)
            if order == -1:
                continue

            copy_sheet.write(num[0], 1, num[1])
            copy_sheet.write(num[0], 2, order['start_time'])
            copy_sheet.write(num[0], 3, order['end_time'])

            copy_sheet.col(0).width = 5000
            copy_sheet.col(1).width = 5000
            copy_sheet.col(2).width = 5000
            copy_sheet.col(3).width = 5000

            print("第{}行写入数据".format(num[0] + 1))

        copy_workbook.save('order.xls')

    end_time = datetime.datetime.now()
    user_time = (end_time - start_time).seconds
    print("共查询数据 {} 条，用时 {} 秒，平均每条用时 {} 秒".format(
        len(filter_order),
        user_time,
        round(user_time / len(filter_order), 2)
    ))


if __name__ == "__main__":
    main()
