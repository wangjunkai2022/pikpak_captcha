import importlib
import logging
import os

import requests

from ..utils import domain_get, extract_parameters, remove_parameters
from dotenv import load_dotenv
# 加载.env文件中的环境变量
load_dotenv()

RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
logger = logging.getLogger("rapidapi")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)

sitekey_login = "6LdwHgcqAAAAACSTxyrqqnHNY9-NdSvRD-1A1eap"
sitekey_rewardVip = "6LerFi0pAAAAAB8PSfeUmwtJx6imhQpza2dCjMmG"

class BaseRapidapi():
    api_url = ''
    key_api_params_url = ""
    key_api_params_sitekey = ''
    params = {}

    def pikpak_req(self, url: str = "", sitekey=sitekey_login):
        captcha_type = "recaptcha"
        if "txCaptcha" in url:
            captcha_type = "txCaptcha"

        params_dict = extract_parameters(url)
        url = remove_parameters(url)
        solvev2e_url = self.api_url
        self.params[self.key_api_params_url] = f"{url}"
        self.params[self.key_api_params_sitekey] = f"{sitekey}"
        headers = {
            "x-rapidapi-key": RAPIDAPI_KEY,
            "x-rapidapi-host": domain_get(self.api_url),
        }
        result = requests.get(solvev2e_url, headers=headers, params=self.params)
        logger.debug(f"rapidapi result:\n{result}")
        if result.status_code != 200:
            logger.debug(f"pikpak_req 失败:{result.text}")
            raise Exception("pikpak_req 报错了")
        result_json = result.json()
        if result_json.get("error") and result_json.get("error") != "":
            raise Exception(f"人机验证失败:\n{url}")

        if captcha_type == "txCaptcha":
            return result_json.get("captcha_response")
            # https://user.mypikpak.com/credit/v1/report?deviceid=a8b423ba16bd3f88826c6fa6f6a53caf&captcha_token=ck0.5Y2OjdaefRjSKhE_py4yekAozlnY5y_c5NSITuo5phHoaqtRn8I27hPH7zKRrgvraAoJrjgPi8NCPT54kQLO_DyxX7NYdcYebshzp60VoVqp5sxxBw-TzG1Dbhjlpw27fp6azVlrxbrnrwwK2KNRcXyNwzcTFqQnu4haS9nD6gEVb3EPUt13UhP4QIVyqhq2_S5HAebkoG_CVof88LS_-QlYrHMv_woq4wqJvhLpCi2paofs7cqNimop5bkDdvFp4ef2UA79PwFVKxNXh5OXVJe1I07nFcPoplvdWTyoiR1oBUDuIO18HQMCsccsfoCJigeBv5_0O7TSXM7cgASK4ZC_AMDkQdyCTL307SmlEyey6JHxFLAB1PH8f9JMAwF5q34zDmLFEIwadhvmNpzJZR5TH06cQXND_SFfl8dGQJ-5D1SBQWisePGTVjtsK0GmaL1g5SNTFS3p-9DMiNiUq01bYaU38Mdac8FMJKgxVAMrw-IoIC6eU8adrvIU4ghqKAxfXPrRvq8Tmo2s3I7DwkL50ENPVsjYepgkxNEqQL8G-i75sMO6ESgymVllR6Gx.ClgIu6zX2vgyEhBZTnhUOXc3R01kV3ZFT0thGgYxLjU0LjIiE2NvbS5waWtjbG91ZC5waWtwYWsqIGE4YjQyM2JhMTZiZDNmODg4MjZjNmZhNmY2YTUzY2FmEoABZyKiAKc5KqCM5gWW2sKj8lVDQ6F31hlJOiDGrlvh4PAhXlgOlAKt4YIlizyzYYmm30vTW206jkWM3LsP2jYXhfwugChSuOKlzUO35OYDh2zE4-b7xGzY6RCGgyzY2GpZA42LnflL4drCLs_C4RgGkA6vAQMQS_iQp442u-Altiw&type=txCaptcha&result=0&data=tr0362dRmkyYi3JLYXtDcy4-PyfDUdyvHpU2zBHaNEwOs5GbPfZgoEaiy7Zv5XBWjjMZoLI9FbK3YDQFkSQDTL9y5QN-zaUotoD6B1i2aUFjHWiMC9BCc4i4U4yYcA_9shsS36nOoqxPaYiTOZRGy_mw8w**&rand_str=%40mDW&request_id=9bd0e318-d89f-4478-9cf9-ac7d18f060a8&sign=CMd0DwOyOlfgEqQXuUidtg%3D%3D&rtc_token=23dc:9ca6:6854:d287:406:7902:ddd:1b5
