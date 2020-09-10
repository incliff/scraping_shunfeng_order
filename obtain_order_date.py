#!D:\DEV\Python\Python38-32

import argparse
import logging
import time
from datetime import datetime
from functools import partial
from multiprocessing import Pool, Manager

import xlrd
import xlwt
from xlutils.copy import copy

import scraping

timeout = 7 * 24 * 60 * 60


def main(excel_path):
    try:
        start_time = datetime.now()

        print("存放数据的excel路径: {}".format(excel_path))
        order_length = scraping_and_save_to_excel(excel_path)

        end_time = datetime.now()
        user_time = (end_time - start_time).seconds
        print("共查询数据 {} 条，用时 {}，平均每条用时 {} 秒".format(
            order_length,
            format_datetime(user_time),
            round(user_time / order_length, 2)
        ))
        time.sleep(3)

    except PermissionError as e:
        print_error(e, "请在关闭【order.xls】文件后，重新执行脚本。")
    except BaseException as e:
        print_error(e, "数据处理出错，点击【回车键】关闭命令行")
    finally:
        pass


def print_error(e, text):
    logging.exception(e)
    time.sleep(1)
    input("=======================================\n"
          "==== " + text + " ===\n"
                           "=======================================")


def scraping_and_save_to_excel(excel_path):
    workbook = xlrd.open_workbook(excel_path, formatting_info=True)

    order_num_list = read_order_num_from_excel(workbook)

    # 将每20条数据分组
    group_list = [order_num_list[i:i + 20] for i in range(0, len(order_num_list), 20)]

    num_list_str_list = []
    for i, order_list in enumerate(group_list):
        num_list_iter = map(lambda x: x[1], order_list)
        num_list_str_list.append(",".join(str(v) for v in num_list_iter))

    # 多进程抓取数据
    p = Pool(4)
    wrap_func = partial(scraping.scraping_oder_time, lock=Manager().Lock())
    result_list = p.map(wrap_func, num_list_str_list)
    p.close()
    p.join()

    result_dict = {}
    for x in result_list:
        result_dict.update(x)

    print("查询结果{}条：{}".format(len(result_dict), result_dict))

    # 未获取到数据
    if len(result_dict) != 0:
        write_to_excel(workbook, order_num_list, result_dict, excel_path)

    return len(order_num_list)


# 读取excel单号数据
def read_order_num_from_excel(workbook):
    sheet = workbook.sheet_by_index(0)
    num_list = sheet.col_values(0)
    date_list = sheet.col_values(1)
    filter_order = []
    for num in enumerate(num_list):
        if date_list[num[0]] == '' and num[1] != '':
            filter_order.append(num)
    return filter_order


def write_to_excel(workbook, order_list, result_dict, excel_path):
    copy_workbook = copy(workbook)
    copy_sheet = copy_workbook.get_sheet(0)

    style = get_red_style_cell()

    for j, num in enumerate(order_list):
        row_num = num[0]
        order_num = num[1]
        order_date = result_dict.get(order_num.strip(), -1)
        if order_date == -1:
            continue

        copy_sheet.write(row_num, 1, order_num)
        copy_sheet.write(row_num, 2, order_date['start_time'])
        copy_sheet.write(row_num, 3, order_date['end_time'])

        between_seconds = (
                datetime.strptime(order_date['start_time'], '%Y-%m-%d %H:%M') -
                datetime.strptime(order_date['end_time'], '%Y-%m-%d %H:%M')
        ).seconds

        if between_seconds >= timeout:
            copy_sheet.write(row_num, 4, format_datetime(between_seconds, accurate_unit=1), style)
        else:
            copy_sheet.write(row_num, 4, format_datetime(between_seconds, accurate_unit=1))

        # 设置列宽
        copy_sheet.col(0).width = 5000
        copy_sheet.col(1).width = 5000
        copy_sheet.col(2).width = 5000
        copy_sheet.col(3).width = 5000

        print("第{}行写入数据".format(row_num + 1))
    copy_workbook.save(excel_path)


def get_red_style_cell():
    pattern = xlwt.Pattern()  # Create the Pattern
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN  # May be: NO_PATTERN, SOLID_PATTERN, or 0x00 through 0x12
    pattern.pattern_fore_colour = 2  # May be: 8 through 63. 0 = Black, 1 = White, 2 = Red, 3 = Green, 4 = Blue, 5 = Yellow, 6 = Magenta, 7 = Cyan, 16 = Maroon, 17 = Dark Green, 18 = Dark Blue, 19 = Dark Yellow , almost brown), 20 = Dark Magenta, 21 = Teal, 22 = Light Gray, 23 = Dark Gray, the list goes on...
    style = xlwt.XFStyle()  # Create the Pattern
    style.pattern = pattern  # Add Pattern to Style
    return style


# accurate_unit 0 秒, 1 分, 2 小时, 3 天
def format_datetime(between_seconds, accurate_unit=0):
    if between_seconds == 0:
        return ""

    elif between_seconds < 60:
        return "{} 秒 ".format(between_seconds)

    elif 60 <= between_seconds < 3600:
        return "{} 分 ".format(between_seconds // 60) + (
            format_datetime(between_seconds % 60, accurate_unit) if accurate_unit < 1 else "")

    elif 3600 <= between_seconds < 86400:
        return "{} 小时 ".format(between_seconds // 3600) + (
            format_datetime(between_seconds % 3600, accurate_unit) if accurate_unit < 2 else "")

    elif between_seconds >= 86400:
        return "{} 天 ".format(between_seconds // 86400) + (
            format_datetime(between_seconds % 86400, accurate_unit) if accurate_unit < 3 else "")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="scraping shunfeng order data")
    parser.add_argument("--path", "-p", help="存放数据的excel路径，非必要参数", default="order.xls")
    parser.add_argument("--timeout_day", "-t", help="订单时间差的超时时长，非必要参数", default=7)
    args = parser.parse_args()

    day = args.timeout_day
    timeout = day * 24 * 60 * 60
    main(args.path)
