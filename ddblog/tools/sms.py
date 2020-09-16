import hashlib
import datetime
import base64
import json

import requests

class YunTongXin():
    base_url = 'https://app.cloopen.com:8883'

    def __init__(self, accountSid, accountToken, appId, templateId):
        #开发者主账户
        self.accountSid = accountSid
        #账户授权令牌
        self.accountToken = accountToken
        #应用id
        self.appId = appId
        #模板id
        self.templateId = templateId

    #生成请求url
    def get_request_url(self, sig):
        self.url = self.base_url + '/2013-12-26/Accounts/%s/SMS/TemplateSMS?sig=%s'%(self.accountSid, sig)
        return self.url

    #生成签名
    def get_sig(self, timestamp):
        #MD5加密（账户Id + 账户授权令牌 + 时间戳）
        s = self.accountSid+self.accountToken+timestamp
        md5 = hashlib.md5()
        md5.update(s.encode())
        return md5.hexdigest().upper()

    def get_timestamp(self):
        #"yyyyMMddHHmmss"
        return datetime.datetime.now().strftime('%Y%m%d%H%M%S')

    #生成请求头
    def get_request_header(self, timestamp):
        #使用Base64编码（账户Id + 冒号 + 时间戳）
        s = self.accountSid+':'+timestamp
        auth = base64.b64encode(s.encode()).decode()
        return {
            'Accept':'application/json',
            'Content-Type':'application/json;charset=utf-8',
            'Authorization': auth
        }

    #生成请求体
    def get_request_body(self, phone, code):

        return {

            "to": phone,
            "appId": self.appId,
            "templateId": self.templateId,
            "datas": [code, "3"]
        }

    #发请求
    def send_request(self, url, header, body):
        res = requests.post(url, headers=header, data=body)
        return res.text

    def run(self, phone, code):
        #获取时间戳
        timestamp = self.get_timestamp()
        #生成签名
        sig = self.get_sig(timestamp)
        #生成url
        url = self.get_request_url(sig)
        print(url)
        #生成请求头
        header = self.get_request_header(timestamp)
        print(header)
        body = self.get_request_body(phone, code)
        print(body)
        data = self.send_request(url, header, json.dumps(body))
        return data

if __name__ == '__main__':

    config = {
        "accountSid":"8aaf07086c6b60c5016c89a354f10f95",
        "accountToken": "6fa62f2ff4d04fe7b11655dfcae54968",
        "appId": "8aaf07086c6b60c5016c89a355410f9b",
        "templateId": "1"
    }
    yun = YunTongXin(**config)
    res = yun.run('18610694548', '881227')
    #{"statusCode":"000000","templateSMS":{"smsMessageSid":"82b36abdab1c4ea5a80c07d8b9081fe8","dateCreated":"20200729155003"}}
    print(res)







