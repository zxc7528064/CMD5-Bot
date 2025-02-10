import discord  # 導入 Discord 機器人 SDK
import requests  # 用來發送 HTTP 請求到 CMD5 API
import re  # 用來驗證哈希值格式

# Discord Bot Token（請填入你的機器人 Token）
TOKEN = "修改 discord bot token"

# CMD5 API 相關參數（支援 MD5, SHA-1, SHA-256, SHA-512, MySQL, MySQL5）
CMD5_EMAIL = "修改"
CMD5_KEY = "修改"
CMD5_API_URL = "http://www.cmd5.com/api.ashx"

# 啟用 intents，並開啟 message_content 權限
intents = discord.Intents.default()  # 使用預設的機器人權限
intents.message_content = True  # 啟用讀取訊息內容的權限
client = discord.Client(intents=intents)  # 初始化 Discord 機器人

# 正則表達式，匹配 16~128 個 16 進位字母或數字（用來檢測是否為哈希值）
HASH_REGEX = re.compile(r"^[a-fA-F0-9]{16,128}$")

# CMD5 API 錯誤代碼對應訊息
CMD5_ERROR_CODES = {
    "CMD5-ERROR:0": "❌ 解密失敗",
    "CMD5-ERROR:-1": "🚫 無效的用戶名或密碼",
    "CMD5-ERROR:-2": "⚠️ 餘額不足，請充值",
    "CMD5-ERROR:-3": "🛑 解密服務器故障",
    "CMD5-ERROR:-4": "❓ 不識別的密文",
    "CMD5-ERROR:-7": "❌ 不支持的哈希類型",
    "CMD5-ERROR:-8": "⛔ API 權限被禁止",
    "CMD5-ERROR:-9": "⚠️ 查詢超過 100 次",
    "CMD5-ERROR:-999": "❌ 其他錯誤"
}

def identify_hash(hash_value):
    """
    判斷哈希值類型：
    - 若符合 HASH_REGEX (16~128 個 16 進位字母或數字)，則視為可查詢的哈希
    - 讓 CMD5 API 自動識別哈希類型
    """
    if HASH_REGEX.match(hash_value):
        return "auto"  # 讓 CMD5 自動識別
    return None  # 不符合哈希格式，回傳 None

async def query_hash(hash_value):
    """
    發送請求到 CMD5 API 進行哈希解密：
    1. 透過 HTTP GET 方法傳遞 `email`、`key` 及 `hash` 至 CMD5 API
    2. 若 API 回應 200，檢查是否回傳錯誤代碼
    3. 若為錯誤代碼，則返回對應的錯誤訊息
    4. 若無錯誤，則回傳解密結果
    """
    params = {
        "email": CMD5_EMAIL,
        "key": CMD5_KEY,
        "hash": hash_value  # 讓 CMD5 自動識別哈希類型
    }
    
    response = requests.get(CMD5_API_URL, params=params)  # 發送 GET 請求至 CMD5 API

    if response.status_code == 200 and response.text:  # API 回應成功
        result = response.text.strip()  # 去除回應的前後空白字符
        
        # 如果 API 回應是錯誤代碼，返回詳細錯誤信息
        if result.startswith("CMD5-ERROR"):
            return CMD5_ERROR_CODES.get(result, "⚠️ 未知錯誤：" + result)
        
        # 否則返回解密結果
        return result
    else:
        return "⚠️ CMD5 API 無法連接，請稍後再試"

@client.event
async def on_ready():
    """
    當機器人成功啟動時觸發此事件
    - 顯示機器人已上線的訊息
    """
    print(f'✅ 機器人 {client.user} 已上線！')

@client.event
async def on_message(message):
    """
    當機器人接收到訊息時觸發此事件：
    1. 檢查訊息是否來自機器人本身，若是則忽略
    2. 讀取訊息內容，判斷是否為哈希值
    3. 若為哈希值，則發送查詢請求給 CMD5 API
    4. 回應解密結果給 Discord 頻道
    """
    if message.author == client.user:
        return  # 忽略機器人自己的訊息

    hash_value = message.content.strip()  # 取得用戶發送的訊息，去除前後空白
    hash_type = identify_hash(hash_value)  # 判斷是否為哈希值

    if hash_type:  # 若訊息為合法哈希值
        await message.channel.send(f"🔍 正在查詢 `{hash_value}`，讓 CMD5 自動識別...")
        result = await query_hash(hash_value)  # 呼叫 CMD5 API 進行解密
        await message.channel.send(f"📝 結果: `{result}`")  # 回傳解密結果
    else:
        await message.channel.send("❌ 只支援 MD5、SHA-1、SHA-256、SHA-512、MySQL、MySQL5 哈希，請輸入正確的哈希值")

# 啟動 Discord 機器人
client.run(TOKEN)
