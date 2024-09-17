import base64
import hashlib
import json
import logging
import os
import random
import re
import time

import requests

from .ai.yolov8_test import ai_test_byte
from .captcha_js2py import get_d, img_jj
from .utils import delete_img, extract_parameters, image_run, remove_parameters, save_requests_img


logger = logging.getLogger("slide_img")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)

proxy = None


def captcha2(url: str = ""):
    logger.info('滑块验证中!!!')
    logger.debug(f'url:{url}')
    params_dict = extract_parameters(url)
    device_id = params_dict.get("device_id")
    captcha_token = params_dict.get('captcha_token')
    url = f"https://user.mypikpak.com/credit/v1/report?deviceid={
        device_id}&captcha_token={captcha_token}&type=pzzlSlider&result=0"
    response2 = requests.get(url, proxies=proxy)
    response_data = response2.json()
    logger.debug(json.dumps(response_data, indent=4))
    return response_data.get("captcha_token")


def captcha(url: str = ""):
    captcha_url = url
    logger.info('滑块验证中!!!')
    logger.debug(f'url:{url}')
    params_dict = extract_parameters(url)
    # url = remove_parameters(url)
    url = "https://user.mypikpak.com/pzzl/gen"
    device_id = params_dict.get("device_id")
    captcha_token = params_dict.get('captcha_token')
    params = {
        "deviceid": device_id,
        "traceid": ""
    }
    response = requests.get(url, params=params, proxies=proxy,)
    imgs_json = response.json()
    frames = imgs_json["frames"]
    pid = imgs_json['pid']
    traceid = imgs_json['traceid']
    logger.info('滑块ID:')
    logger.debug(json.dumps(pid, indent=4))
    params = {
        'deviceid': device_id,
        'pid': pid,
        'traceid': traceid
    }
    url = "https://user.mypikpak.com/pzzl/image"
    response1 = requests.get(url, params=params, proxies=proxy,)
    img_data = response1.content
    tmp_root_path = os.path.dirname(os.path.abspath(__file__))
    tmp_root_path = os.path.join(tmp_root_path, "slide_img_temp")
    one_img = os.path.join(tmp_root_path, "1.png")
    save_requests_img(img_data, one_img)
    # 保存拼图图片
    image_run(one_img, frames)
    # 识别图片
    select_id = None
    for file in os.listdir(tmp_root_path):
        with open(f"{tmp_root_path}/{file}", 'rb') as f:
            image_bytes = f.read()
            if ai_test_byte(image_bytes) == "ok":
                select_id = file.split(".")[0]
                break
    # 删除缓存图片
    delete_img(one_img)
    if not select_id:
        logger.info("ai识别图片失败 重新验证")
        return captcha(captcha_url)
    json_data = img_jj(frames, int(select_id), pid)
    f = json_data['f']
    npac = json_data['ca']
    params = {
        'pid': pid,
        'deviceid': device_id,
        'traceid': traceid,
        'f': f,
        'n': npac[0],
        'p': npac[1],
        'a': npac[2],
        'c': npac[3],
        'd': get_d(pid + device_id + str(f)),
    }
    url = f"https://user.mypikpak.com/pzzl/verify"
    response1 = requests.get(url, params=params, proxies=proxy)
    response_data = response1.json()
    if response_data['result'] == 'accept':
        logger.info('验证通过!!!')
        sign, request_id = getResults(captcha_token)
        url = f"https://user.mypikpak.com/credit/v1/report"
        params = {
            'deviceid': device_id,
            'captcha_token': captcha_token,
            'type': 'pzzlSlider',
            'result': "0",
            'data': pid,
            'traceid': traceid,
            'request_id': request_id,
            'sign': sign,
            # 'rtc_token': '',
        }
        response2 = requests.get(url, params=params, proxies=proxy)
        response_data = response2.json()
        # logger.info('获取验证TOKEN:')
        logger.debug(json.dumps(response_data, indent=4))
        save_frames(frames, int(select_id))
        return response_data.get("captcha_token")
    else:
        return ""


