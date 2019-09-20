# *--conding:utf-8--*
import os, re
import random

import redis
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import *
import telebot
import requests
from data_comming import get_all_music, get_all_music_list

requests.adapters.DEFAULT_RETRIES = 5
r = requests.session()
r.keep_alive = False
bot = telebot.TeleBot(token=API_TOKEN)



# 底部标签
def bottom_markup():
    try:
        markup = InlineKeyboardMarkup()
        markup.row_width = 1
        markup.one_time_keyboard = 2
        markup.add(InlineKeyboardButton(type_list[0], callback_data='type_{}'.format(type_list[0])),
                   InlineKeyboardButton(type_list[1], callback_data='type_{}'.format(type_list[1])),
                   InlineKeyboardButton(type_list[2], callback_data='type_{}'.format(type_list[2])),
                   InlineKeyboardButton(type_list[3], callback_data='type_{}'.format(type_list[3])),
                   InlineKeyboardButton(type_list[4], callback_data='type_{}'.format(type_list[4])),
                   InlineKeyboardButton(type_list[5], callback_data='type_{}'.format(type_list[5])),
                   InlineKeyboardButton(type_list[6], callback_data='type_{}'.format(type_list[6])),
                   InlineKeyboardButton('我要上传/upload', callback_data='upload'),
                   InlineKeyboardButton('联系客服/Customer service', url=my_url))
        return markup
    except:
        pass
@bot.message_handler(commands=['leave'])
def leave_group(message):
    try:
        bot.send_message(message.chat.id,'我要走了，各位小姐姐拜拜')
        bot.leave_chat(message.chat.id)
    except:
        pass
        return

@bot.message_handler(commands=['start'])
def handle_start(message):
    try:
        bot.send_message(message.chat.id, "🌹欢迎来到天山一枝梅的音乐空间\n你可以直接输入歌名查找",
                         reply_markup=bottom_markup())
    except Exception as e:
        pass


@bot.message_handler(commands=['cat_musice'])
def cat_all_musice(message):
    try:
        all_musice = get_all_music_list()
        bot.send_message(message.chat.id, '服务器总计：{} 部资源，请大家踊跃上传高质量音乐'.format(len(all_musice)))
    except:
        return


@bot.callback_query_handler(func=lambda call: call.data)
def send_music_file(call):
    try:
        pool = redis.ConnectionPool(host='localhost', port=6379, decode_responses=True, password=123456)
        redis_db = redis.Redis(connection_pool=pool)
        if redis_db.get('music_timer'):
            bot.answer_callback_query(call.id, '操作太频繁,正在拼命准备资源，请稍等片刻.....', show_alert=True, cache_time=5)
        else:
            redis_db.set('music_timer', 'mutton', ex=2)
            if call.data.startswith('music_'):
                music_type = re.findall(r'^music_(.*)_type_(.*)', call.data)[0]
                path = os.path.abspath(os.path.join(os.getcwd(), music_type[1]))
                msg_id = bot.reply_to(call.message, '正在发送....').message_id
                with open(path + '/' + music_type[0], 'rb')as f:
                    bot.send_audio(call.message.chat.id, f,
                                   caption=music_type[0].split('.')[0] + "<a href='{}'>{}</a>".format(bot_url,
                                                                                                      '@all_musices_bot'),
                                   parse_mode='HTML', timeout=20)
                    bot.delete_message(call.message.chat.id, msg_id)
            elif call.data.startswith('type_'):
                music_type: str = re.search(r'^type_(.*)', call.data).group(1)
                music_list = get_all_music(music_type)
                mark = InlineKeyboardMarkup()
                for one in random.sample(music_list, 10):
                    mark.add(InlineKeyboardButton(text=one, callback_data='music_{}_type_{}'.format(one, music_type)))
                mark.add(InlineKeyboardButton(text='返回目录', callback_data='go_last'))
                bot.edit_message_text(music_type + '随机10首', chat_id=call.message.chat.id,
                                      message_id=call.message.message_id,
                                      reply_markup=mark)
            elif call.data == 'go_last':
                bot.edit_message_text('音乐机器人', chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      reply_markup=bottom_markup())
            elif call.data == 'upload':
                msg = bot.send_message(call.message.chat.id,
                                       '请输入上传类型 歌曲名称空格隔开，\n如：热门DJ舞曲  狂浪\n  输入：q 退出输入模式！\nPlease enter the type of upload and the name of the song, \nseparated by a space,For Example: Englishsongs  happyBirthday')
                bot.register_next_step_handler(msg, get_user_input_name)
    except:
        pass


@bot.message_handler(func=lambda msg: msg.text)
def musin(message):
    try:
        name = ''.join(message.text.strip())
        music_list = get_all_music_list()
        for one in music_list:
            if name + '.mp3' == one[0] or name + '.m4a' == one[0]:
                msg_id = bot.reply_to(message, '正在发送....').message_id
                with open(one[1], 'rb')as f:
                    bot.send_audio(message.chat.id, f,
                                   caption=name + "<a href='{}'>{}</a>".format(bot_url, '@all_musices_bot'),
                                   parse_mode='HTML', timeout=20)
                    bot.delete_message(message.chat.id, msg_id)
                    return
            else:
                pass
        bot.send_message(message.chat.id, '你输入的歌名不存在，请先上传')
    except:
        return


def get_user_input_name(message):
    try:
        if len(message.text) > 20:
            msg = bot.reply_to(message, '名字太长，请重新输入')
            bot.register_next_step_handler(msg, get_user_input_name)
        elif message.text.strip().upper() == 'Q':
            bot.reply_to(message, '退出成功，你现在可以输入歌名进行快速搜索额')
            return
        else:
            input_list = message.text.split()
            msg = bot.reply_to(message, '请拖入音频文件:')
            bot.register_next_step_handler(msg, save_user_input_file, input_list)
    except:
        bot.reply_to(message, '操作失败')
        return


def save_user_input_file(message, input_list):
    try:
        if message.content_type == 'document':
            file = bot.get_file(file_id=message.document.file_id)
            new_file = bot.download_file(file.file_path)
            with open(input_list[0] + '/' + input_list[1] + '.mp3', 'wb')as f:
                f.write(new_file)
            bot.reply_to(message, '上传成功！')
        elif message.content_type == 'audio':

            file = bot.get_file(file_id=message.audio.file_id)
            new_file = bot.download_file(file.file_path)
            with open(input_list[0] + '/' + input_list[1] + '.mp3', 'wb')as f:
                f.write(new_file)
            bot.reply_to(message, '上传成功！')
        elif message.text.strip().upper() == 'Q':
            bot.reply_to(message, '退出成功，你现在可以输入歌名进行快速搜索额')
        else:
            bot.reply_to(message, '上传的不是音频文件，请重新拖入文件上传！')

    except:
        bot.reply_to(message, '上传失败')
        return


if __name__ == '__main__':
    bot.skip_pending = True
    bot.polling(none_stop=True)
