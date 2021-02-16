import os
import re
import requests
from prettytable import PrettyTable
from datetime import datetime, timedelta


def output_time(check_time):
    playtime_hours = int(check_time / 3600)
    playtime_minutes = int((check_time - (3600 * playtime_hours)) / 60)
    playtime_seconds = int(
        check_time - (playtime_hours * 3600 + playtime_minutes * 60))
    time_logs = '{0}:{1}:{2}'.format(playtime_hours, playtime_minutes,
                                     playtime_seconds)
    return time_logs


def total_time(logs_join, logs_exit, vanish_log_join,
               vanish_log_exit, days):
    playtime_check = 0
    vanish_time = 0
    for j in range(len(logs_join)):
        time_in_game = get_time(logs_join[j], logs_exit[j])
        playtime_check += time_in_game
    for v in range(len(vanish_log_join)):
        time_in_vanish = get_time(vanish_log_join[v], vanish_log_exit[v])
        vanish_time += time_in_vanish
    playtime_total = output_time(playtime_check)
    playtime_vanish = output_time(vanish_time)
    playtime = output_time(playtime_check - vanish_time)
    average_online_total = output_time(playtime_check / len(days))
    average_online = output_time((playtime_check - vanish_time) / len(days))
    return (playtime_total, playtime_vanish, playtime,
            average_online_total, average_online)


def get_time(join_logs, exit_logs):
    log_join = join_logs.split(' ')[0].split('-')
    log_exit = exit_logs.split(' ')[0].split('-')

    year_join = int(log_join[2])
    month_join = int(log_join[1])
    day_join = int(log_join[0])
    hour_join = int(log_join[3])
    minute_join = int(log_join[4])
    seconds_join = int(log_join[5])

    year_exit = int(log_exit[2])
    month_exit = int(log_exit[1])
    day_exit = int(log_exit[0])
    hour_exit = int(log_exit[3])
    minute_exit = int(log_exit[4])
    seconds_exit = int(log_exit[5])

    time_join = datetime(year_join, month_join, day_join,
                         hour_join, minute_join, seconds_join)
    time_exit = datetime(year_exit, month_exit, day_exit, hour_exit,
                         minute_exit, seconds_exit)
    time_in_game = int((time_exit - time_join).total_seconds())
    return time_in_game


def fix_exit(logs_join, logs_exit):
    time_in_game = get_time(logs_join[0], logs_exit[0])
    if time_in_game < 0:
        logs_exit.pop(0)
    return logs_exit


def check_activity(nick, user_dates):
    player = nick.lower()
    nick_write = player
    logs_join = []
    logs_exit = []
    vanish_log_join = []
    vanish_log_exit = []
    activity_local_chat = 0
    activity_global_chat = 0
    activity_private_message = 0
    kick = 0
    warn = 0
    mute = 0
    ban = 0
    vanish = False
    check_coincidence = None
    mute_list = ['/tempmute', '/mute']
    ban_list = ['/tempban', '/ban']
    m_list = ['/tell', '/m', '/w', '/msg', '/pm', '/t', '/r']
    for date in user_dates:
        file = 'logs/{0}.txt'.format(date)
        with open(file, 'r', encoding='utf-8') as logs_file:
            for line in logs_file:
                line_split = line.split(' ')
                time_log = line_split[0].split('[')[1].split(']')[0].split(':')
                time_logs = '{0}-{1}-{2}'.format(time_log[0], time_log[1],
                                                 time_log[2])
                line_time = '{0}-{1}-{2}'.format(date, time_logs,
                                                 ' '.join(line_split[
                                                          1:len(line_split)]))
                if (len(line_split) == 3
                        and line_split[1].lower() == player
                        and line_split[2].split('\n')[0] == 'зашёл'):
                    if check_coincidence == 'зашёл':
                        logs_join.pop(-1)
                    logs_join.append(line_time)
                    check_coincidence = 'зашёл'
                    nick_write = line_split[1]
                elif (len(line_split) == 3
                      and line_split[1].lower() == player
                      and line_split[2].split('\n')[0] == 'вышел'):
                    if check_coincidence == 'вышел':
                        logs_exit.pop(-1)
                    logs_exit.append(line_time)
                    check_coincidence = 'вышел'
                    if vanish:
                        vanish_log_exit.append(line_time)
                        vanish = False
                elif (len(line_split) > 3
                      and line_split[1] == '[L]'
                      and line_split[2].split(':')[0].lower() == player):
                    activity_local_chat += 1
                elif (len(line_split) > 3
                      and line_split[1] == '[G]'
                      and line_split[2].split(':')[0].lower() == player):
                    activity_global_chat += 1
                elif (len(line_split) > 5
                      and line_split[1].lower() == player
                      and line_split[5].lower() in m_list):
                    activity_private_message += 1
                elif (len(line_split) > 6
                      and line_split[1].lower() == player
                      and line_split[5].lower() == '/kick'):
                    kick += 1
                elif (len(line_split) > 6
                      and line_split[1].lower() == player
                      and line_split[5].lower() == '/warn'):
                    warn += 1
                elif (len(line_split) > 6
                      and line_split[1].lower() == player
                      and line_split[5].lower() in mute_list):
                    mute += 1
                elif (len(line_split) > 6
                      and line_split[1].lower() == player
                      and line_split[5].lower() in ban_list):
                    ban += 1
                elif (len(line_split) == 6
                      and line_split[1].lower() == player
                      and line_split[5].lower().split('\n')[0] == '/vanish'
                      or len(line_split) > 6
                      and line_split[1].lower() == player
                      and line_split[5].lower() == '/vanish'):
                    if not vanish:
                        vanish_log_join.append(line_time)
                        vanish = True
                    else:
                        vanish_log_exit.append(line_time)
                        vanish = False
    logs_exit = fix_exit(logs_join, logs_exit)
    if len(logs_join) > len(logs_exit):
        logs_exit.append(logs_join[-1])
    return ([nick_write, activity_local_chat, activity_global_chat,
             activity_private_message, warn, mute, kick, ban,
             *total_time(logs_join, logs_exit, vanish_log_join,
                         vanish_log_exit, user_dates)])