def getResults(captcha_str: str = ""):
    # 获取当前时间戳（毫秒）
    current_timestamp_seconds = time.time()
    current_timestamp_milliseconds = int(current_timestamp_seconds * 1000)

    # 随机生成0到999之间的整数
    random_suffix = random.randint(0, 999)

    # 将随机数格式化为三位数，不足的前面补零
    random_suffix_str = f"{random_suffix:03}"

    # 替换时间戳的后三位
    final_timestamp = str(current_timestamp_milliseconds)[
        :-3] + random_suffix_str
    url = f'https://api-drive.mypikpak.com/captcha-jsonp/v2/executor?callback=handleJsonpResult_{
        final_timestamp}'
    params = {
        'callback': f'handleJsonpResult_{final_timestamp}',
    }
    response = requests.get(url, params=params, proxies=proxy)
    handleJsonpResult = response.text
    # 正则表达式匹配
    uuid_pattern = r'\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b'
    uuid_pattern_and_word = r'\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}hello_world\b'
    match_uuid = re.findall(uuid_pattern, handleJsonpResult)
    match_uuid_word = re.findall(uuid_pattern_and_word, handleJsonpResult)
    match_for_str = re.search(r'for\(.*\+\)', handleJsonpResult).group()
    match_for_count = int(re.search(r'i<.*;', match_for_str).group()[2:-1], 16)

    uuid_result = match_uuid[0]
    uuid_word_str = match_uuid_word[0]
    uuid_word_str_notword = uuid_word_str[:-len("hello_world")][-12:]
    for uuid_str in match_uuid:
        if uuid_word_str_notword in uuid_str:
            print(f'这个是uuid-word 相识\n{uuid_str}')
            uuid_word_str_notword = uuid_str
        else:
            uuid_result = uuid_str

    hashResult = uuid_word_str + captcha_str + uuid_word_str_notword
    if "sha256" in handleJsonpResult:
        for count in range(match_for_count):
            hashResult = sha256_to_base64(hashResult)
    elif "md5" in handleJsonpResult:
        for count in range(match_for_count):
            hashResult = md5_to_base64(hashResult)
    elif "sha1" in handleJsonpResult:
        for count in range(match_for_count):
            hashResult = sha1_to_base64(hashResult)

    return hashResult, uuid_result


def md5_to_base64(string):
    # 计算 MD5 哈希值
    # 使用 digest() 获取字节形式的哈希值
    md5_hash = hashlib.md5(string.encode('utf-8')).digest()

    # 转换为 Base64 编码
    base64_encoded = base64.b64encode(md5_hash)

    return base64_encoded.decode('utf-8')  # 将字节编码转换为字符串


def sha1_to_base64(string):
    # 计算 SHA-1 哈希值
    sha1_hash = hashlib.sha1(string.encode(
        'utf-8')).digest()  # 使用 digest() 获取字节形式的哈希值

    # 转换为 Base64 编码
    base64_encoded = base64.b64encode(sha1_hash)

    return base64_encoded.decode('utf-8')  # 将字节编码转换为字符串


def sha256_to_base64(string):
    # 计算 SHA-256 哈希值
    sha256_hash = hashlib.sha256(string.encode(
        'utf-8')).digest()  # 使用 digest() 获取字节形式的哈希值

    # 转换为 Base64 编码
    base64_encoded = base64.b64encode(sha256_hash)

    return base64_encoded.decode('utf-8')  # 将字节编码转换为字符串


cache_json_file = os.path.abspath(__file__)[:-3] + "Temp" + ".json"


