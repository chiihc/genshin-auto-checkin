# settings
import logging
import json
import requests
import os

from requests.exceptions import HTTPError

__all__ = ['log', 'CONFIG', 'req']

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%Y-%m-%dT%H:%M:%S')


log = logger = logging


class _Config:
    GIH_VERSION = ''
    WBH_VERSION = '1.0.1'
    ACT_ID = 'e202009291139501'
    APP_VERSION = '2.3.0'
    REFERER_URL = 'https://webstatic.mihoyo.com/bbs/event/signin-ys/index.html?' \
                  'bbs_auth_required={}&act_id={}&utm_source={}&utm_medium={}&' \
                  'utm_campaign={}'.format('true', ACT_ID, 'bbs', 'mys', 'icon')
    AWARD_URL = 'https://api-takumi.mihoyo.com/event/bbs_sign_reward/home?act_id={}'.format(ACT_ID)
    ROLE_URL = 'https://api-takumi.mihoyo.com/binding/api/getUserGameRolesByCookie?game_biz={}'.format('hk4e_cn')
    INFO_URL = 'https://api-takumi.mihoyo.com/event/bbs_sign_reward/info?region={}&act_id={}&uid={}'
    SIGN_URL = 'https://api-takumi.mihoyo.com/event/bbs_sign_reward/sign'
    USER_AGENT = 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) ' \
                 'miHoYoBBS/{}'.format(APP_VERSION)
    # weibo
    CONTAINER_ID = '100808fc439dedbb06ca5fd858848e521b8716'
    SUPER_URL = 'https://m.weibo.cn/api/container/getIndex?containerid={}'.format('100803_-_page_my_follow_super')
    YS_URL = 'https://m.weibo.cn/api/container/getIndex?containerid={}_-_feed'.format(CONTAINER_ID)
    KA_URL = 'https://ka.sina.com.cn/innerapi/draw'
    BOX_URL = 'https://ka.sina.com.cn/html5/mybox'
    WB_USER_AGENT = 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E150'


class ProductionConfig(_Config):
    LOG_LEVEL = logging.INFO


class DevelopmentConfig(_Config):
    LOG_LEVEL = logging.DEBUG


class HttpRequest(object):
    @staticmethod
    def to_python(json_str: str):
        return json.loads(json_str)

    @staticmethod
    def to_json(obj):
        return json.dumps(obj, indent=4, ensure_ascii=False)

    def request(self, method, url, max_retry: int = 2,
            params=None, data=None, json=None, headers=None, **kwargs):
        for i in range(max_retry + 1):
            try:
                s = requests.Session()
                response = s.request(method, url, params=params,
                    data=data, json=json, headers=headers, **kwargs)
            except HTTPError as e:
                log.error(f'HTTP error:\n{e}')
                log.error(f'The NO.{i + 1} request failed, retrying...')
            except KeyError as e:
                log.error(f'Wrong response:\n{e}')
                log.error(f'The NO.{i + 1} request failed, retrying...')
            except Exception as e:
                log.error(f'Unknown error:\n{e}')
                log.error(f'The NO.{i + 1} request failed, retrying...')
            else:
                return response

        raise Exception(f'All {max_retry + 1} HTTP requests failed, die.')


req = HttpRequest()

RUN_ENV = os.environ.get('RUN_ENV', 'dev')
if RUN_ENV == 'dev':
    CONFIG = DevelopmentConfig()
else:
    CONFIG = ProductionConfig()

log.basicConfig(level=CONFIG.LOG_LEVEL)


MESSAGE_TEMPLATE = '''
    {today:#^28}
    🔅[{region_name}]{uid}
    今日奖励: {award_name} × {award_cnt}
    本月累签: {total_sign_day} 天
    签到结果: {status}
    {end:#^28}'''

CONFIG.MESSAGE_TEMPLATE = MESSAGE_TEMPLATE

