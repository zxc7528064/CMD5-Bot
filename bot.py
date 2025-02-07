import discord
import requests
import re  # 用來驗證哈希值

TOKEN = "Discord機器人token"
CMD5_EMAIL = "修改成Gmail"
CMD5_KEY = "修改成CMD5_Key"
CMD5_API_URL = "http://www.cmd5.com/api.ashx"

# 啟用 intents，並開啟 message_content 權限
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# 定義哈希值正則表達式（只允許 32 位 MD5）
HASH_REGEX = re.compile(r"^[a-fA-F0-9]{32}$")

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

@client.event
async def on_message(message):
    print(f"收到訊息: {message.content}")  # 方便排查問題

    if message.author == client.user:
        return  # 不回應自己的訊息

    # **如果訊息是 MD5 哈希值，則自動查詢**
    if HASH_REGEX.match(message.content):
        hash_value = message.content.strip()
        await message.channel.send(f"正在查詢 `{hash_value}`...")

        # 發送 CMD5 API 請求
        params = {"email": CMD5_EMAIL, "key": CMD5_KEY, "hash": hash_value}
        response = requests.get(CMD5_API_URL, params=params)

        print(f"CMD5 API 回應: {response.text}")  # 記錄 API 回應內容

        if response.status_code == 200:
            result = response.text.strip()
            if "CMD5-ERROR" in result:
                await message.channel.send(f"解密失敗: `{result}`")
            else:
                await message.channel.send(f"哈希 `{hash_value}` 的明文為： `{result}`")
        else:
            await message.channel.send("無法連接 CMD5 API，請稍後再試。")

client.run(TOKEN)
