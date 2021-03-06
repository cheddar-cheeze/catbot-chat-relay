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
                md = "[ %n ](https://steamcommunity.com/profiles/%i): %m"
                new = md.replace('%n', cleaned_name).replace('%m', dict_message[6]).replace('%i', str(new_id))
                print(new)
                message_obj = {
                    'ipc_id': dict_message[-1],
                    'text': new
                }
                message_queue.append(message_obj)
        except Exception as e:
            print(e)

def relay(bot ,job):
    logs = glob.glob('/opt/cathook/data/*.csv')
    for file in logs:
        if file:
            Thread(target=tail, args=(bot, job, file)).start()

def message_send(bot, job):
    if message_queue[:]:
        filter_list = []
        for message in message_queue:
            filter_list.append(message['text'])
        a, seen, result = filter_list, set(), []
        for idx, item in enumerate(a):
            if item not in seen:
                seen.add(item)
            else:
                result.append(idx)
        for indx in result:
            print('Removing duplicate at queue pos:' + str(indx))
            message_queue.pop(indx)
        del filter_list[:]
        print("Sending Messages!")
        try:
            for message_obj in message_queue:
                message = "*cat-bot " + str(message_obj['ipc_id']) + "* \n" + str(message_obj['text'])
                try:
                    bot.send_message(chat_id='-1001203927071', text=message, parse_mode='MARKDOWN', disable_web_page_preview=True, disable_notification=True)
                except Exception as e:
                    break
            del message_queue[:]
        except Exception as e:
            print(e)
        finally:
            print("Messages Sent!")

dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("say", say, pass_args=True))
dispatcher.add_handler(CommandHandler("sayall", sayall, pass_args=True))
updater.start_polling()
job.run_once(relay, 1)
job.run_repeating(message_send, interval=10, first=0)
updater.idle()
