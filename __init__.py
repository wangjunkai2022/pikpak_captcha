import logging
from .captcha_2captcha import (
    captcha_rewardVip as captcha_2captcha_rewardVip,
    get_token_register,
)
from .captcha_slide_img import captcha
from .rapidapi import (
    create_instance_and_pikpak_req,
    create_instance_and_pikpak_rewardVip,
)

logger = logging.getLogger("captcha")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)


def slider_validation(url: str, proxy=None):
    """
    滑块验证
    """
    return captcha(url, proxy)


def google_re_validation(url: str):
    """
    google 注册验证
    """
    try:
        return create_instance_and_pikpak_req(url)
    except Exception as e:
        return get_token_register(url)


def google_rewardVip_validation():
    """
    google vip操作
    """
    try:
        return create_instance_and_pikpak_rewardVip()
    except Exception as e:
        return captcha_2captcha_rewardVip()


if __name__ == "__main__":
    google_re_validation("https://user.mypikpak.com/captcha/v2/txCaptcha.html?action=POST%3A%2Fv1%2Fauth%2Fverification&appName=NONE&appid=XBASE&captcha_token=ck0.5Y2OjdaefRjSKhE_py4yekAozlnY5y_c5NSITuo5phHoaqtRn8I27hPH7zKRrgvraAoJrjgPi8NCPT54kQLO_DyxX7NYdcYebshzp60VoVqp5sxxBw-TzG1Dbhjlpw27fp6azVlrxbrnrwwK2KNRcXyNwzcTFqQnu4haS9nD6gEVb3EPUt13UhP4QIVyqhq2_S5HAebkoG_CVof88LS_-QlYrHMv_woq4wqJvhLpCi2paofs7cqNimop5bkDdvFp4ef2UA79PwFVKxNXh5OXVJe1I07nFcPoplvdWTyoiR1oBUDuIO18HQMCsccsfoCJigeBv5_0O7TSXM7cgASK4ZC_AMDkQdyCTL307SmlEyey6JHxFLAB1PH8f9JMAwF5q34zDmLFEIwadhvmNpzJZR5TH06cQXND_SFfl8dGQJ-5D1SBQWisePGTVjtsK0GmaL1g5SNTFS3p-9DMiNiUq01bYaU38Mdac8FMJKgxVAMrw-IoIC6eU8adrvIU4ghqKAxfXPrRvq8Tmo2s3I7DwkL50ENPVsjYepgkxNEqQL8G-i75sMO6ESgymVllR6Gx.ClgIu6zX2vgyEhBZTnhUOXc3R01kV3ZFT0thGgYxLjU0LjIiE2NvbS5waWtjbG91ZC5waWtwYWsqIGE4YjQyM2JhMTZiZDNmODg4MjZjNmZhNmY2YTUzY2FmEoABZyKiAKc5KqCM5gWW2sKj8lVDQ6F31hlJOiDGrlvh4PAhXlgOlAKt4YIlizyzYYmm30vTW206jkWM3LsP2jYXhfwugChSuOKlzUO35OYDh2zE4-b7xGzY6RCGgyzY2GpZA42LnflL4drCLs_C4RgGkA6vAQMQS_iQp442u-Altiw&clientVersion=NONE&client_id=YNxT9w7GMdWvEOKa&countryCode=HK&creditkey=ck0.5Y2OjdaefRjSKhE_py4yekAozlnY5y_c5NSITuo5phHoaqtRn8I27hPH7zKRrgvraAoJrjgPi8NCPT54kQLO_DyxX7NYdcYebshzp60VoVqp5sxxBw-TzG1Dbhjlpw27fp6azVlrxbrnrwwK2KNRcXyNwzcTFqQnu4haS9nD6gEVb3EPUt13UhP4QIVyqhq2_S5HAebkoG_CVof88LS_-QlYrHMv_woq4wqJvhLpCi2paofs7cqNimop5bkDdvFp4ef2UA79PwFVKxNXh5OXVJe1I07nFcPoplvdWTyoiR1oBUDuIO18HQMCsccsfoCJigeBv5_0O7TSXM7cgASK4ZC_AMDkQdyCTL307SmlEyey6JHxFLAB1PH8f9JMAwF56qIju74d1rAcRgnWiaS6oB5qjIFLaAnEYvFde7U8m9TL5Vrs4DnLk34J0AWKP80oMY3AVNDIGnvqMhR81pWvn8JCrEYJsVzJrTdvgVKzGt0D9U0K_avTCRAx-UgW74O1_mqlVg9jSjKqOlOY_031m_6xCONLS6WGiKHzq0BcH6w.ClgIu6zX2vgyEhBZTnhUOXc3R01kV3ZFT0thGgYxLjU0LjIiE2NvbS5waWtjbG91ZC5waWtwYWsqIGE4YjQyM2JhMTZiZDNmODg4MjZjNmZhNmY2YTUzY2FmEoABZyKiAKc5KqCM5gWW2sKj8lVDQ6F31hlJOiDGrlvh4PAhXlgOlAKt4YIlizyzYYmm30vTW206jkWM3LsP2jYXhfwugChSuOKlzUO35OYDh2zE4-b7xGzY6RCGgyzY2GpZA42LnflL4drCLs_C4RgGkA6vAQMQS_iQp442u-Altiw&credittype=1&device_id=a8b423ba16bd3f88826c6fa6f6a53caf&deviceid=a8b423ba16bd3f88826c6fa6f6a53caf&event=xbase-auth-verification&hl=zh&platformVersion=NONE&privateStyle=&redirect_uri=xlaccsdk01%3A%2F%2Fxbase.cloud%2Fcallback%3Fstate%3Dharbor")