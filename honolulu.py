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
            page.goto(TARGET_URL, wait_until="networkidle", timeout=60000)
            page.wait_for_timeout(3000)

            # 2. 「Schedule a booking」をクリック
            page.get_by_text("Schedule a booking").click()
            page.wait_for_timeout(2000)

            # 3. 「Personal Shopping」を選択
            page.get_by_text("Personal Shopping").click()
            page.wait_for_timeout(2000)

            # 4. 人数「2」を選択
            page.get_by_text("2", exact=True).click()
            page.wait_for_timeout(4000)

            # 5. 空き枠判定・日付・時間抽出
            body_text = page.locator("body").inner_text()

            if "No available times for the next 5 days" not in body_text:
                # 画面上の時間帯ボタン（例: 4:30 PM）を取得
                time_slots = page.locator("button:has-text('AM'), button:has-text('PM')").all_inner_texts()
                
                # 日付表記（例: Saturday, Sep 19）を抽出
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
