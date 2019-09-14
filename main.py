from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageSendMessage
from bs4 import BeautifulSoup
import requests
import urllib
import os
import json
import datetime
import random

app = Flask(__name__)

YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)

# 乱数の設定
random_text = random.randint(0, 2)
random_img = random.randint(0, 99)


def get_text():
    hour = datetime.datetime.now().hour
    weekday = datetime.date.today().weekday()  # 曜日を示す 0:Mon

    if 6 <= hour <= 16:
        WORK = True
    else:
        WORK = False

    if weekday >= 5:
        HOLIDAY = True
    else:
        HOLIDAY = False

    # 送信するテキスト
    if (WORK, HOLIDAY) == (True, False):
        text_list = ["今日もファイト！", "無理しないでね", "頑張っててえらい！"]
    elif (WORK, HOLIDAY) == (False, False):
        text_list = ["今日もお疲れさま", "よく頑張ったね", "ご褒美だよ"]
    else:
        text_list = ["休日だからゆっくり休んでね", "いつもご苦労さま", "休日楽しんでね"]
    return text_list


class GoogleImageSerch(object):
    def __init__(self):
        self.GOOGLE_IMAGE_SEARCH_URL = "https://www.google.co.jp/search"
        self.session = requests.session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:10.0) \
                    Gecko/20100101 Firefox/10.0"
            }
        )

    def search(self, keyword, maximum):
        query = self.generate_query(keyword)
        return self.serch_images(query, maximum)

    def generate_query(self, keyword):
        # search query generator
        page = 0
        while True:
            params = urllib.parse.urlencode(
                {"q": keyword, "tbm": "isch", "ijn": str(page)}
            )

            yield self.GOOGLE_IMAGE_SEARCH_URL + "?" + params
            page += 1

    def serch_images(self, generate_query, maximum):
        img_url_list = []
        total = 0
        while True:
            # search
            html = self.session.get(next(generate_query)).text
            soup = BeautifulSoup(html, "lxml")
            elements = soup.select(".rg_meta.notranslate")
            jsons = [json.loads(e.get_text()) for e in elements]
            image_url_list = [js["ou"] for js in jsons]

            # add search results
            if not image_url_list:
                # cprint("No more images.", "yellow")
                break
            elif len(image_url_list) > maximum - total:
                img_url_list += image_url_list[: maximum - total]
                break
            else:
                img_url_list += image_url_list
                total += len(image_url_list)
        return img_url_list


target = "イケメン"
num = 100
google_image_serch = GoogleImageSerch()
img_url_list = google_image_serch.search(target, num)
text_list = get_text()


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        [ImageSendMessage(original_content_url=img_url_list[random_img],
                          preview_image_url=img_url_list[random_img]),
         TextSendMessage(text=text_list[random_text])]  # messageは最大５件 配列にして渡す
    )


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
