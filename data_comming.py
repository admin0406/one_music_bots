# *--conding:utf-8--*
import sys, os
import time
import requests

requests.packages.urllib3.disable_warnings()


def download(url, file_path):
    # verify=False 这一句是为了有的网站证书问题，为True会报错
    r = requests.get(url, stream=True, verify=False)
    if r.status_code == 200:
        chunk_size = 1024
        start = time.time()
        total_size = int(r.headers['Content-Length'])
        temp_size = 0
        print('[文件大小]：%0.2f MB' % (total_size / chunk_size / 1024))
        with open(file_path + '.mp3', "wb") as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    temp_size += len(chunk)
                    f.write(chunk)
                    f.flush()
                    done = int(50 * temp_size / total_size)
                    sys.stdout.write("\r[%s%s] %d%%" % ('█' * done, ' ' * (50 - done), 100 * temp_size / total_size))
                    sys.stdout.flush()
        end = time.time()
        print('\n' + '下载完成！用时%.2f秒' % (end - start))
    else:
        print('请求失败')


def get_username_from_message(message):
    if message.from_user.username:
        return message.from_user.username
    else:
        return ''


def get_nickname_from_message(message):
    frist_name = message.from_user.first_name
    last_name = message.from_user.last_name
    if frist_name and last_name and frist_name != last_name:
        username = frist_name + last_name
    else:
        username = frist_name
    return username


def get_chat_id_from_message(message):
    return message.from_user.id


def get_all_music_list(path=None):
    if path:
        return [(i, root + '/' + i) for root, dirs, files in os.walk(path) for i in files if
                i and os.path.splitext(i)[1].lower() == '.m4a' or os.path.splitext(i)[1].lower() == '.mp3']
    else:
        return [(i, root + '/' + i) for root, dirs, files in os.walk(os.path.abspath(os.path.join(os.getcwd())), ) for
                i in files if
                i and os.path.splitext(i)[1].lower() == '.m4a' or os.path.splitext(i)[1].lower() == '.mp3']


def get_all_music(type_name):
    path = os.path.abspath(os.path.join(os.getcwd(), type_name))
    return [one[0] for one in get_all_music_list(path)]
