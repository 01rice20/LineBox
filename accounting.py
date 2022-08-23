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
from influxdb import InfluxDBClient

class DB():
    def __init__(self, ip, port, user, password, db_name):
        self.client = InfluxDBClient(ip, port, user, password, db_name) 
        print('Influx DB init.....')

    def insertData(self, data):
        """
        [data] should be a list of datapoint JSON,
        "measurement": means table name in db
        "tags": you can add some tag as key
        "fields": data that you want to store
        """
        if self.client.write_points(data):
            return True
        else:
            print('Falied to write data')
            return False

    def queryData(self, query):
        """
        [query] should be a SQL like query string
        """
        return self.client.query(query)

    def delete_all(self):
        return self.client.drop_measurement('accounting_items')

# Init a Influx DB and connect to it
db = DB('127.0.0.1', 8086, 'root', '', 'testdb')
#db.create_database('testdb')
load_dotenv() # Load your local environment variables

CHANNEL_TOKEN = os.environ.get('LINE_TOKEN')
CHANNEL_SECRET = os.getenv('LINE_SECRET')

app = FastAPI()

My_LineBotAPI = LineBotApi(CHANNEL_TOKEN) # Connect Your API to Line Developer API by Token
handler = WebhookHandler(CHANNEL_SECRET) # Event handler connect to Line Bot by Secret key

CHANNEL_ID = os.getenv('LINE_UID') # For any message pushing to or pulling from Line Bot using this ID
My_LineBotAPI.push_message(CHANNEL_ID, TextSendMessage(text='Welcome ! Want to track your expenses ?')) # Push a testing message

# Events for message reply
my_event = ['#note', '#report', '#delete', '#sum']

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
    global accounting
    
    # Split message by white space
    recieve_message = str(event.message.text).split(' ')
    # Get first splitted message as command
    case_ = recieve_message[0].lower().strip()
    
    #note
    if re.match(my_event[0], case_):
        # cmd: #note [事件] [+/-] [錢]
        event_ = recieve_message[1]
        op = recieve_message[2]
        money = int(recieve_message[3])
        # process +/-
        if op == '-':
            money *= -1
        # get user id
        user_id = event.source.user_id
        query_str = """
        select * from accounting_items 
        """
        result = db.queryData(query_str)
        points = result.get_points(tags={'user': str(user_id)})
        reply_text = ''
        i = 0
        for i, point in enumerate(points):
            i += 1
        number = i
        print("number: ", number)
        # build data
        data = [
            {
                "measurement" : "accounting_items",
                "tags": {
                    "num": number,
                    "user": str(user_id)
                },
                "fields":{
                    "event": str(event_),
                    "money": money
                }
            }
        ]
        if db.insertData(data):
            # successed
            My_LineBotAPI.reply_message(
                event.reply_token,
                TextSendMessage(
                    text="Write to DB Successfully!"
                )
            )
    #report
    elif re.match(my_event[1], case_):
        # get user id
        user_id = event.source.user_id
        query_str = """
        select * from accounting_items 
        """
        result = db.queryData(query_str)
        points = result.get_points(tags={'user': str(user_id)})
        
        reply_text = ''
        for i, point in enumerate(points):
            time = point['time']
            event_ = point['event']
            money = point['money']
            number = point['num']
            reply_text += f'[{number}] -> [{time}] : {event_}   {money}\n'

        My_LineBotAPI.reply_message(
            event.reply_token,
            TextSendMessage(
                text=reply_text
            )
        )
    #delete
    elif re.match(my_event[2], case_):
        item = recieve_message[1]
        
        if item == 'all':
            db.delete_all()
            My_LineBotAPI.reply_message(
                event.reply_token,TextSendMessage(text= "All deleted.")
            )
        elif item.isdigit():
            item = int(recieve_message[1])
            querystr = "SELECT * from accounting_items"
            rs = db.queryData(querystr)
            points = rs.get_points()
            cnt = 0
            for items in points:
                #print(cnt, "  ", items['num'])
                if item == cnt:
                    print (items['num'])
                    db.queryData(f"SELECT * INTO delete_data FROM accounting_items WHERE \"num\"!=\'{item}\' group by *")
                    db.queryData("DROP measurement accounting_items")
                    result =db.queryData("SELECT * INTO accounting_items FROM delete_data group by *")
                    db.queryData("DROP measurement delete_data")
                    My_LineBotAPI.reply_message(
                        event.reply_token,TextSendMessage(text= "Data deleted.") 
                    )
                cnt += 1
    #sum
    elif re.match(my_event[3], case_):
        date = recieve_message[1]
        if date == "30d":
            sumstr = "SELECT * FROM accounting_items WHERE time > now() - 30d"
        elif date == "7d":
            sumstr = "SELECT * FROM accounting_items WHERE time > now() - 7d"
        else:
            sumstr = "SELECT * FROM accounting_items WHERE time > now() - 1d"
        result = db.queryData(sumstr)
        user_id = event.source.user_id
        points = result.get_points(tags={'user': str(user_id)})
        total = 0
        for i, point in enumerate(points):
            money = point['money']
            total += money
        print("Total: ", total)
        My_LineBotAPI.reply_message(
            event.reply_token,TextSendMessage(text=f"The total balence in {date} is ${total}.")
        )
    else:
        My_LineBotAPI.reply_message(
            event.reply_token,
            TextSendMessage(
                text=str(event.message.text)
            )
        )

# Line Sticker Class
class My_Sticker:
    def __init__(self, p_id: str, s_id: str):
        self.type = 'sticker'
        self.packageID = p_id
        self.stickerID = s_id

# Add stickers into my_sticker list
my_sticker = [My_Sticker(p_id='446', s_id='1995'), My_Sticker(p_id='446', s_id='2012'),
     My_Sticker(p_id='446', s_id='2024'), My_Sticker(p_id='446', s_id='2027'),
     My_Sticker(p_id='789', s_id='10857'), My_Sticker(p_id='789', s_id='10877'),
     My_Sticker(p_id='789', s_id='10881'), My_Sticker(p_id='789', s_id='10885'),
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