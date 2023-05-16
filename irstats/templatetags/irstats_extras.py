from django import template
from django.utils.safestring import mark_safe
import logging



from datetime import timedelta
import json

register = template.Library()
logger = logging.getLogger("irstats_extras.py")

@register.filter
def convertTime(raw_data):
    if raw_data and raw_data > 0:
        iTime_seconds = raw_data // 10000
        iTime_decimal = raw_data - (iTime_seconds * 10000)
        tDelta_str = str(timedelta(seconds=iTime_seconds)).split(":")
        formattedString = "%s:%s:%s" % (tDelta_str[1], tDelta_str[2], str(iTime_decimal).zfill(4))
        return formattedString
    return "-"

@register.filter
def returnBool(raw_data):
    if raw_data:
        return mark_safe("<i class='bi bi-check-lg'></i></td>")
    return mark_safe("")

@register.filter
def getCleanedList(raw_data):
    try:
        raw_list = json.loads(raw_data.replace('\'', '"'))
        return ', '.join(raw_list)
    except json.JSONDecodeError as e:
        logger.warning("Get Cleaned List Deconding JSON Error" + str(e))
        logger.warning(str(raw_data))
        return "Decode Error"
    return ""

@register.simple_tag
def getBannerImage(asset_dict, key):
    try:
        temp = asset_dict.get(str(key))
        return "https://images-static.iracing.com" + temp.get("folder") + "/" + temp.get("large_image")
    except AttributeError as e:
        logger.info("Get Banner Image AttributeError for " + str(key))
    except TypeError as e:
        logger.info("Get Banner Image TypeError for " + str(e))
    return None

@register.simple_tag
def getSeriesImage(asset_dict, key):
    try:
        temp = asset_dict.get(str(key))
        return "https://images-static.iracing.com/img/logos/series/" + temp.get("logo")
    except AttributeError as e:
        logger.info("Get Series Image Attribute Error for " + str(key))
    except TypeError as e:
        logger.info("Get Series Image TypeError for " + str(e))
    return None

@register.simple_tag
def calculateAverage(average, count):
    try:
        real_average = int(average/count)
        return real_average
    except ZeroDivisionError as e:
        return "-"
    except ValueError as e:
        return "-"

@register.simple_tag
def calculateAverageTime(average, count):
    try:
        real_average = int(average/count)
        return convertTime(real_average)
    except ZeroDivisionError as e:
        return "-"
    except ValueError as e:
        return "-"