def get_user_dates(date1, date2):
    user_dates = []
    try:
        d1 = datetime.strptime(date1, '%d-%m-%Y')
        d2 = datetime.strptime(date2, '%d-%m-%Y')
        for day in range((d2 - d1).days + 1):
            user_dates.append((d1 + timedelta(days=day)).strftime('%d-%m-%Y'))
        if len(user_dates) == 0:
            for day in range((d1 - d2).days + 1):
                user_dates.append(
                    (d2 + timedelta(days=day)).strftime('%d-%m-%Y'))
        return user_dates
    except ValueError:
        print('OB1LAB' + ' Проверьте правильность ввода дат')


def correct_date(date1, date2):
    date_check1 = re.findall(r'\d{2}-\d{2}-\d{4}', date1)
    date_check2 = re.findall(r'\d{2}-\d{2}-\d{4}', date2)
    if len(date_check1) > 0 and len(date_check2) > 0:
        return get_user_dates(date1, date2)
    else:
        print('OB1LAB' + 'Проверьте правильность ввода дат')


def log_file_download(url, date):
    url_download = '{0}{1}.txt'.format(url, date)
    log_download = requests.get(url_download).text
    file = 'logs/{0}.txt'.format(date)
    log_file = open(file, 'w', encoding='utf-8')
    log_file.write(log_download)
    log_file.close()


def logs_downloader(url, logs_dir, dates):
    if len(logs_dir) > 0:
        dates_sort = [datetime.strptime(day, '%d-%m-%Y') for day in logs_dir]
        dates_sort.sort()
        local_logs = [datetime.strftime(d, '%d-%m-%Y') for d in dates_sort]
        local_logs.pop(-1)
    else:
        local_logs = []
    for date in dates:
        if date not in local_logs:
            print('Скачиваем логи за {0}'.format(date))
            log_file_download(url, date)


def url_fix(url):
    if url[-1] != '/':
        url += '/'
    return url


def get_log_dates(url):
    dates = []
    request = requests.get(url).text
    log_dates = re.findall(r'\d{2}-\d{2}-\d{4}', request)
    for date in log_dates:
        if date not in dates:
            dates.append(date)
    return dates


def check_local_logs(url, user_dates):
    dir_path = os.listdir()
    if 'logs' not in dir_path:
        os.mkdir('logs')
    logs_in_dir = []
    skipped_dates = []
    logs_dir = os.listdir('logs')
    for log_file in logs_dir:
        logs_in_dir.append(log_file.split('.')[0])
    url = url_fix(url)
    access = requests.get(url).status_code
    if access == 200:
        dates = get_log_dates(url)
        for day in user_dates:
            if day not in dates:
                skipped_dates.append(day)
        if len(skipped_dates) > 0:
            print('Не найдены логи за:\n{0}'.format('\n'.join(skipped_dates)))
            return False
        logs_downloader(url, logs_in_dir, dates)
    else:
        print('Не удается получить доступ, докачайте логи вручную в "logs"')
        for date in user_dates:
            if date not in logs_in_dir:
                skipped_dates.append(date)
        if len(skipped_dates) > 0:
            print('Не найдены логи за:\n{0}'.format('\n'.join(skipped_dates)))
            return False
    return True


def start():
    table = PrettyTable()
    table.field_names = ['Ник', '[L]', '[G]', 'ls', 'warn', 'mute', 'kick',
                         'ban', 'Онлайн', 'Онлайн в ванише',
                         'Онлайн без ваниша',
                         'Средний онлайн', 'Средний онлайн без ваниша']
    players = ['Timberg', 'Sanyakhma', 'LoverTommy', 'AzazeIII']
    url = 'http://logs.s12.mcskill.ru/Hitechcraft2_public_logs/'
    date1 = '08-02-2021'
    date2 = '14-02-2021'
    user_dates = correct_date(date1, date2)
    if user_dates and check_local_logs(url, user_dates):
        for nick in players:
            table.add_row(check_activity(nick, user_dates))
        output_logs_txt = open('Output.txt', 'w')
        output_logs_txt.write(str(table))
        output_logs_txt.close()


if __name__ == '__main__':
    start()
