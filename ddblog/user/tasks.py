from ddblog.celery import app
from django.conf import settings
from tools.sms import YunTongXin

@app.task
def send_sms_c(phone, code):

    config = {
        "accountSid": settings.SMS_ACCOUNT_ID,
        "accountToken": settings.SMS_ACCOUNT_TOKEN,
        "appId": settings.SMS_APP_ID,
        "templateId": settings.SMS_TEMPLATE_ID
    }
    yun = YunTongXin(**config)
    res = yun.run(phone, code)



