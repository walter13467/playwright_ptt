from playwright.sync_api import sync_playwright

def run(playwright):
    # 啟動瀏覽器
    browser = playwright.chromium.launch(headless=False)  # headless=False 會顯示瀏覽器窗口
    context = browser.new_context()
    page = context.new_page()
    
    # 設置 cookie
    context.add_cookies([{
        'name': 'over18',
        'value': '1',
        'domain': '.ptt.cc',
        'path': '/'
    }])
    
    # 打開 PTT 八卦版
    page.goto("https://www.ptt.cc/bbs/Gossiping/index.html")
    
    # 如果需要點擊 "我同意" 按鈕
    # page.click('button:has-text("我同意")')
    
    # 等待一段時間以便觀察結果
    page.wait_for_timeout(5000)
    
    # 關閉瀏覽器
    browser.close()

with sync_playwright() as playwright:
    run(playwright)