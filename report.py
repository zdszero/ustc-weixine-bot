import json
import requests
from bs4 import BeautifulSoup
import re
import time


class Reporter(object):
    def __init__(self, id: str, password: str):
        self.id = id
        self.password = password

    def report(self) -> bool:
        # login
        login_success = False
        try_count = 5
        form = None
        session = None
        while not login_success and try_count > 0:
            test_url = 'https://weixine.ustc.edu.cn/2020/login'
            session = self.login()
            form = session.get(test_url)
            # when logined, the form.url should be 'https://weixine.ustc.edu.cn/2020/daliy_report'
            if form.url == test_url:
                print('Login failed ...')
            else:
                print('Login succeed!')
                login_success = True
            try_count -= 1
        if not login_success or not form or not session:
            print('Failed to login')
            return False
        # return is report is done today
        soup = BeautifulSoup(form.text, 'html.parser')
        last_report_time = soup.find(
            'span', {'class': 'text-warning'}).next_sibling
        last_date = re.search(r'\d+-\d+-\d+', last_report_time).group(0)
        if time.strftime('%Y-%m-%d') == last_date:
            print('The report has been done today')
            return True
        # report
        token = soup.find('input', {'name': '_token'})['value']
        with open('./data.json', 'r') as data_fp:
            report_data = json.load(data_fp)
            report_data['_token'] = token
        report_url = 'https://weixine.ustc.edu.cn/2020/daliy_report'
        res = session.post(url=report_url, data=report_data)
        if res.status_code != 200:
            print('Error: report error')
            return False
        print('You have reported successfully')
        return True

    def login(self) -> requests.Session:
        login_url = 'https://passport.ustc.edu.cn/login?service=https%3A%2F%2Fweixine.ustc.edu.cn%2F2020%2Fcaslogin'
        session = requests.session()
        tmpform = session.get(login_url)
        soup = BeautifulSoup(tmpform.text, 'html.parser')
        cas_lt = soup.find('input', {'id': 'CAS_LT'})['value']
        login_data = {
            'model': 'uplogin.jsp',
            'CAS_LT': cas_lt,
            'service': 'https://weixine.ustc.edu.cn/2020/caslogin',
            'warn': '',
            'showCode': '',
            'username': self.id,
            'password': self.password,
            'button': ''
        }
        session.post(url=login_url, data=login_data)
        print('Login ...')
        return session


def main():
    with open('./user.json', 'r') as user_fp:
        user_data = json.load(user_fp)
        id = user_data['id']
        password = user_data['password']
        r = Reporter(id, password)
        r.report()


if __name__ == '__main__':
    main()
