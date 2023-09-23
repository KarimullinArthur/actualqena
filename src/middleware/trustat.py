import asyncio
import traceback
from typing import List

import aiohttp
from loader import db


class TrustatApi:
    def __init__(self):
        self.session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False))
        self.API_URL = "https://api.trustat.ru/"

    async def get_channel_views(self, channel_id: int):
        url = self.API_URL + "channel/views/"
        async with self.session.get(url, params={"channel_id": channel_id}) as response:
            data = await response.json()
        if "Not Found" in data:
            return False
        else:
            return data['views']

    async def get_channel(self, channel_id: int, link=None):
        url = self.API_URL + "channel/"
        async with self.session.get(url, params={"channel_id": channel_id}) as response:
            data = await response.json()
        if "Not Found" in data:
            return False
        else:
            if link:
                data.append(link)
            return data

    async def get_channels_with_link(self, channel_data: dict):
        tasks = []
        for key, value in channel_data.items():
            link = key
            channel_id = value
            task = self.get_channel(channel_id, link)
            tasks.append(task)
        resp = await asyncio.gather(*tasks)
        return resp

    async def get_channels_views(self, channels: List[int]):
        try:
            if not channels:
                return 0, []
            found_channels = []
            views = 0

            url = self.API_URL + "channel/views/"
            async with self.session.get(url, params={"channels": ','.join(map(str, channels))}) as response:
                data = await response.json()

            if data == "Not Found":
                return 0, []
            for channel in data:
                views += channel['views']
                found_channels.append(channel['cid'])

            await self.session.close()
            set1 = set(channels)
            set2 = set(found_channels)

            result_set = set1.difference(set2)

            not_found_channels = list(result_set)
            return views, not_found_channels
        except Exception as e:
            print(e)
            print(traceback.format_exc())

    async def add_channels(self, channel_links: str):
        url = self.API_URL + "channel/add"
        async with self.session.post(url, json={"channel_links": channel_links}) as response:
            data = await response.json()
        if "detail" in data and data["detail"][0]["msg"] != "Successful Response":
            return None
        else:
            return data

    async def get_task_status(self, task_id: int):
        url = self.API_URL + "tasks/{}".format(task_id)
        async with self.session.get(url) as response:
            data = await response.json()
        if "detail" in data and data["detail"][0]["msg"] != "Successful Response":
            return "Error"
        else:
            return data

    async def run_task_check(self, task_id: int):
        ATTEMPTS_LIMIT = 100
        attempts = 0
        while ATTEMPTS_LIMIT >= attempts:
            task = await self.get_task_status(task_id)
            task_status = task['status']
            if task_status != "processing" and task_status != 'waiting':
                return task
            attempts += 1
            await asyncio.sleep(1)

    async def close(self):
        await self.session.close()


async def get_form(tg_id: int):
    trustat = TrustatApi()
    link = db.get_link(tg_id)

    await trustat.add_channels(', '.join(link['links']))
    task_id = await trustat.add_channels(', '.join(link['links']))
    await trustat.get_task_status(task_id['task_id'])
    await trustat.run_task_check(task_id['task_id'])
    data = await trustat.get_task_status(task_id['task_id'])

    result = ''
    for channel in data['result']:
        result += f'''
<a href='{channel['link']}'>{channel['title']}</a>
Пдп👥 {channel['participant_count']}
Охват👁 {channel['views_24']}
ER📈 {channel['er']}
'''
    if len(data['result']) != 1:
        result += '''
Всего подписчиков👥
Общий охват👁

'''
    result += f"Купить рекламу {link['username']}"
    await trustat.close()
    return result
