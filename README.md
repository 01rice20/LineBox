# LineBox

## This is a simple calculator
1. You can use four functions for total, there're addition, subtraction, multiplication and division separately.
2. You can also send some stickers, the robot will send you some cute stickers, too.

## How to use
### Install python packages
> pip install -r requirements.txt
### Enter your IDs in .env.sample
```
LINE_TOKEN =
LINE_SECRET =
LINE_UID =
```
### Run ngrok
> ngrok http 8787
### Run main.py
> python3 main.py

## How to compute
```
1. Addition: a + b
2. Subtraction: a - b
3. Multiplication: a * b
4. Division: a / b
(Please separate three of them with spaces)
```

## Simple accounting book -> accounting.py
1. You can use four functions below: note, report, delete and sum

## How to use
### Install InfluxDB
```
sudo curl -sL https://repos.influxdata.com/influxdb.key | sudo apt-key add -
sudo echo "deb https://repos.influxdata.com/ubuntu bionic stable" | sudo tee /etc/apt/sources.list.d/influxdb.list
sudo apt update
sudo apt install influxdb
```
### Run InfluxDB
```
sudo systemctl enable influxdb
sudo systemctl start influxdb
sudo service influxdb start
```
### Run ngrok
> ngrok http 8787
### Line developer Webhook URL enter
> Copy the URL on ngrok "Forwarding" Session Status 

> Ex: https://0af4-35-78-232-104.jp.ngrok.io
### Run accounting.py
> python3 accounting.py

> And make sure the success message has pop out after clicking vertify button on Line developer webhook setting

## How to record
```
1. Note (Track your expenses, Please separate four of them with spaces): 
  #note test1 + 1000 (income)
  #note test2 - 200  (expenses)
2. Report (List all items): #report
3. Delete the item: 
  #delete all (delete all your items)
  #delete [num] (All items got a number, enter the number shown on #report)
4. Check out your daily/weekly/monthly cost (Default is 1 day): 
  #sum 1d (check today's balence)
  #sum 7d (check this week's balence)
  #sum 30d (check this month's balence)
```
