import requests
import re
from playwright.sync_api import sync_playwright

WEBHOOK_URL = "https://webhook.worksmobile.com/message/1f163fa9-b6ec-4de9-983d-4b44031a4800"
TARGET_URL = "https://waitwhile.com/locations/chromeheartshonolulu"

def send_line(text):
    requests.post(WEBHOOK_URL, json={"title": "CHホノルル予約", "body": {"text": text}})

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            # 1. トップページへアクセス
            page.goto(TARGET_URL, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(5000)
            print(f"[1] トップページURL: {page.url}")

            # 2. 「Schedule a booking」をクリック
            btn1 = page.get_by_text("Schedule a booking")
            print(f"[2] 'Schedule a booking' 要素数: {btn1.count()}")
            btn1.click()
            page.wait_for_timeout(3000)
            print(f"[2] クリック後URL: {page.url}")
            print(f"[2] クリック後の画面冒頭200文字: {page.locator('body').inner_text()[:200]}")

            # 3. 「Personal Shopping」を選択
            btn2 = page.get_by_text("Personal Shopping")
            print(f"[3] 'Personal Shopping' 要素数: {btn2.count()}")
            btn2.click()
            page.wait_for_timeout(3000)
            print(f"[3] クリック後URL: {page.url}")
            print(f"[3] クリック後の画面冒頭200文字: {page.locator('body').inner_text()[:200]}")

            # 4. 人数「2」を選択
            btn3 = page.get_by_text("2", exact=True)
            print(f"[4] '2'(人数) 要素数: {btn3.count()}")
            btn3.click()
            page.wait_for_timeout(5000)
            print(f"[4] クリック後URL: {page.url}")

            # 5. 空き枠判定・日付・時間抽出
            body_text = page.locator("body").inner_text()
            print(f"[5] 最終画面の全文（最大1500文字）:\n{body_text[:1500]}")

            if "No available times for the next 5 days" not in body_text:
                time_slots = page.locator("button:has-text('AM'), button:has-text('PM')").all_inner_texts()
                date_match = re.search(r'(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday),\s+[A-Za-z]+\s+\d+', body_text)
                date_str = date_match.group(0) if date_match else "日時選択画面にて空きあり"
                time_str = ", ".join(time_slots) if time_slots else "空き枠あり"

                msg = (
                    f"【CHホノルル店】事前予約の空き枠（2名）を検知しました！\n\n"
                    f"📅 日付: {date_str}\n"
                    f"⏰ 空き時間: {time_str}\n\n"
                    f"予約URL:\n{TARGET_URL}"
                )
                send_line(msg)
                print(f"空き枠検知: LINEへ通知送信\n{msg}")
            else:
                print("現在空き枠はありません。")

        except Exception as e:
            print(f"エラー発生: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    run()
