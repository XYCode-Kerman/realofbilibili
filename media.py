import random
import requests
import math
import time
import pymongo
import decimal

mongodb = pymongo.MongoClient('127.0.0.1', 27017)
bilibili = mongodb.get_database('bilibili')

media_name = '三体'
media_id = '4315402'
cookie = 'cookie in http header'
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36'

session = requests.session()


def get_short_all():
    data = []
    raw = bilibili.get_collection('raw')

    print(
        '删除了',
        raw.delete_many({
            'media_id': media_id
        }).deleted_count,
        '份文档'
    )

    first = session.get(f'https://api.bilibili.com/pgc/review/short/list?media_id={media_id}&ps=30&sort=0', headers={
                        'Cookie': cookie, 'User-Agent': user_agent}).json()
    next = first['data']['next']
    total = first['data']['total']
    total_page = math.ceil(total / 30)

    # Get all
    page = 0
    while total_page >= page:
        this_page = session.get(f'https://api.bilibili.com/pgc/review/short/list?media_id={media_id}&ps=30&sort=0&cursor={next}', headers={
                                'Cookie': cookie, 'User-Agent': user_agent}).json()
        next = this_page['data']['next']

        for comment in this_page['data']['list']:
            comment['media_name'] = media_name
            comment['media_id'] = media_id

            data.append(comment)
            raw.insert_one(comment)

        page += 1

        if page % 10 == 0:
            print(f'Page: {page} / {total_page}')

            time.sleep(random.randint(0, 3))

    return data


def real_score():
    raw = bilibili.get_collection('raw')

    data = [
        x['score']
        for x in raw.find({'media_id': media_id}, {'score': 1})
    ]

    sum = decimal.Decimal(0)
    for score in data:
        sum += decimal.Decimal(score)

    real = sum / decimal.Decimal(data.__len__())

    print(f'{media_name} 的评分是：{real}')

    # print(str(real).split('.')[1].__len__())


if '__main__' == __name__:
    print('1. 获取数据')
    print('2. 得出真实评分')
    print('3. 上面两者都')

    select = input('输入选项前的序号（不包含小数点）：')
    media_name = input('请输入番名（允许自定义）：')
    media_id = input('请输入番ID（获取方式见README）：')

    if select == '1':
        get_short_all()
    elif select == '2':
        real_score()
    else:
        get_short_all()
        real_score()
