import os
import discord
from discord import app_commands
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import tempfile
import os
import time

# インテントの設定
intents = discord.Intents.default()
class MyClient(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()

client = MyClient()

# HTMLをスクリーンショットとして保存する関数
def html_to_screenshot(html_content):
    # Chromeのオプション設定
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')

    # 一時ファイルの作成
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
        f.write(html_content)
        temp_path = f.name

    # Chromeドライバーの初期化
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # HTMLファイルを開く
        driver.get(f'file://{temp_path}')
        time.sleep(2)  # レンダリング待機

        # スクリーンショットを撮影
        screenshot_path = f"{temp_path}.png"
        driver.save_screenshot(screenshot_path)
        
        return screenshot_path
    finally:
        driver.quit()
        os.remove(temp_path)

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

@client.tree.command(name="steam", description="SteamウィジェットのHTMLコードを画像として表示します")
@app_commands.describe(htmlcode="SteamウィジェットのHTMLコードを入力してください")
async def steam(interaction: discord.Interaction, htmlcode: str):
    try:
        # 応答を遅延
        await interaction.response.defer()
        
        # HTMLコンテンツをスクリーンショットに変換
        screenshot_path = html_to_screenshot(htmlcode)
        
        # スクリーンショットを送信
        await interaction.followup.send(file=discord.File(screenshot_path))
        
        # スクリーンショットファイルの削除
        os.remove(screenshot_path)
        
    except Exception as e:
        await interaction.followup.send(f'エラーが発生しました: {str(e)}')

client.run(os.getenv('DISCORD_TOKEN'))
