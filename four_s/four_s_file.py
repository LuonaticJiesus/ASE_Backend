import os
import time

from django.http import JsonResponse
from django.utils.crypto import get_random_string
from django.views.decorators.csrf import csrf_exempt
from qcloud_cos import CosConfig, CosS3Client

from BackEnd import global_config

tencent_cos_secret_id = global_config['tencent_cos']['secret_id']
tencent_cos_secret_key = global_config['tencent_cos']['secret_key']
tencent_cos_region = global_config['tencent_cos']['region']
tencent_cos_bucket = global_config['tencent_cos']['bucket']
tencent_cos_config = CosConfig(Region=tencent_cos_region, SecretId=tencent_cos_secret_id,
                               SecretKey=tencent_cos_secret_key, Timeout=5)
tencent_cos_client = CosS3Client(tencent_cos_config, retry=0)

chars = 'abcdefghijklmnopqrstuvwxyz0123456789'


def rand_str():
    ret = str(time.time()).replace('.', '')
    size = 25 - len(ret)
    if size > 0:
        ret = ret + get_random_string(size, chars)
    return ret


@csrf_exempt
def file_upload(request):
    if request.method != 'POST':
        return JsonResponse({'status': -1, 'info': '请求方式错误'})
    try:
        file = request.FILES.get('file', None)
        if file is None:
            return JsonResponse({'status': -1, 'info': '缺少参数'})
        suffix = os.path.splitext(file.name)[-1]
        file_key = rand_str() + suffix
        response = tencent_cos_client.upload_file_from_buffer(
            Bucket=tencent_cos_bucket, Key=file_key, Body=file)
        if response is None:
            return JsonResponse({'status': -1, 'info': '上传失败'})
        file_url = 'https://{}.cos.{}.myqcloud.com/{}'.format(tencent_cos_bucket, tencent_cos_region, file_key)
        return JsonResponse({'status': 0, 'info': '上传成功',
                             'data': {'url': file_url}})
    except Exception as e:
        print(e)
        return JsonResponse({'status': -1, 'info': '操作错误，上传失败'})
