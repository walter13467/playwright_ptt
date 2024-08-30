from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import pandas as pd

url = "https://www.ptt.cc/bbs/Gossiping/index.html"
num_page = 3

def playwright(url):
    print(url)
    with sync_playwright() as p:
        # 啟動瀏覽器
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        # 設置 cookie
        context.add_cookies([{
            'name': 'over18',
            'value': '1',
            'domain': '.ptt.cc',
            'path': '/'
        }])

        articles = []
        for p in range(num_page):
            # 訪問 PTT 八卦版（需同意18歲以上進入）
            page.goto(url)
            # page.click("text=我同意，我已年滿十八歲")

            # 等待首頁加載完成
            page.wait_for_load_state("load")
            
            # 獲取首頁文章列表
            page_content = page.content()
            soup = BeautifulSoup(page_content, "lxml")

            articles.append(fetch_page_list(soup,articles))

            controls = soup.select(".action-bar a.btn.wide")[1]
            next_page_url = parse_next_link(controls)
            url = next_page_url
            print("url:",url)
    
        articles = fetch_page_content(page,articles)

        browser.close()

    return articles

def parse_next_link(controls):
    
    link = controls.attrs['href']
    next_page_url = 'https://www.ptt.cc' + link
    return next_page_url

def fetch_page_list(soup,articles):
    # 獲取每篇文章的標題與鏈接
    for entry in soup.select(".r-ent"):     #r-ent是文章
        title_tag = entry.select_one(".title a")    
        if title_tag:
                title = title_tag.text.strip()      #strip()清除空白換行
                link = "https://www.ptt.cc" + title_tag['href']
                push_num = entry.select_one(".nrec").text
                articles.append({"title": title, "push_num": push_num ,"link": link})
    return articles

def fetch_page_content(page,articles):
    # 爬取每篇文章的內文與推文
    for article in articles:
        page.goto(article["link"])
        post_content = page.content()
        post_soup = BeautifulSoup(post_content, "lxml")
        
        # 文章內文
        main_content = post_soup.select_one("#main-content")
        content_text = main_content.get_text().split("--")[0].strip()  # 內文
        
        # 推文
        comments = []
        for comment in post_soup.select(".push"):
            push_tag = comment.select_one(".push-tag").text.strip()
            push_userid = comment.select_one(".push-userid").text.strip()
            push_content = comment.select_one(".push-content").text.strip()[1:].strip()
            comments.append({
                "tag": push_tag,
                "userid": push_userid,
                "content": push_content
            })
        
        article["content"] = content_text
        article["comments"] = comments

    return articles

# 執行並打印結果
if __name__ == "__main__":
    url = "https://www.ptt.cc/bbs/Gossiping/index.html"
    num_page = 3
    articles = playwright(url)
    for article in articles:
        print(f"Title: {article['title']}")
        print(f"Push_num: {article['push_num']}")
        print(f"Content: {article['content']}")
        print("Comments:")
        for comment in article['comments']:
            print(f"{comment['tag']} {comment['userid']}: {comment['content']}")
        print("="*80)
    
    df = pd.DataFrame(articles)
    df.to_csv('output.csv', index=False, encoding='utf-8-sig')
