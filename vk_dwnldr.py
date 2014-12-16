#!/usr/bin/env python3

import vk_auth
import getpass
import json
import urllib.request, urllib.error, urllib.parse
from urllib.parse import urlencode
import os

def callApi(method, params, token):
    if isinstance(params, list):
        params_list = [kv for kv in params]
    elif isinstance(params, dict):
        params_list = list(params.items())
    else:
        params_list = [params]
    params_list.append(("access_token", token))
    url = "https://api.vk.com/method/%s?%s" % (method, urlencode(params_list))
    try:return json.loads(urllib.request.urlopen(url).read().decode('utf-8'))["response"]
    except:return [6,{},{}]

def dumpMessages(f, msgs, startNum = 1):
    O = startNum
    for msg in msgs[1:]:
        O += 1
        qual=['src_xxxbig', 'src_xbig', 'src_xxbig', 'src_big', 'src', 'src_small']
        try:
            if msg['attachments']:
                for i in range(len(msg['attachments'])):
                    for j in qual:
                        try:
                            if msg['attachments'][i]['photo']:
                                f.write(str(msg['attachments'][i]['photo'][j]) + "\n")
                            else: break
                        except: pass
                        else: break
            else:
                if msg['attachment']['photo']:
                    for j in qual:
                        try: f.write(str(msg['attachment']['photo'][j]) + "\n")
                        except: pass
                        else: break
                else: continue
        except: pass

if __name__ == "__main__":
    email = input("Email: ")
    password = getpass.getpass()
    APP_ID="4589651"
    token, user_id = vk_auth.auth(email, password, APP_ID, "messages")

    dumpMore = 'y'
    while dumpMore == 'y':
        UID = input("Target user ID: ")
        first200 = callApi("messages.getHistory", [("uid", UID), ("count", "200"), ("rev", "1"), ("offset", "0")], token)
        fullCount = int(first200[0])

        Folder = ("dump_dialog_%s" % UID) #Создаем папку "dump_dialog_№№"
        if Folder and not os.path.exists(Folder):
            os.makedirs(Folder) 

        dia_path = os.path.join(Folder or "", "dump_dialog_%s.txt" % UID)

        with open(dia_path, "w") as f: #В файл "dump_dialog_№№.txt" записываем ссылки на фотографии
            dumpMessages(f, first200)
            receivedCount = len(first200) - 1
            while receivedCount < fullCount:
                print("Dumped %d / %d" % (receivedCount, fullCount))
                next200 = callApi("messages.getHistory", [("uid", UID), ("count", "200"), ("rev", "1"), ("offset", str(receivedCount))], token)
                dumpMessages(f, next200, startNum = receivedCount + 1)
                receivedCount += len(next200) - 1
            print("Dumped %d / %d" % (receivedCount, fullCount))
        print("Finished dumping chat with user %s" % UID)

        with open(dia_path, "r") as dumpLinks: #Скачиваем фотографии по ссылкам из "dump_dialog_№№.txt"
            #print("Found %d photos" % sum(1 for _ in dumpLinks))
            file_num = 0
            for href in dumpLinks:
                try:
                    t_name = str(file_num+1)+'.jpg'
                    t_path = os.path.join(Folder or "", t_name)
                    urllib.request.urlretrieve(href, t_path)
                    file_num += 1
                    print ("Downloaded %s files" % str(file_num))
                except:pass
        with open(dia_path, "r") as f:
            print("Saved %s / %s photos" % (str(file_num),str(sum(1 for _ in f))))
        print("Finished saving chat with user %s" % UID)
        dumpMore = input("Do you want to dump one more chat? (y/n) ")

    print("Goodbye!")