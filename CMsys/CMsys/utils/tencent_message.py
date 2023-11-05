from tencentcloud.common import credential
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.sms.v20190711 import sms_client, models
from CMsys import settings


# 4发送到手机上，使用腾讯云
# 创建应用：SDK AppID：1400659894
# 申请签名：签名id:453703 名称：nwpuzhy公众号
# 申请模板：模板id：1367808 名称：nwpuzhy公众号短信
# 
# 调用接口发送短信
def send_message(phone, code, template_id="1372615"):
    try:
        """
        实例化一个认证对象，传入腾讯云secretID，secretKey
        """
        phone = "{}{}".format("+86", phone)
        cred = credential.Credential(settings.TENCENT_SECRET_ID, settings.SECRET_KEY)
        client = sms_client.SmsClient(cred, settings.TENCENT_CITY)
        req = models.SendSmsRequest()

        """
        基本类型的设置
        """
        req.SmsSdkAppid = settings.TENCENT_APP_ID
        req.Sign = settings.TENCENT_SIGN
        req.PhoneNumberSet = [phone, ]
        req.TemplateID = template_id
        req.TemplateParamSet = [code, ]

        # 通过client对象调用DescribeInstancesResponse方法发起请求
        resp = client.SendSms(req)

        if resp.SendStatusSet[0].Code == "Ok":  # 也可以用fee
            return True

    except TencentCloudSDKException as err:
        # print(err)
        pass
