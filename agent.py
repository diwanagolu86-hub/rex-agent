import os
import sys
import asyncio
import json
from playwright.async_api import async_playwright
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Config
DRIVE_FOLDER_ID = os.environ["DRIVE_FOLDER_ID"]
CMD_VAL = os.environ["CMD_VAL"] # HF se aayega
JOB_ID = os.environ["JOB_ID"]   # Unique ID

def get_drive_service():
    creds_json = json.loads(os.environ["G_DRIVE_CREDS"])
    creds = service_account.Credentials.from_service_account_info(creds_json)
    return build('drive', 'v3', credentials=creds)

async def run():
    print(f"🚀 Processing: {CMD_VAL}")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_context(viewport={'width':1280,'height':720})
        page = await page.new_page()
        
        try:
            # Action Logic
            if "http" in CMD_VAL:
                await page.goto(CMD_VAL, timeout=60000)
            
            # Screenshot
            filename = f"result_{JOB_ID}.png"
            await page.screenshot(path=filename)
            print("📸 Screenshot taken!")
            
            # Upload to Drive
            service = get_drive_service()
            meta = {'name': filename, 'parents': [DRIVE_FOLDER_ID]}
            media = MediaFileUpload(filename, mimetype='image/png')
            service.files().create(body=meta, media_body=media).execute()
            print("✅ Uploaded to Drive")
            
        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            await browser.close()

asyncio.run(run())


