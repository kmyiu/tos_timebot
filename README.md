# TOS Remove CurrentEvents Past Events Bot

> This is a small project on [TOS Wikia, Chinese version](https://tos.fandom.com/zh), , by administrator 
[Km14~](https://tos.fandom.com/zh/wiki/%E7%95%99%E8%A8%80%E5%A2%99:Km14~)

[Template:CurrentEvents](https://tos.fandom.com/zh/wiki/Template:CurrentEvents) contains a list of game events. Past events are hidden in desktop version but shown in mobile due to no js. This bot aims to remove past events and save in 
[Template:CurrentEvents2](https://tos.fandom.com/zh/wiki/Template:CurrentEvents2), and the mobile site will contains a link to view the
[reduced timetable](https://tos.fandom.com/zh/wiki/%E6%B4%BB%E5%8B%95%E6%99%82%E9%96%93%E8%A1%A8%E6%89%8B%E6%A9%9F%E7%89%88)

# Enviorment
`Python 3.6` with following packages installed
- `bs4` 
- `requests`
- `python_dateutil`

# General idea
A event is listed in the format of

`{{Event|xxxxxx
|2020/x/x |2020/x/x }}`
or 
`{{Event|xxxxxx
|2020/x/x}}`

Parse those events out and filter by their timestamp.