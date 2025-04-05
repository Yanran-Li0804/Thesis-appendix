# -*- coding: utf-8 -*-
# 不可避免重复……后续去重吧
import time
from playwright.async_api import async_playwright
import csv
from datetime import datetime
import os

def save_to_csv(data, filename):
    if not data:
        print("No data to save.")
        return

    file_exists = os.path.exists(filename)  # 检查文件是否已存在

    try:
        with open(filename, mode='a', newline='', encoding='utf-8') as file:
            fieldnames = ["title", "content", "url", "last_reply_time"]
            writer = csv.DictWriter(file, fieldnames=fieldnames)

            if not file_exists:  # 如果文件不存在，写入 header
                writer.writeheader()

            writer.writerows(data)
        print(f"数据已保存到 {filename}")
    except Exception as e:
        print(f"保存数据到 CSV 时发生错误: {e}")
# 处理回复时间，自动将时间补上当天日期
def format_reply_time(reply_time):
    current_date = datetime.now().strftime('%Y-%m-%d')  # 当前日期 (YYYY-MM-DD)
    if ':' in reply_time:  # 如果回复时间是当天时间格式，例如 '16:29'
        # formatted_time = f"{current_date} {reply_time}"
        formatted_time = current_date
        return formatted_time
    else:  # 如果是日期格式，例如 '9-11'
        current_year = datetime.now().year  # 获取当前年份
        formatted_time = f"{current_year}-{reply_time.replace('-', '-')}"  # 格式化为 YYYY-MM-DD
        return formatted_time
async def get_data(page):
    try:
        # 等待直到至少有一个post出现，最多等5秒
        await page.wait_for_selector('li.j_thread_list.clearfix.thread_item_box', timeout=5000)

        posts = await page.query_selector_all('li.j_thread_list.clearfix.thread_item_box')
        post_data = []
        for post in posts:
            title_element = await post.query_selector('div.threadlist_title.pull_left.j_th_tit')
            title = await title_element.inner_text() if title_element else "unknown title"
            title = title.strip()

            link_element = await post.query_selector('a.j_th_tit')
            link = await link_element.get_attribute('href') if link_element else "unknown link"
            link = f"https://tieba.baidu.com{link}"

            content_element = await post.query_selector('div.threadlist_abs.threadlist_abs_onlyline')
            content = await content_element.inner_text() if content_element else ''
            content = content.strip()

            # 获取最后回复时间
            reply_time_element = await post.query_selector('span.threadlist_reply_date.pull_right.j_reply_data')
            reply_time = await reply_time_element.inner_text() if reply_time_element else "unknown time"
            # 格式化回复时间
            formatted_reply_time = format_reply_time(reply_time.strip())

            data_dic = {
                "title": title,
                "content": content,
                "url": link,
                "last_reply_time": formatted_reply_time
            }
            post_data.append(data_dic)

        return post_data
    except Exception as e:
        print(f"获取数据时发生错误: {e}")
# 翻页
async def click_with_retries(page, selector, max_attempts, delay):
    attempts = 0
    while attempts < max_attempts:
        try:
            # 等待弹窗消失
            await page.wait_for_selector('#tiebaCustomPassLogin', state='hidden', timeout=3000)
            element = await page.query_selector(selector)
            if element:
                await element.scroll_into_view_if_needed()
                await element.click()
                return True
        except Exception as e:
            print(f"点击元素时发生错误: {e}")
        attempts += 1
        await page.wait_for_timeout(delay)  # 等待一段时间后再重试
    print(f"点击 {selector} 元素失败，已尝试 {max_attempts} 次")

async def process(page, start_page, num_pages): # num_pages是这次process需要爬取的总页数 # page pn=0; 1, 2
    all_data = []  # 用于保存所有爬取的数据
    current_page = start_page # 1
    try:
        for i in range(num_pages): # 循环num_pages次 # i=0 or 1
            print(f"正在获取第 {current_page} 页...")
            page_data = await get_data(page)
            all_data.extend(page_data)

            await click_with_retries(page, 'a:has-text("上一页")', max_attempts=50, delay=1500) # 翻页 pn=50
            await page.wait_for_load_state('domcontentloaded')
            # 添加这一行打印新页面的 URL 以确保翻页成功
            await page.wait_for_selector('a:has-text("上一页")', timeout=2000)
            current_page = current_page - 1  # 页数-1
            # 每爬取20页保存一次
            if (i + 1) % 20 == 0:
                save_to_csv(all_data, output_file)
                all_data = []
                print("已爬取20页内容，已保存数据...")

    except Exception as e:
        print(f"处理帖子时发生错误: {e}")

    finally:
        if all_data:  # 检查是否有数据需要保存
            save_to_csv(all_data, output_file)

async def main(start_page, num_pages, output_file):
    start_time = time.time()
    try:
        async with async_playwright() as p:
            print("Playwright launched")
            total_processed_pages = 0  # 用于跟踪已处理的总页数

            while total_processed_pages < num_pages:
                browser = await p.chromium.launch(headless=False)
                context = await browser.new_context()
                page = await context.new_page()
                print("Page opened")

                url = f'https://tieba.baidu.com/f?kw=%E5%AD%99%E7%AC%91%E5%B7%9D&ie=utf-8&pn={(start_page-1) * 50}'
                await page.goto(url, wait_until='domcontentloaded')
                await page.wait_for_timeout(2000)
                print("Page loaded")

                pages_to_process = min(num_pages - total_processed_pages, 20) # 每20页重启一次浏览器
                await process(page, start_page, pages_to_process)  # 每次处理20页

                await page.close()  # 关闭当前页面
                await context.close()  # 关闭上下文
                await browser.close()  # 关闭浏览器

                total_processed_pages += pages_to_process
                start_page = start_page - pages_to_process  # 更新开始页数 # 第一次是2001，第二次是2001-20

    except Exception as e:
        print(f"Error in main function: {e}")
    except KeyboardInterrupt:
        print("程序被强行终止，正在保存数据...")
    finally:
        end_time = time.time()  # 记录结束时间
        elapsed_time = end_time - start_time  # 计算运行时间
        print(f"程序运行了 {elapsed_time:.2f} 秒")  # 打印运行时间

if __name__ == '__main__':
    import asyncio

    start_page = int(input("从第几页开始: "))
    num_pages = int(input("请输入你想要爬取的页数: "))
    output_file = input("请输入保存数据的文件名（包括扩展名，如：rawdata_20241015.csv）：")
    asyncio.run(main(start_page, num_pages, output_file))