#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import os
lgname = os.environ['lgname']
lgpassword = os.environ['lgpassword']


# In[ ]:


def wiki_login(session):
    url = "https://tos.fandom.com/zh/api.php"
    params_login = {
        "action": "login",
        "lgname": lgname,
        "format": "json"
    }
    r = session.post(url, data=params_login)
    lgtoken = r.json()['login']['token']

    params_login = {
        "action": "login",
        "lgname": lgname,
        "lgpassword": lgpassword,
        "lgtoken" : lgtoken,
        "format": "json"
    }
    r = session.post(url, data=params_login)
    return r.json()['login']['result'] == 'Success'


# In[ ]:


def wiki_edit(session, new_text):  
    url = "https://tos.fandom.com/zh/api.php"
    params_edittoken = {
        "action": "query",
        "prop": "info",
        "intoken": "edit",
        "titles": "Template:CurrentEvents2",
        "format": "json"
    }
    r = session.post(url, data=params_edittoken)
    r.json()
    pageid = list(r.json()['query']['pages'].keys())[0]
    edittoken = r.json()['query']['pages'][pageid]['edittoken']
    params_edit = {
        "action": "edit",
        "title": "Template:CurrentEvents2",
        "text": new_text,
        "format": "json",
        "token": edittoken
    }
    r = session.post(url, data=params_edit) 
    print(r.json())
    return r.json()['edit']['result']


# In[ ]:


def clean_html(raw_html):
    import re
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext

def get_timetable_text(session):
    from requests import Session
    from bs4 import BeautifulSoup as bs
    CurrentEvents = session.get("https://tos.fandom.com/zh/wiki/Template:CurrentEvents?action=edit")
    CurrentEventsOriginalText = bs(CurrentEvents.content, "html.parser")
    CurrentEventsOriginalText = CurrentEventsOriginalText.find("div", {"id": "editarea"}).find("textarea")
    return clean_html(CurrentEventsOriginalText.text)

def get_timetable_text_cur(session):
    import re
    timetable_text = remove_comments(get_timetable_text(session))
    blocks_valid = remove_ended_event(timetable_text)
#     remove duplicate newlines
    timetable_text_cur = ''.join(blocks_valid)
    timetable_text_cur = re.sub(r'(\n\s*)+\n+', '\n\n', timetable_text_cur)
    return timetable_text_cur


# In[ ]:


def parse_texttime_to_datetime(time_str, end_of_day):
    from dateutil import parser as time_parser
    import datetime
    import re
    time_str = "".join(re.split("}", time_str, flags=re.DOTALL))
    try:
        time = time_parser.parse(time_str)
        if end_of_day:
            if time.hour == 0 and time.minute == 0:
                time += datetime.timedelta(hours = 23, minutes = 59, seconds = 0)
        return time
    except ValueError:
        return None


# In[ ]:


def check_event_ended(event_start, event_end):
    import datetime
    time_now = datetime.datetime.utcnow()
    event_end = event_end - datetime.timedelta(hours = 8)
    event_end += datetime.timedelta(hours = 0, minutes = 1, seconds = 0)
    if event_end <= time_now:
        return True
    else:
        return False


# In[ ]:


def remove_comments(s):
    import re
    return "".join(re.sub("<!--(.*?)-->", "", s, flags=re.DOTALL))


# In[ ]:


def remove_ended_event(s):
    import re
    curly_cnt = 0
    parse_ok = True
    length = len(s)
    block_start = 0
    block_end = 0
    block_ended = True
    blocks = list()
    for i in range(length):
        if(block_ended == True and curly_cnt == 0):
            block_start = i
            block_ended = False
        if(s[i] == '{'):
            curly_cnt += 1
        if(s[i] == '}'):
            curly_cnt -= 1
            if(curly_cnt < 0):
                parse_ok = False
            if(curly_cnt == 0):
                block_end = i
                block_ended = True
                blocks.append(s[block_start:block_end+1])
    if curly_cnt != 0:
        parse_ok = False
    if parse_ok:
        blocks_valid = list()
        for block_str in blocks:
#             EventSection does not have time
            if(re.search("{{EventSection[|](.*)}}", block_str, flags=re.DOTALL) == None):
#                 print(block_str)
                block_paramsplit = re.split("[|]", block_str, flags=re.DOTALL)
                event_start = None
                event_end = None
                event_ended = False
                if len(block_paramsplit) == 1:
                    event_start = parse_texttime_to_datetime(block_paramsplit[-1], False)
                    event_end = parse_texttime_to_datetime(block_paramsplit[-1], True)
                elif len(block_paramsplit) > 1:
                    event_start = parse_texttime_to_datetime(block_paramsplit[-2], False)
                    event_end = parse_texttime_to_datetime(block_paramsplit[-1], True)
#                 print(event_start)
#                 print(event_end)
                if(event_start != None and event_end != None):
                    event_ended = check_event_ended(event_start, event_end)
                if event_ended == False:
                    blocks_valid.append(block_str)
            else:
                 blocks_valid.append(block_str)   
    return blocks_valid


# In[ ]:


def main():
    import time
    from requests import Session
    loop_cnt = 0
    session = Session()
    while True:
        print('Looping...' + str(loop_cnt))
        if loop_cnt == 20:
            loop_cnt = 0
            session = Session()
        try:
            if loop_cnt == 0:
                login_success = wiki_login(session)
            if login_success:
                print('Login success...')
                timetable_text_cur = get_timetable_text_cur(session)
                if timetable_text_cur:
                    print('Checking timetable...')
                    wiki_edit(session, timetable_text_cur)
                    print('Checking timetable done...')
        except:
            pass
        time.sleep(60)
        loop_cnt = loop_cnt + 1


# In[10]:


if __name__ == "__main__":
    main()

