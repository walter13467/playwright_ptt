from playwright.sync_api import sync_playwright
import asyncio
from bs4 import BeautifulSoup
import pandas as pd

url = "https://www.ptt.cc/bbs/Gossiping/index.html"
num_page = 3

def playwright(url):
    print(url)
    with sync_playwright() as p:
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
        for _ in range(num_page):
            # 訪問 PTT 八卦版
            page.goto(url)
            page.wait_for_load_state("load")
            
            # 獲取首頁文章列表
            page_content = page.content()
            soup = BeautifulSoup(page_content, "lxml")
            fetch_page_list(soup, articles)

            controls = soup.select(".action-bar a.btn.wide")[1]
            url = parse_next_link(controls)
            print("url:", url)
    
        fetch_page_content(page, articles)
        browser.close()

    return articles

def parse_next_link(controls):
    link = controls.attrs['href']
    next_page_url = 'https://www.ptt.cc' + link
    return next_page_url

def fetch_page_list(soup, articles):
    # 獲取每篇文章的標題與鏈接
    for entry in soup.select(".r-ent"):
        title_tag = entry.select_one(".title a")
        if title_tag:
            title = title_tag.text.strip()
            link = "https://www.ptt.cc" + title_tag['href']
            push_num = entry.select_one(".nrec").text
            articles.append({"title": title, "push_num": push_num, "link": link})

def fetch_page_content(page, articles):
    # 爬取每篇文章的內文與推文
    for article in articles:
        page.goto(article["link"])
        post_content = page.content()
        post_soup = BeautifulSoup(post_content, "lxml")
        
        # 文章內文
        main_content = post_soup.select_one("#main-content")
        content_text = main_content.get_text().split("--")[0].strip()
        
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

# 執行並打印結果
if __name__ == "__main__":

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
