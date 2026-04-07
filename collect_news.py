import feedparser
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timezone, timedelta
import os

RSS_FEEDS = [
    ("SaaStr", "https://www.saastr.com/feed/"),
    ("Product Hunt", "https://www.producthunt.com/feed"),
    ("TechCrunch SaaS", "https://techcrunch.com/tag/saas/feed/"),
    ("G2 Learning Hub", "https://learn.g2.com/rss.xml"),
    ("ChartMogul Blog", "https://chartmogul.com/blog/feed/"),
]

def collect_news():
    articles = []
    for source_name, url in RSS_FEEDS:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:3]:
                articles.append({
                    "title": entry.get("title", "No title"),
                    "link": entry.get("link", ""),
                    "summary": entry.get("summary", "")[:150] + "...",
                    "source": source_name,
                })
        except Exception as e:
            print(f"Error fetching {source_name}: {e}")
    return articles

def build_html(articles):
    jst = timezone(timedelta(hours=9))
    today = datetime.now(jst).strftime("%Y年%m月%d日")
    rows = ""
    for a in articles:
        rows += f"""
        <tr>
          <td style="padding:12px;border-bottom:1px solid #eee;">
            <div style="font-size:11px;color:#888;">{a['source']}</div>
            <a href="{a['link']}" style="font-weight:bold;color:#1a0dab;text-decoration:none;">
              {a['title']}
            </a>
            <div style="font-size:12px;color:#555;margin-top:4px;">{a['summary']}</div>
          </td>
        </tr>"""
    return f"""
    <html><body style="font-family:sans-serif;max-width:600px;margin:auto;">
      <h2 style="background:#0077b6;color:white;padding:16px;border-radius:8px;">
        ☁️ SaaS業界 ニュースダイジェスト<br>
        <span style="font-size:14px;">{today}</span>
      </h2>
      <table width="100%" cellpadding="0" cellspacing="0">{rows}</table>
      <p style="color:#aaa;font-size:11px;text-align:center;">自動収集 by GitHub Actions</p>
    </body></html>"""

def send_email(html_content):
    sender = os.environ["GMAIL_ADDRESS"]
    password = os.environ["GMAIL_APP_PASSWORD"]
    receiver = os.environ["GMAIL_ADDRESS"]

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"☁️ SaaSニュース {datetime.now().strftime('%m/%d')}"
    msg["From"] = sender
    msg["To"] = receiver
    msg.attach(MIMEText(html_content, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, password)
        server.sendmail(sender, receiver, msg.as_string())
    print("メール送信完了！")

if __name__ == "__main__":
    articles = collect_news()
    html = build_html(articles)
    send_email(html)
