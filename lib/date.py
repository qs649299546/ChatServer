from datetime import datetime, date


FORMAT_DATETIME = '%Y-%m-%d %H:%M:%S'
FORMAT_DATETIME_NO_SECONDS = '%Y-%m-%d %H:%M'


def strptime(dt_str, raise_error=True):
    if not dt_str:
        return None

    time_format = FORMAT_DATETIME if dt_str.count(':') == 2 else FORMAT_DATETIME_NO_SECONDS

    try:
        ret = datetime.strptime(dt_str, time_format)
    except ValueError:
        if raise_error:
            raise ValueError('"{0}" 时间格式错误'.format(dt_str))
        else:
            return None

    return ret
