#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import yaml
from telepost import getPost, getImages, exitTelethon, getTelethonClient, genText
import plain_db
from opencc import OpenCC
import cached_url
cc = OpenCC('tw2sp')

existing = plain_db.load('existing')

with open('credential') as f:
    credential = yaml.load(f, Loader=yaml.FullLoader)

def isPromotion(line):
    if not line.strip():
        return True
    for starter in ['👉订阅', 'https://t.me/HKinternationalfront']:
        if line.strip().startswith(starter):
            return True
    return False

def stripPromotion(text):
    lines = text.split('\n')
    while lines:
        if isPromotion(lines[-1]):
            lines.pop()
        else:
            break
    return '\n'.join(lines).strip()

def addSource(text, key):
    return text + '\n\n来源： ' + key

async def send(client, channel, target, post, img_number, new_text):
    video = post.getVideo()
    if video:
        cached_url.get(video, mode='b', force_cache=True)
        await client.send_message(target, new_text, file = cached_url.getFilePath(video))
        return
    if not img_number:
        await client.send_message(target, new_text)
        return
    fns = await getImages(channel, post.post_id, img_number)
    await client.send_message(target, new_text, file = fns)

async def simplifyOne(client, target):
    channel = credential['source_group']
    post = getPost(channel, existing, min_time=1)
    key = 'https://t.me/' + post.getKey()
    img_number = post.getImgNumber()
    text = await genText(channel, post.post_id)
    mid_text = stripPromotion(cc.convert(text))
    new_text = addSource(mid_text, key)
    try:
        await send(client, channel, target, post, img_number, new_text)
    except:
        await send(client, channel, target, post, img_number, mid_text)
    existing.update(key, 1)

async def simplify():
    client = await getTelethonClient()
    await client.get_dialogs()
    target = await client.get_entity(credential['target_group'])
    try:
        for _ in range(3):
            await simplifyOne(client, target)
    except Exception as e:
        print(e)
    print('here')
    await exitTelethon()
    
if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    r = loop.run_until_complete(simplify())
    loop.close()