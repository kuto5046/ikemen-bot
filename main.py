from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageSendMessage
import os

app = Flask(__name__)

YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)

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
# def handle_message(event):
#      line_bot_api.reply_message(
#      	event.reply_token,
#         TextSendMessage(text="お疲れさま"))


def handle_message(event):
    line_bot_api.reply_message(
    	event.reply_token,
	ImageSendMessage(original_content_url="https://symfo.web.fc2.com/sample_src/lena.jpg", 
			 preview_image_url="https://symfo.web.fc2.com/sample_src/lena_preview.jpg")
    )

    line_bot_api.reply_message(
       event.reply_token,
       TextSendMessage(text="いつもお疲れさま")
    )


if __name__ == "__main__":
#    app.run()
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
