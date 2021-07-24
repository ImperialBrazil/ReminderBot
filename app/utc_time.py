import math


def time_operation(local_time: str, utc_code: str, monday: bool, tuesday: bool, wednesday: bool, thursday: bool,
                   friday: bool, saturday: bool, sunday: bool):
    days = [monday, tuesday, wednesday, thursday, friday, saturday, sunday]
    t = ''
    for y in days:
        t += str(int(y)) + '|'
    local_days = t[0:-1]
    minutes = int(local_time[3:5]) + 60 * int(local_time[0:2])
    utc_minutes = int(utc_code[4:6]) + 60 * int(utc_code[1:3])
    if utc_code[0] == '+':
        minutes_ = minutes - utc_minutes
    else:
        minutes_ = minutes + utc_minutes
    #
    hours_ = math.floor(minutes_ / 60)
    minutes_ = minutes_ - hours_ * 60
    #
    if hours_ < 0:
        hours_ = hours_ + 24
        monday_ = days[0]
        for y in range(0, 6):
            days[y] = days[y + 1]
        days[6] = monday_
    elif hours_ > 23:
        hours_ = hours_ - 24
        sunday_ = days[6]
        for y in range(6, 0, -1):
            days[y] = days[y - 1]
        days[0] = sunday_
    #
    if hours_ < 10:
        hours_ = '0' + str(hours_)
    if minutes_ < 10:
        minutes_ = '0' + str(minutes_)
    time = str(hours_) + ':' + str(minutes_)
    #
    t = ''
    for y in days:
        t += str(int(y)) + '|'
    days_ = t[0:-1]
    return time, local_days, days_
