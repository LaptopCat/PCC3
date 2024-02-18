from aiohttp import ClientSession
from websockets import connect
from asyncio import wait_for
from orjson import loads, dumps as dump
from discord import Embed
import base64

dumps = lambda a:str(dump(a), "utf-8")

TIMEOUT = 10
SERVER = "api.creaty.me:44386"
SESSION_MANAGER = f"wss://{SERVER}/ws/sessionmanager"
FILE_STORAGE = f"https://{SERVER}/api/storage/pc-creator-two/Localizations/production.json"
HTTP_HEADERS = {"User-Agent": "UnityPlayer/2022.3.14f1 (UnityWebRequest/1.0, libcurl/7.80.0-DEV)", "X-Unity-Version": "2022.3.14f1"}
WS_HEADERS = {"User-Agent": "websocket-sharp/1.0"}

PUBLIC_PROMOCODE_LIST = [
  "X5XKEY",
  "R5RKEY",
  "LNY024",
]
LEADERBOARDS = {
  "PC Score": "PCPower",
  "Bitcoin": "BTC",
  "Ethereum": "ETH",
  "Dogecoin": "DOGE"
}
LEADERBOARD_TITLES = {
  1: "🥇",
  2: "🥈",
  3: "🥉"
}
LOADING = "<a:Loading:867450712887918632>"

ONLINE_USERS = "0"

TOKEN = ""

async def authed_post(*args, **kwargs):
  global TOKEN
  newHeaders = dict(HTTP_HEADERS)
  if "headers" in kwargs:
    newHeaders = kwargs["headers"]
  if TOKEN == "":
    TOKEN = await get_token()
  newHeaders["Authorization"] = "Bearer "+TOKEN
  kwargs["headers"] = newHeaders

  async with ClientSession() as session:
    while True:
      result = await session.post(*args, **kwargs)

      await result.text() # some things break without this for some reason haha
      #print(args, kwargs, TOKEN, result.status, await result.text())

      if result.status == 401:
        TOKEN = await get_token()
        newHeaders["Authorization"] = "Bearer "+TOKEN
      else:
        return result
  

async def get_trader(id="", code=""):
  result = await authed_post(f"https://{SERVER}/api/trading/trader/get", json={"traderID": id, "traderCode": code})

  if result.status != 204:
    return await result.json(loads=loads)

async def get_account(userid):
  async with ClientSession() as session:
    result = await session.get(f"https://{SERVER}/api/storage/pc-creator-two/PlayerSaves/{userid}.json?alt=media", headers=HTTP_HEADERS)

    return await result.json(loads=loads)

async def get_userid(email):
  async with ClientSession() as session:
    result = await session.post(f"https://us-central1-pc-creator-test.cloudfunctions.net/getUserUUID?email={email}")

    if result.status == 200:
      return await result.text()

async def get_token():
  async with ClientSession() as session:
      result = await session.post(f"https://{SERVER}/api/auth/token", json={
        "UserID": "pc-creator-2-discord-bot",
        "ProjectID": "pc-creator-two",
        "Country": "TV",
        "Version": "1.12.0"
      }, headers=HTTP_HEADERS)
      return (await result.json(loads=loads))["token"]

async def check_main_server():
  global ONLINE_USERS, TOKEN
  try:
    if TOKEN == "":
      TOKEN = await get_token()

    async with connect(SESSION_MANAGER, extra_headers=WS_HEADERS) as socket:
      await socket.send(dumps({"method": "authorize", "args": TOKEN}))
      async for msg in socket:
        break
      await socket.send(dumps({"method": "Subscribe"}))
      async for msg in socket:
        msg = loads(msg)
        ONLINE_USERS = str(msg["response"]["sessionCount"])
        await socket.close()
    return True
  except:
    return False

async def check_http(url):
  try:
    async with ClientSession() as session:
      result = await session.get(url, headers=HTTP_HEADERS)
    return result.status < 500 
  except:
    return False


async def get_lb(id, count=100):
  result = await authed_post(f"https://{SERVER}/api/leaderboard/get", json={"ID": id, "limit": count})

  return await result.json(loads=loads)

definitions = {
  FILE_STORAGE: {
    "name": "File Storage",
    "check": lambda: check_http(FILE_STORAGE)
  },
  SESSION_MANAGER: {
    "name": "Main Server",
    "check": check_main_server
  }
}


def format_msg(url, status):
  if status is True:
    data = f"✅ | {definitions[url]['name']} is online\n"
    if url == SESSION_MANAGER:
      data += f"\n{ONLINE_USERS} users online"
    return data
  if status is False:
    return f"❌ | {definitions[url]['name']} is down!\n"
  if status == "loading":
    return f"{LOADING} | Connecting to {definitions[url]['name']}...\n"

def bool_emoji(a):
    return "✅" if a else "❌"

def decrypt_currency(enc):
  try:
    return float(base64.b64decode(enc["_encryptedValue"]).decode())
  except:
    return 0.0

async def checker_wrapper(coro):
  try:
    return await wait_for(coro, timeout=TIMEOUT)
  except:
    return False


async def live_check(index, item, checks, response):
  definition = definitions[item]
  data = await checker_wrapper(definition["check"]())
  checks[index] = format_msg(item, data)
  await response.edit_original_message(
    embed=Embed(title="Status", description=''.join(checks).strip()))
  return
