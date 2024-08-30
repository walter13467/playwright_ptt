from playwright.sync_api import sync_playwright

def run(playwright):
    # 啟動瀏覽器
    browser = playwright.chromium.launch(headless=False)  # headless=False 會顯示瀏覽器窗口
    page = browser.new_page()
    
    # 打開 Google 首頁
    page.goto("https://www.google.com")
    
    # 檢查頁面標題是否包含 "Google"
    title = page.title()
    print(f"Page title: {title}")
    assert "Google" in title
    
    # 關閉瀏覽器
    browser.close()

with sync_playwright() as playwright:
    run(playwright)
