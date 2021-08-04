# ReminderBot
A Reminder Bot for Telegram on aiogram and sqlite3

https://t.me/Alarm_Notification_Reminder_Bot

 ![alt text](https://i.imgur.com/JtcHwix.png)

## Commands
- [/set_reminder](https://github.com/coder8jedi/ReminderBot#set-reminder) - create new reminder
- [/my_reminders](https://github.com/coder8jedi/ReminderBot#my-reminders) - print your reminders
- [/del_reminder](https://github.com/coder8jedi/ReminderBot#del-reminder) - delete reminder
- [/edit_reminder](https://github.com/coder8jedi/ReminderBot#edit-reminder) - edit reminder
- [/cancel](https://github.com/coder8jedi/ReminderBot#cancel) - cancel
- [/utc](https://github.com/coder8jedi/ReminderBot#utc) - change time zone
- [/lang](https://github.com/coder8jedi/ReminderBot#lang) - change interface language
- [/help](https://github.com/coder8jedi/ReminderBot#start--help) - print a list of commands

## File Tree
<details>
<summary>OPEN</summary>

```
├── app/
│ ├── handlers/
│ │ ├── __init__.py
│ │ ├── common.py
│ │ ├── del_reminder.py
│ │ ├── edit_reminder.py
│ │ ├── lang.py
│ │ ├── my_reminder.py
│ │ ├── set_reminder.py
│ │ └── utc.py
│ ├── __init__.py
│ ├── config_reader.py
│ ├── keyboards.py
│ ├── localization.py
│ ├── remiders_run.py
│ └── utc_time.py
├── config/
│ └── bot.ini
├── localization/
│ ├── en.txt
│ └── uk.txt
├── bot.py
└── data.db
```
 
</details>


### Start & Help
```/help``` - print a list of commands

![alt text](https://i.imgur.com/Ywc05uW.gif)

### Set Reminder
```/set_reminder``` - create new reminder

![alt text](https://i.imgur.com/aEQz8Bo.gif)

### My Reminders
```/my_reminders``` - print your reminders

![alt text](https://i.imgur.com/cfiUfYH.gif)

### Del Reminder
```/del_reminder``` - delete reminder

![alt text](https://i.imgur.com/t9HFkdK.gif)

### Edit Reminder
```/edit_reminder``` - edit reminder

![edit_reminder](https://i.imgur.com/rlpcEiu.gif)

### Cancel
```/cancel``` - cancel command where there is not cancel button

![alt text](https://i.imgur.com/yZcm9JC.gif)

### UTC
```/utc``` - change time zone

![alt text](https://i.imgur.com/gPGvsKA.gif)

### Lang
```/lang``` - change inteface language

![alt text](https://i.imgur.com/5irLaIq.gif)
