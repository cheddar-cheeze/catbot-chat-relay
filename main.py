import tailer
import getpass
import telegram_wrapper
import csv

chat_id = ''
bot = telegram_wrapper.Client(token='')
while True:
    try:
        for line in tailer.follow(open('/opt/cathook/data/chat-' + getpass.getuser() + '.csv')):
            out = csv.reader(line, delimiter=',')
            dict_message = []
            for row in out:
                dict_message.append(','.join(row).strip(','))
            new_id = int(dict_message[2]) + 76561197960265728
            md = """
            [%n](https://steamcommunity.com/profiles/%i)
            %m
            """
            new = md.replace('%n', dict_message[4]).replace('%m', dict_message[6]).replace('%i', str(new_id))
            print(new)
            bot.send_message(chat_id, new, 'markdown')
    except:
        pass
