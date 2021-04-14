#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import yaml
from telepost import getPost, getImages, exitTelethon, getTelethonClient, genText
import plain_db
from opencc import OpenCC
cc = OpenCC('hk2s')

existing = plain_db.load('existing')

with open('credential') as f:
    credential = yaml.load(f, Loader=yaml.FullLoader)

def stripPromotion(text):
    lines = text.split('\n')
    while lines:
        if lines[-1].startswith('👉訂閱'):
            lines.pop()
        else:
            break
    return '\n'.join(lines).strip()

def addSource(text, channel, post_id):
    return text + '\n\n来源： ' + channel + '/' + str(post_id) 

async def simplifyOne(target):
    channel = credential['source_group']
    post = getPost(channel, existing, min_time=1)
    img_number = post.getImgNumber()
    text = await genText(channel, post.post_id)
    print(text)
    new_text = stripPromotion(cc.convert(text))
    new_text = addSource(new_text, channel, post.post_id)
    if post.getVideo():
        print('WARNING VIDEO')
        return
    if not img_number:
        await client.send_messages(target, new_text)
    fns = await getImages(channel, post.post_id, img_number)
    await client.send_messages(target, new_text, file = fns)

async def simplify():
    client = await getTelethonClient()
    await client.getDialogs()
    target = await client.get_entity(credential['target_group'])
    while True:
        simplifyOne(target)
    await exitTelethon()
    
if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    r = loop.run_until_complete(simplify())
    loop.close()