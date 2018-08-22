import tailer
import requests
from telegram.ext import Updater, CommandHandler, Filters
import csv
from threading import Thread
import glob

updater = Updater(token='')
dispatcher = updater.dispatcher
job = updater.job_queue

def start(bot, update):
    bot.send_message(chat_id=update['message']['chat']['id'], text=
    """*Commands*
    say - <ipc-connection><message>
    sayall - <message>
    """, parse_mode='MARKDOWN')

def say(bot, update, args):
    message = ' '.join(str(x) for x in args[1:])
    if ';' in message:
        bot.send_message(chat_id=update['message']['chat']['id'], text='No command injection for u faggot')
    else:
        user_name = update['message']['chat']['username']
        requests.post('http://localhost:8081/api/direct/exec',
                      json={
                          'target': args[0],
                          'cmd': 'say "[RELAY]' + user_name + ": " + message + '"'
                      })
        print(user_name + ' sent "' + message + '" to catbot ' + args[0])
        bot.send_message(chat_id=update['message']['chat']['id'], text='message sent!')
        bot.send_message(chat_id=-1001203927071, text='@' + user_name + ' sent: "' + message.replace('"', "'") + '", to catbot' + args[0])

def sayall(bot, update, args):
    message = ' '.join(str(x) for x in args)
    if ';' in message:
        bot.send_message(chat_id=update['message']['chat']['id'], text='No command injection for u faggot')
    else:
        user_name = update['message']['chat']['username']
        requests.post('http://localhost:8081/api/direct/exec_all',
                      json={
                          'cmd': 'say "[RELAY]' + user_name + ": " + message + '"'
                      })
        print(user_name + ' sent "' + message + '" to all catbots')
        bot.send_message(chat_id=update['message']['chat']['id'], text='message sent!')
        bot.send_message(chat_id=-1001203927071, text='@' + user_name + ' sent: "' + message.replace('"', "'") + '", to all catbots')

message_queue = []
def tail(bot, job, file):
    print('tailing ' + file)
    while True:
        try:
            for line in tailer.follow(open(file)):
                out = csv.reader(line, delimiter=',')
                dict_message = []
                for row in out:
                    dict_message.append(','.join(row).strip(','))
                new_id = int(dict_message[2]) + 76561197960265728
                cleaned_name = dict_message[4].replace('[', '').replace(']', '')
                md = "(catbot-%c) \n [ %n ](https://steamcommunity.com/profiles/%i): %m"
                new = md.replace('%n', cleaned_name).replace('%m', dict_message[6]).replace('%i', str(new_id)).replace('%c', dict_message[-1])
                print(new)
                message_queue.append(new)
        except Exception as e:
            print(e)

def relay(bot ,job):
    logs = glob.glob('/opt/cathook/data/*.csv')
    for file in logs:
        if file:
            Thread(target=tail, args=(bot, job, file)).start()

def message_send(bot, job):
    if message_queue[:]:
        print("Sending Messages!")
        try:
            cleaned_queue = set(message_queue)
            for message in cleaned_queue:
                bot.send_message(chat_id='-1001203927071', text=message, parse_mode='MARKDOWN', disable_web_page_preview=True, disable_notification=True)
            del message_queue[:]
            print("Messages Sent!")
        except Exception as e:
            print(e)

dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("say", say, pass_args=True))
dispatcher.add_handler(CommandHandler("sayall", sayall, pass_args=True))
updater.start_polling()
job.run_once(relay, 1)
job.run_repeating(message_send, interval=5, first=0)
