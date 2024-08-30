import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import json

url = "https://www.ptt.cc/bbs/Gossiping/index.html"
num_page = 3

async def playwright_scraper(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        
        # 設置 cookie
        await context.add_cookies([{
            'name': 'over18',
            'value': '1',
            'domain': '.ptt.cc',
            'path': '/'
        }])

        articles = []
        for _ in range(num_page):
            page = await context.new_page()
            await page.goto(url)
            await page.wait_for_load_state("load")
            
            page_content = await page.content()
            soup = BeautifulSoup(page_content, "lxml")
            fetch_page_list(soup, articles)

            controls = soup.select(".action-bar a.btn.wide")[1]
            url = parse_next_link(controls)
            print("url:", url)
            await page.close()
    
        await fetch_page_content(context, articles)
        await browser.close()

    return articles

def parse_next_link(controls):
    link = controls.attrs['href']
    next_page_url = 'https://www.ptt.cc' + link
    return next_page_url

def fetch_page_list(soup, articles):
    for entry in soup.select(".r-ent"):
        title_tag = entry.select_one(".title a")
        if title_tag:
            title = title_tag.text.strip()
            link = "https://www.ptt.cc" + title_tag['href']
            push_num = entry.select_one(".nrec").text
            articles.append({"title": title, "push_num": push_num, "link": link})

async def fetch_page_content(context, articles):
    async def fetch_article(article):
        page = await context.new_page()
        await page.goto(article["link"])
        post_content = await page.content()
        await page.close()
        
        post_soup = BeautifulSoup(post_content, "lxml")
        
        main_content = post_soup.select_one("#main-content")
        content_text = main_content.get_text().split("--")[0].strip()
        
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

    await asyncio.gather(*[fetch_article(article) for article in articles])

async def main():
    articles = await playwright_scraper(url)
    for article in articles:
        print(f"Title: {article['title']}")
        print(f"Push_num: {article['push_num']}")
        print(f"Content: {article['content']}")
        print("Comments:")
        for comment in article['comments']:
            print(f"{comment['tag']} {comment['userid']}: {comment['content']}")
        print("="*80)
    
    # df = pd.DataFrame(articles)
    # df.to_csv('output.csv', index=False, encoding='utf-8-sig')
    # 將數據寫入 JSON 文件
    with open('data.json', 'w', encoding='utf-8') as file:
        json.dump(articles, file, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    asyncio.run(main())