def save_frames(frames, ok_index):
    try:
        with open(cache_json_file, mode="r", encoding="utf-8") as file:
            json_str = file.read()
            json_data = json.loads(json_str)
    except:
        json_data = []

    json_data.append({
        "frames": frames,
        'index': ok_index,
    })
    with open(cache_json_file, mode='w', encoding="utf-8") as file:
        file.write(json.dumps(json_data, indent=4, ensure_ascii=False))


if __name__ == "__main__":
    # temp_url = "https://user.mypikpak.com/captcha/v2/spritePuzzle.html?action=POST%3A%2Fv1%2Fauth%2Fsignin&appName=NONE&appid=XBASE&captcha_token=ck0.Qw-6MZu4AFID9FGWJhMEqeQxWCjq7EzgkXyAAGNtoYZMv2UlkFSxjJETtWwrW--DSNCs6AYPvhDmN7v85e0uh8aFJEp1ErnZmVInRnEi_rrqprTSfeFJsWuVu59lJElBDM3_RRdpkCdzKVd10vnz_RPa5kb_oJB2xACcpj1Ig1S4yD4Xa52m0Jm3OyRSPxwmw6nBHE63DgObQ3VEfD_XQyF7aHz3phaCRoItnO5ONQTKSKGGCGm5e15Zbtx4E0iHM31CDclY4jvCSCaZvUcOVXQkAK-aZaJW6PriN1CEM-CwqWmDxZ-o4mj-MIKucp6r5jSPAWj14LFPGqDGQ-buxsKRo2BRiwtfMq7V48xvxZU&clientVersion=NONE&client_id=YNxT9w7GMdWvEOKa&creditkey=ck0.Qw-6MZu4AFID9FGWJhMEqeQxWCjq7EzgkXyAAGNtoYZMv2UlkFSxjJETtWwrW--DSNCs6AYPvhDmN7v85e0uh8aFJEp1ErnZmVInRnEi_rrqprTSfeFJsWuVu59lJElBDM3_RRdpkCdzKVd10vnz_RPa5kb_oJB2xACcpj1Ig1S4yD4Xa52m0Jm3OyRSPxwmw6nBHE63DgObQ3VEfD_XQyF7aHz3phaCRoItnO5ONQTKSKGGCGm5e15Zbtx4E0iHM31CDclY4jvCSCaZvUcOVXQkAK-aZaJW6PriN1CEM-CwqWmDxZ-o4mj-MIKucp6rnGFSsvNYwEQ2APaLgKYtUQ&credittype=1&device_id=d1b59f081c21134db020c18dbaa3d3d9&deviceid=d1b59f081c21134db020c18dbaa3d3d9&event=signin_check&platformVersion=NONE&privateStyle=&redirect_uri=xlaccsdk01%3A%2F%2Fxbase.cloud%2Fcallback%3Fstate%3Dharbor&traceid="  # 请替换为实际的网页地址
    # # temp_url = "https://user.mypikpak.com/captcha/v2/reCaptcha.html?action=POST%3A%2Fv1%2Fauth%2Fverification&appName=NONE&appid=XBASE&captcha_token=ck0.7GJjmxpAYMz3p7o-XaRoCL24PAmVtaYQw8aW53X5zpPEFutBJ-EdUQjn1yPfZR8SLTlgbYZH9W6kjDxrklaRpiPfm-0ghQKwgC-EWCFxfMaHU0YuNiIbD7wSPSL8ZxYckdmcLl6YCQOoAePUFGqKu5VqX2FDUADF_k_3lCdf6HuWumzcilO6T7ZkpJ8Nb0cOhchDmTpUInQ6KfYiT_1Bh6To_L52TY-oQUXVysW_XafqggzLPSaeVgbcFapeTByfcCYJkKerv-5nhu7i1z6KKdiajnuQdbEFpsQDnJqsAjFvVrPJIRkobkX_fq1Jj8qMlLL-KSQCxvGFtql1DUPDqt7Q1U4IuBNLrqXPKwlDmvHlquFvb7o8Kf9wNYeBF8Jj7vWO_jfzVMHw_H3RM3E6iu9R7Skibdvl3GmNv3hbk02y9rYAYXzIsJvjFNH2iJA0cXXdl28dtfuWAb-D-Xg3bP7IAP9fPb6Xta1sqAM5br2KI0_YlzZS0bXl7oFQHbKZxoMGQKpT-QPtai_hnSoi8HsVTCTQ_GJt5EeXr3kLItA.ClgIseq_8Y0yEhBZTnhUOXc3R01kV3ZFT0thGgYxLjQyLjgiE2NvbS5waWtjbG91ZC5waWtwYWsqIDhiYWQ3OWQ0NWFkZGI3YjRlMzkyZjY2M2MzYTA1NDY3EoABeX6oIi9giuXRWMvTtebZLThVIOj_mNZ8AxyMRvobiC9k2xoEnWG-_u_oC2t-5wN7MjEZsSrDArTwEVmjH7hqIKm7RvSxVBGox0crshw39G53zm7onc7INFr2wM_V3ezereCqIa4tLAvdJYsIu-Pi9SbRd0IkBNt3D09vXORU_5c&clientVersion=NONE&client_id=YNxT9w7GMdWvEOKa&creditkey=ck0.7GJjmxpAYMz3p7o-XaRoCL24PAmVtaYQw8aW53X5zpPEFutBJ-EdUQjn1yPfZR8SLTlgbYZH9W6kjDxrklaRpiPfm-0ghQKwgC-EWCFxfMZXiDHj2_zheD9GWz5CsaR6xSNMCbl_CHhcWfUdZr3zXG3H5qMwJBLIE4TTw7P4dy54ljpsLDo7s5ecOjS3AZeDHL2e-9rUy74z5HzQ9mHyyjz8lY3hW0voyMjT8tavTLgB7ZAxKmBMi6pXQBynLUZFRlpPLmlF18L6_4Rvuv72n5SVrvith5YTibNGEduK0biN8HUQtrlnEJdyInbMLX2od1zJbJYTLp7reMWsgaG27zRow-mxhRPl8P72vKIf1MMDP5iLb_XtmeEHV3uoPwzeyhi0znC1j_xytF5IaCWDAI3X9eP-xOGxMKAhvy_RjRo_yKCk3-nxVb-La7j19adCVhob1qO4e7EFX-9rYlsks0pimz64RvPi-J1ryapaVDu9FTraiBI6vXSeZfHU9eZu.ClgIseq_8Y0yEhBZTnhUOXc3R01kV3ZFT0thGgYxLjQyLjgiE2NvbS5waWtjbG91ZC5waWtwYWsqIDhiYWQ3OWQ0NWFkZGI3YjRlMzkyZjY2M2MzYTA1NDY3EoABeX6oIi9giuXRWMvTtebZLThVIOj_mNZ8AxyMRvobiC9k2xoEnWG-_u_oC2t-5wN7MjEZsSrDArTwEVmjH7hqIKm7RvSxVBGox0crshw39G53zm7onc7INFr2wM_V3ezereCqIa4tLAvdJYsIu-Pi9SbRd0IkBNt3D09vXORU_5c&credittype=1&device_id=8bad79d45addb7b4e392f663c3a05467&deviceid=8bad79d45addb7b4e392f663c3a05467&event=xbase-auth-verification&hl=zh&mainHost=user.mypikpak.com&platformVersion=NONE&privateStyle=&redirect_uri=xlaccsdk01%3A%2F%2Fxbase.cloud%2Fcallback%3Fstate%3Dharbor"
    # # # temp_url = "https://www.google.com/"
    # # get_token_register(temp_url)
    # # captcha_rewardVip()
    # captcha(temp_url)
    # # response = requests.get("http://localhost:7690/api/login", params={
    # #     "url": temp_url
    # # })
    # # json_data = response.json()
    # # print(response)

    getResults("test")