#         https://user.mypikpak.com/credit/v1/report?
# deviceid=a8b423ba16bd3f88826c6fa6f6a53caf&
# captcha_token=ck0.5Y2OjdaefRjSKhE_py4yekAozlnY5y_c5NSITuo5phHoaqtRn8I27hPH7zKRrgvraAoJrjgPi8NCPT54kQLO_DyxX7NYdcYebshzp60VoVqp5sxxBw-TzG1Dbhjlpw27fp6azVlrxbrnrwwK2KNRcXyNwzcTFqQnu4haS9nD6gEVb3EPUt13UhP4QIVyqhq2_S5HAebkoG_CVof88LS_-QlYrHMv_woq4wqJvhLpCi2paofs7cqNimop5bkDdvFp4ef2UA79PwFVKxNXh5OXVJe1I07nFcPoplvdWTyoiR1oBUDuIO18HQMCsccsfoCJigeBv5_0O7TSXM7cgASK4ZC_AMDkQdyCTL307SmlEyey6JHxFLAB1PH8f9JMAwF5q34zDmLFEIwadhvmNpzJZR5TH06cQXND_SFfl8dGQJ-5D1SBQWisePGTVjtsK0GmaL1g5SNTFS3p-9DMiNiUq01bYaU38Mdac8FMJKgxVAMrw-IoIC6eU8adrvIU4ghqKAxfXPrRvq8Tmo2s3I7DwkL50ENPVsjYepgkxNEqQL8G-i75sMO6ESgymVllR6Gx.ClgIu6zX2vgyEhBZTnhUOXc3R01kV3ZFT0thGgYxLjU0LjIiE2NvbS5waWtjbG91ZC5waWtwYWsqIGE4YjQyM2JhMTZiZDNmODg4MjZjNmZhNmY2YTUzY2FmEoABZyKiAKc5KqCM5gWW2sKj8lVDQ6F31hlJOiDGrlvh4PAhXlgOlAKt4YIlizyzYYmm30vTW206jkWM3LsP2jYXhfwugChSuOKlzUO35OYDh2zE4-b7xGzY6RCGgyzY2GpZA42LnflL4drCLs_C4RgGkA6vAQMQS_iQp442u-Altiw&
# type=txCaptcha&
# result=0&
# data=tr0362dRmkyYi3JLYXtDcy4-PyfDUdyvHpU2zBHaNEwOs5GbPfZgoEaiy7Zv5XBWjjMZoLI9FbK3YDQFkSQDTL9y5QN-zaUotoD6B1i2aUFjHWiMC9BCc4i4U4yYcA_9shsS36nOoqxPaYiTOZRGy_mw8w**&
# rand_str=%40mDW&
# request_id=9bd0e318-d89f-4478-9cf9-ac7d18f060a8&
# sign=CMd0DwOyOlfgEqQXuUidtg%3D%3D&
# rtc_token=23dc:9ca6:6854:d287:406:7902:ddd:1b5

        url = "https://user.mypikpak.com/credit/v1/report"
        captcha_token = params_dict.get("captcha_token")
        headers = {
            "authority": "user.mypikpak.com",
            "accept": "application/json, text/plain, */*",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "zh-CN,zh;q=0.9",
            # "cookie": f"captcha_token={captcha_token}"
        }
        params = {
            "deviceid": params_dict["deviceid"],
            'captcha_token': captcha_token,
            'type': captcha_type,
            "result": '0',
            'data': result_json.get("result")

        }

        response = requests.get(url, headers=headers, params=params,)
        res_js_data = response.json()
        # if res_js_data.get("error") != "":
        #     logger.error(res_js_data.get("error"))
        captcha_token = res_js_data.get("captcha_token")
        logger.info(f"自动获得到的token:{captcha_token}")
        return captcha_token

    def pikpak_rewardVip(self, sitekey: str = sitekey_rewardVip):
        url = "https://user.mypikpak.com"
        solvev2e_url = self.api_url
        self.params[self.key_api_params_url] = f"{url}"
        self.params[self.key_api_params_sitekey] = f"{sitekey}"
        headers = {
            "x-rapidapi-key": RAPIDAPI_KEY,
            "x-rapidapi-host": domain_get(self.api_url),
        }
        result = requests.get( solvev2e_url, headers=headers, params=self.params)
        if result.status_code != 200:
            logger.error(f"captcha_rewardVip 失败:{result.text}")
            raise Exception("pikpak_rewardVip 报错了")
        logger.info(result)
        result_json = result.json()
        return result_json.get("result")


# 定义要创建的类名集合
class_names = {
    "Captcha2": ".2captcha",
    "CaptchaKiller": ".captcha_killer",
    'Capsolver': '.capsolver',
}


def _getInstanceClass(class_name) -> BaseRapidapi:
    module_name = class_names.get(class_name)
    if module_name:
        # 动态导入模块
        module = importlib.import_module(module_name, package=__package__)
        # 获取类对象
        cls = getattr(module, class_name)
        # 创建实例
        instance: BaseRapidapi = cls()
        return instance
    else:
        logger.debug(f"Class {class_name} not found.")


def create_instance_and_pikpak_req(url):
    # 遍历集合并创建实例
    for name in class_names.keys():
        instance = _getInstanceClass(name)
        try:
            return instance.pikpak_req(url)
        except Exception as e:
            logger.debug(f"google 注册验证 当前验证模块失败:{name}\nException:{e}")
    raise Exception("都没成功验证")


def create_instance_and_pikpak_rewardVip():
    # 遍历集合并创建实例
    for name in class_names.keys():
        instance = _getInstanceClass(name)
        try:
            return instance.pikpak_rewardVip()
        except Exception as e:
            logger.debug(f"google 获取vip 当前验证模块失败:{name}\nException:{e}")
    raise Exception("都没成功验证")
