import os
import re
import json
import random
from dotenv import load_dotenv
from pyquery import PyQuery
from fastapi import FastAPI, Request, HTTPException
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *

load_dotenv() # Load your local environment variables

CHANNEL_TOKEN = os.environ.get('LINE_TOKEN')
CHANNEL_SECRET = os.getenv('LINE_SECRET')

app = FastAPI()

My_LineBotAPI = LineBotApi(CHANNEL_TOKEN) # Connect Your API to Line Developer API by Token
handler = WebhookHandler(CHANNEL_SECRET) # Event handler connect to Line Bot by Secret key

CHANNEL_ID = os.getenv('LINE_UID') # For any message pushing to or pulling from Line Bot using this ID
My_LineBotAPI.push_message(CHANNEL_ID, TextSendMessage(text='This is a simple calculator!')) # Push a testing message

# Line Developer Webhook Entry Point
@app.post('/')
async def callback(request: Request):
    body = await request.body() # Get request
    signature = request.headers.get('X-Line-Signature', '') # Get message signature from Line Server
    try:
        handler.handle(body.decode('utf-8'), signature) # Handler handle any message from LineBot and 
    except InvalidSignatureError:
        raise HTTPException(404, detail='LineBot Handle Body Error !')
    return 'OK'

# All message events are handling at here !
@handler.add(MessageEvent, message=TextMessage)
def handle_textmessage(event):
    global my_calculator
    recieve_message = str(event.message.text).split(' ')
    #print(len(recieve_message))
    #print(len(recieve_message[0]))
    #print(len(recieve_message[2]))    
    if len(recieve_message) == 3 and (recieve_message[1]=='+' or recieve_message[1]=='-' or recieve_message[1]=='*' or recieve_message[1]=='/') and ((recieve_message[0].isdigit()) or (ord(recieve_message[0][0]) == 45 and recieve_message[0][1:].isdigit())) and ((recieve_message[2].isdigit()) or (ord(recieve_message[2][0]) == 45 and recieve_message[2][1:].isdigit())):
        num1 = int(recieve_message[0])
        num2 = int(recieve_message[2])
        #print (ord(recieve_message[2]))
        if (recieve_message[1] == '+'):
            sum = num1 + num2
        elif (recieve_message[1] == '-'):
            sum = num1 - num2
        elif (recieve_message[1] == '*'):
            sum = num1 * num2
        elif (recieve_message[1] == '/'):
            if (recieve_message[2] == '0'):
                My_LineBotAPI.reply_message(event.reply_token,TextSendMessage(text='Dividend cannot be 0'))
                return
            else:
                sum = num1 / num2
    else:
        My_LineBotAPI.reply_message(
                event.reply_token,
                TextSendMessage(text='It seems like there is something wrong with your command! Please check it again')
            )
        return
    text_message = TextSendMessage(text=sum)
    My_LineBotAPI.reply_message(event.reply_token,text_message)

# Line Sticker Class
class My_Sticker:
    def __init__(self, p_id: str, s_id: str):
        self.type = 'sticker'
        self.packageID = p_id
        self.stickerID = s_id

# Add stickers into my_sticker list
my_sticker = [My_Sticker(p_id='6362', s_id='11087926'), My_Sticker(p_id='6362', s_id='11087936'),
     My_Sticker(p_id='6362', s_id='11087937'), My_Sticker(p_id='6362', s_id='11087939'),
     My_Sticker(p_id='6632', s_id='11825385'), My_Sticker(p_id='8522', s_id='16581277'),
     ]

# Line Sticker Event
@handler.add(MessageEvent, message=StickerMessage)
def handle_sticker(event):
    # Random choice a sticker from my_sticker list
    ran_sticker = random.choice(my_sticker)
    # Reply Sticker Message
    My_LineBotAPI.reply_message(
        event.reply_token,
        StickerSendMessage(
            package_id= ran_sticker.packageID,
            sticker_id= ran_sticker.stickerID
        )
    )

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app='main:app', reload=True, host='0.0.0.0', port=8787)
