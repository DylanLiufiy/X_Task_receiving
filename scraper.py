import os
import re
import time
import random
import urllib.parse
import requests
from bs4 import BeautifulSoup

# ==================== 🎯 核心个性化配置 ====================
PLATFORM = "youtube.com"      # 要抓取的平台，可选: "youtube.com" 或 "tiktok.com"
KEYWORD = "AI tools"          # 你想追踪的热门领域/爆火视频关键词
EMAIL_DOMAIN = "gmail.com"     # 想要筛选的电子邮箱后缀
MAX_PAGES = 3                 # 每次运行抓取的 Google 搜索页数（建议3-5页，太高GitHub公共IP易被风控）
# =========================================================

def get_user_agents():
    return [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0"
    ]

def build_search_url(page):
    # 构造高级 Dorking 语法: site:youtube.com "AI tools" "gmail.com"
    query = f'site:{PLATFORM} "{KEYWORD}" "{EMAIL_DOMAIN}"'
    start = page * 10
    return f"https://google.com{urllib.parse.quote_plus(query)}&start={start}"

def extract_emails_and_links(text):
    # 精准匹配标准的电子邮箱格式
    email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
    emails = re.findall(email_pattern, text)
    
    # 提取潜在的创作者主页链接
    link_pattern = rf'https?://(?:www\.)?{PLATFORM}/@[a-zA-Z0-9_\-\.]+'
    links = re.findall(link_pattern, text)
    
    return list(set(emails)), list(set(links))

def main():
    print(f"🚀 启动自动化抓取工作流...")
    print(f"📍 目标平台: {PLATFORM} | 热门关键词: {KEYWORD}")
    
    all_leads = {}
    headers = {"User-Agent": random.choice(get_user_agents())}
    
    for page in range(MAX_PAGES):
        url = build_search_url(page)
        print(f"正在分析第 {page + 1} 页潜力数据...")
        
        try:
            # 增加随机延迟防封锁
            time.sleep(random.uniform(2, 5))
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code == 429:
                print("⚠️ 触发安全拦截(429 Too Many Requests)，正在尝试安全撤退并保存已有数据...")
                break
                
            if response.status_code != 200:
                print(f"⚠️ 请求异常，状态码: {response.status_code}")
                continue
                
            soup = BeautifulSoup(response.text, 'html.parser')
            # 捕获整个搜索结果页面的所有文本片段进行深度交叉比对
            page_text = soup.get_text()
            emails, links = extract_emails_and_links(page_text)
            
            # 简单粗暴的数据融合逻辑：将本页抓到的邮箱与主页做多对多或单项匹配
            for email in emails:
                if email.lower() not in all_leads:
                    # 尽可能找一个属于该平台的达人链接绑定，找不到则留空
                    matched_link = links[0] if links else f"https://{PLATFORM}/(根据搜索定位)"
                    all_leads[email.lower()] = matched_link
                    print(f"✨ 成功拦截到达人商务邮箱: {email} -> 来源: {matched_link}")
                    
        except Exception as e:
            print(f"❌ 发生未知错误: {e}")
            continue

    # ==================== 💾 结果本地持久化 ====================
    if all_leads:
        # 如果没有 output 文件夹，自动创建
        if not os.path.exists("output"):
            os.makedirs("output")
            
        csv_path = "output/leads.csv"
        file_exists = os.path.exists(csv_path)
        
        with open(csv_path, "a", encoding="utf-8") as f:
            if not file_exists:
                f.write("Email,Platform_Link\n") # 写入表头
            for email, link in all_leads.items():
                f.write(f"{email},{link}\n")
                
        print(f"🎉 任务圆满成功！本次共新捕获 {len(all_leads)} 个精准商业线索，已保存至 {csv_path}")
    else:
        print("💡 提示：本次运行未发现满足条件的新邮件，可能已被平台风控，请尝试更换关键词。")

if __name__ == "__main__":
    main()
