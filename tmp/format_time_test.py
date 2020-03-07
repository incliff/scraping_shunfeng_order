# format time
def format_datetime(between_seconds, accurate_unit=0):
    # accurate_unit 0 秒, 1 分, 2 小时, 3 天

    if between_seconds == 0:
        return ""

    elif between_seconds < 60:
        return "{}秒 ".format(between_seconds)

    elif 60 <= between_seconds < 3600:
        return "{}分 ".format(between_seconds // 60) + (
            format_datetime(between_seconds % 60, accurate_unit) if accurate_unit < 1 else "")

    elif 3600 <= between_seconds < 86400:
        return "{}小时 ".format(between_seconds // 3600) + (
            format_datetime(between_seconds % 3600, accurate_unit) if accurate_unit < 2 else "")

    elif between_seconds >= 86400:
        return "{}天 ".format(between_seconds // 86400) + (
            format_datetime(between_seconds % 86400, accurate_unit) if accurate_unit < 3 else "")


print(format_datetime(10000000, accurate_unit=1))
