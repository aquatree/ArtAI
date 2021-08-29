import json
import os
import re
import requests
import pandas as pd

from bs4 import BeautifulSoup as bs


def _get_bs(link):
    """
    BeautifulSoupオブジェクトを作成する。
    """
    html = requests.get(link)
    return bs(html.content, 'lxml')


def _get_tag(bs, tag, **kwargs):
    """
    指定したtagの内容をすべて取得する。
    """
    return bs.find_all(tag, **kwargs)


def _get_tag_one(bs, tag, **kwargs):
    """
    指定したtagのうち一番初めのものを取得する。
    """
    return bs.find(tag, **kwargs)


def get_contents(bs, tag, cls):
    """
    公演の情報を取得する。
    """
    cls = get_env(cls)
    contents = _get_tag(bs, tag, class_=cls)
    return [c.get_text().replace(' ', '').replace('\n', '') for c in contents]


def get_date(bs, status_tag, status_cls, date_tag, date_cls):
    """
    公演の日付を取得する。
    """
    status_cls = get_env(status_cls)

    status = _get_tag(bs, status_tag, class_=status_cls)
    for s in status:
        s.extract()

    return get_contents(bs, date_tag, date_cls)


def get_price(
    base, bs, detail_tag, detail_cls,
    prc_tag, prc_cls, prc_href, val_tag, val_cls
):
    """
    公演の料金情報を取得する。
    """
    base = get_env(base)
    detail_cls = get_env(detail_cls)
    prc_cls = get_env(prc_cls)
    prc_href = get_env(prc_href)
    val_cls = get_env(val_cls)

    detail = _get_tag(bs, detail_tag, class_=detail_cls)
    link_list = []
    for d in detail:
        link = d.get('href')
        link_list.append(link)

    price_link_list = []
    for li in link_list:
        page = _get_bs(base + li)
        price_link = _get_tag_one(
            page, prc_tag, class_=prc_cls, href=re.compile(prc_href)).get('href')
        price_link_list.append(price_link)

    price_list = []
    for li in price_link_list:
        page = _get_bs(base + li)
        price = _get_tag_one(page, val_tag, class_=val_cls).get_text()
        price_list.append(price)

    return price_list


def get_json_script(bs, tag, type):
    """
    JSON形式で記述された公演情報を取得する。
    """
    type = get_env(type)
    script = _get_tag_one(bs, tag, type=type).string
    return json.loads(script)


def make_df(title, date, place, price, script):
    """
    公演情報のDataFrameを作成する。
    """
    return pd.DataFrame(
        {
            'title': title,
            'date': date,
            'place': place,
            'price': price,
            'start_date': [j['startDate'] for j in script],
            'end_date': [j['endDate'] for j in script],
            'url': [j['url'] for j in script],
            'description': [j['description'] for j in script],
        }
    )


def get_main_bs(base, main_url):
    """
    公演情報のBeautifulSoupオブジェクトを取得する。
    """
    return _get_bs(base + main_url)


def get_env(env):
    """
    引数envで設定された環境変数を取得する。
    """
    val = os.environ.get(env)
    val_list = val.split(',')

    return val_list if len(val_list) > 1 else val


if __name__ == '__main__':
    store = pd.DataFrame()

    for i in range(100):
        main_url = get_env('MAIN_URL').format(i+1)
        main_bs = get_main_bs(get_env('BASE'), main_url)

        title = get_contents(main_bs, 'span', 'CLASS_TITLE')
        if title == []:
            break
        print(f'scraping {i+1} files...')
        date = get_date(main_bs, 'span', 'CLASS_STATUS', 'p', 'CLASS_DATE')
        place = get_contents(main_bs, 'p', 'CLASS_PLACE')
        price = get_price('BASE', main_bs, 'a', 'CLASS_DETAIL', 'a',
                          'CLASS_PRICE', 'HREF_PRICE', 'td', 'CLASS_PRICE_VALUE')
        script = get_json_script(main_bs, 'script', 'JSON_TYPE')

        df = make_df(title, date, place, price, script)
        store = pd.concat([store, df])

    store.to_csv('../etc/output/df.csv')
