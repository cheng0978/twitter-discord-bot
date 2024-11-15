import os
from discord.ext import commands, tasks
import discord
from dotenv import load_dotenv
import tweepy

# 載入環境變數
load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")  # 使用 API v2 的 Bearer Token
DISCORD_CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))
TWITTER_USER_HANDLE = os.getenv("TWITTER_USER_HANDLE")

# 設定 Twitter API v2
twitter_client = tweepy.Client(bearer_token=TWITTER_BEARER_TOKEN)

# Discord Bot 設定
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# 記錄最新推文 ID
last_tweet_id = None

@tasks.loop(minutes=5)  # 每 1 分鐘檢查一次
async def check_tweets():
    global last_tweet_id

    try:
        # 使用 API v2 獲取最新推文
        user = twitter_client.get_user(username=TWITTER_USER_HANDLE)
        tweets = twitter_client.get_users_tweets(user.data.id, max_results=5)

        if tweets.data:
            latest_tweet = tweets.data[0]
            if last_tweet_id is None or latest_tweet.id > last_tweet_id:
                last_tweet_id = latest_tweet.id
                channel = bot.get_channel(DISCORD_CHANNEL_ID)
                if channel:
                    tweet_url = f"https://twitter.com/{TWITTER_USER_HANDLE}/status/{latest_tweet.id}"
                    await channel.send(f"📢 新推文！\n🔗 {tweet_url}")

    except Exception as e:
        print(f"錯誤：{e}")

@bot.event
async def on_ready():
    print(f"已登入為 {bot.user}")
    check_tweets.start()  # 啟動背景任務

# 啟動機器人
bot.run(DISCORD_TOKEN)
