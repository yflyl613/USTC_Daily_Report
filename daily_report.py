import requests
import json
import re
import urllib3
import argparse
import logging
import sys
import muggle_ocr

root = logging.getLogger()
root.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter("[%(levelname)s %(asctime)s] %(message)s")
handler.setFormatter(formatter)
root.addHandler(handler)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

address_dict = {
    '内地': 1,
    '香港': 2,
    '澳门': 4,
    '台湾': 5,
    '国外': 3
}

inschool_dict = {
    '东区': 2,
    '南区': 3,
    '中区': 4,
    '北区': 5,
    '西区': 6,
    '先研院': 7,
    '国金院': 8,
    '其他校区': 9,
    '校外': 0
}

status_dict = {
    '正常在校园内': 1,
    '正常在家': 2,
    '居家留观': 3,
    '集中留观': 4,
    '住院治疗': 5,
    '其他': 6
}

with open('province.json', 'r') as f:
    province_dict = json.load(f)

with open('city.json', 'r') as f:
    city_dict = json.load(f)

with open('district.json', 'r') as f:
    district_dict = json.load(f)

class Report(object):
    def __init__(self, args, config):
        self.args = args
        self.config = config
        self.sdk = muggle_ocr.SDK(model_type=muggle_ocr.ModelType.OCR)

        self.login()
        self.send_report()

    def login(self):
        self.session = requests.session()

        url = 'https://passport.ustc.edu.cn/login?service=https%3A%2F%2Fweixine.ustc.edu.cn%2F2020%2Fcaslogin'
        response = self.session.get(url)
        assert response.status_code == 200
        cookie = response.cookies
        CAS_LT_catcher = r'name="CAS_LT" value="LT-[A-Za-z0-9]+"'
        CAS_LT = re.findall(CAS_LT_catcher, response.text)
        assert(len(CAS_LT) > 0)
        CAS_LT = CAS_LT[0].split('=')[-1].strip('"')

        url = 'https://passport.ustc.edu.cn/validatecode.jsp?type=login'
        headers = {
            'Cookie': f"lang=zh; JSESSIONID={cookie['JSESSIONID']}"
        }
        response = self.session.get(url, headers=headers)
        assert response.status_code == 200

        data = {
            'model': 'uplogin.jsp',
            'CAS_LT': CAS_LT,
            'LT': self.sdk.predict(image_bytes=response.content),
            'service': 'https://weixine.ustc.edu.cn/2020/caslogin',
            'warn': '',
            'showCode': 1,
            'username': self.args.username,
            'password': self.args.password,
            'button': ''
        }
        headers = {
            'Cookie': f"JSESSIONID={cookie['JSESSIONID']}"
        }
        url = 'https://passport.ustc.edu.cn/login'
        response = self.session.post(url, data=data, headers=headers, verify=False)
        assert response.status_code == 200
        self.cookie = response.cookies

        url = 'https://weixine.ustc.edu.cn/2020/home'
        headers = {
            'Cookie':  f"XSRF-TOKEN={self.cookie['XSRF-TOKEN']}; laravel_session={self.cookie['laravel_session']}"
        }
        response = self.session.get(url, headers=headers)
        token_catcher = r'name="_token" value="[A-Za-z0-9]+"'
        _token = re.findall(token_catcher, response.text)
        assert(len(_token) > 0)
        _token = _token[0].split('=')[-1].strip('"')
        self._token = _token
        logging.info('Login successful')

    def send_report(self):
        url = 'https://weixine.ustc.edu.cn/2020/daliy_report'
        data = {
            '_token': self._token,
            'now_address': self.config['now_address'],
            'gps_now_address': '',
            'now_province': self.config['now_province'],
            'gps_province': '',
            'now_city': self.config['now_city'],
            'gps_city': '',
            'now_country': self.config['now_country'],
            'gps_country': '',
            'now_detail': '',
            'is_inschool': self.config['is_inschool'],
            'body_condition': 1,
            'body_condition_detail': '',
            'now_status': self.config['now_status'],
            'now_status_detail': '',
            'has_fever': 0,
            'last_touch_sars': 0,
            'last_touch_sars_date': '',
            'last_touch_sars_detail': '',
            'is_danger': 0,
            'is_goto_danger': 0,
            'jinji_lxr': self.args.contact_name,
            'jinji_guanxi': self.args.contact_relation,
            'jiji_mobile': self.args.contact_phone,
            'other_detail': ''
        }
        headers = {
            'Cookie': f"XSRF-TOKEN={self.cookie['XSRF-TOKEN']}; laravel_session={self.cookie['laravel_session']}"
        }
        response = self.session.post(url, data, headers=headers, verify=False)
        assert response.status_code == 200
        logging.info('The daily report has been sent')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--username", type=str)
    parser.add_argument("--password", type=str)
    parser.add_argument("--contact_name", type=str)
    parser.add_argument("--contact_phone", type=str)
    parser.add_argument("--contact_relation", type=str)
    args = parser.parse_args()

    with open('config.json', 'r') as f:
        config = json.load(f)
    processed_config = {
        'now_address': address_dict[config['当前所在地']],
        'now_province': province_dict[config['省']],
        'now_city': city_dict[config['省']][config['市']],
        'now_country': district_dict[config['省']][config['市']].get(config['区'], ''),
        'is_inschool': inschool_dict[config['校区']],
        'now_status': status_dict[config['当前状态']]
    }
    Report(args, processed_config)

