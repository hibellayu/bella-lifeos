import os
import datetime
import urllib.request
from zoneinfo import ZoneInfo
import anthropic

TAIPEI = ZoneInfo("Asia/Taipei")


def fetch_calendar_events(ical_url: str, today: datetime.date) -> list[dict]:
    try:
        with urllib.request.urlopen(ical_url, timeout=10) as resp:
            raw = resp.read().decode("utf-8")
    except Exception as e:
        print(f"Failed to fetch calendar: {e}")
        return []

    events = []
    in_event = False
    current: dict = {}

    for line in raw.splitlines():
        line = line.strip()
        if line == "BEGIN:VEVENT":
            in_event = True
            current = {}
        elif line == "END:VEVENT" and in_event:
            in_event = False
            start = current.get("DTSTART", "")
            if start:
                try:
                    if "T" in start:
                        dt = datetime.datetime.strptime(start[:15], "%Y%m%dT%H%M%S")
                        event_date = dt.date()
                        time_str = dt.strftime("%H:%M")
                    else:
                        event_date = datetime.date(int(start[:4]), int(start[4:6]), int(start[6:8]))
                        time_str = "全天"
                    if event_date == today:
                        events.append({
                            "summary": current.get("SUMMARY", "（無標題）"),
                            "time": time_str,
                        })
                except Exception:
                    pass
        elif in_event and ":" in line:
            key, _, val = line.partition(":")
            key = key.split(";")[0]
            current[key] = val

    events.sort(key=lambda e: e["time"] if e["time"] != "全天" else "00:00")
    return events


def get_quote(client: anthropic.Anthropic) -> str:
    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=300,
        messages=[{
            "role": "user",
            "content": (
                "請給我一句來自書籍或哲學家的金句，可以是中文或英文。"
                "如果是英文，請附上中文翻譯與一句簡短解說（30字以內）。"
                "格式：\n金句本文\n\n── 出處\n\n（如為英文附：📖 中文：...）\n🍺 ..."
                "\n只輸出這個格式，不要其他說明。"
            ),
        }],
    )
    return message.content[0].text


def generate_html(today: datetime.date, events: list[dict], quote: str | None) -> str:
    date_str = today.strftime("%Y 年 %m 月 %d 日")
    weekdays = ["一", "二", "三", "四", "五", "六", "日"]
    weekday = weekdays[today.weekday()]

    if events:
        items_html = "".join(
            f'<li><span class="time">{e["time"]}</span><span class="title">{e["summary"]}</span></li>'
            for e in events
        )
        schedule_html = f"""
        <div class="section">
          <h2>📅 今日行程</h2>
          <ul class="events">{items_html}</ul>
        </div>"""
    else:
        schedule_html = """
        <div class="section free-section">
          <h2>📅 今日行程</h2>
          <p class="free-text">今日你很 Free 喔～</p>
        </div>"""

    quote_html = quote.replace("\n", "<br>") if quote else ""
    quote_block = f"""
        <div class="section quote-section">
          <h2>✨ 今日金句</h2>
          <blockquote>{quote_html}</blockquote>
        </div>""" if quote_html else ""

    return f"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Bella's LifeOS｜{date_str}</title>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: -apple-system, "PingFang TC", "Noto Sans TC", sans-serif;
      background: #f0ede8;
      color: #3d3530;
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 2rem 1rem;
    }}
    .card {{
      background: #fdfaf7;
      border: 1px solid #e8ddd5;
      border-radius: 24px;
      padding: 2.5rem 2rem;
      max-width: 600px;
      width: 100%;
      box-shadow: 0 4px 24px rgba(180,150,140,0.12);
    }}
    .header {{
      background: rgba(220, 180, 180, 0.8);
      border-radius: 20px 20px 0 0;
      margin: -2.5rem -2rem 2rem -2rem;
      padding: 2rem 2rem;
      text-align: center;
    }}
    .header .name {{
      font-size: 0.78rem;
      color: #8a6060;
      letter-spacing: 0.18em;
      text-transform: uppercase;
      margin-bottom: 0.5rem;
    }}
    .header .date {{
      font-size: 1.6rem;
      font-weight: 700;
      color: #3d2e2e;
    }}
    .header .weekday {{
      font-size: 0.9rem;
      color: #9a7070;
      margin-top: 0.25rem;
    }}
    .divider {{
      border: none;
      border-top: 1px solid #edd5d0;
      margin: 1.5rem 0;
    }}
    .section {{ margin-bottom: 1.5rem; }}
    .section:last-of-type {{ margin-bottom: 0; }}
    .section h2 {{
      font-size: 0.85rem;
      color: #9dbaA0;
      letter-spacing: 0.08em;
      margin-bottom: 1rem;
      text-transform: uppercase;
    }}
    .events {{ list-style: none; }}
    .events li {{
      display: flex;
      gap: 1rem;
      align-items: flex-start;
      padding: 0.7rem 0;
      border-bottom: 1px solid #f0e5e0;
    }}
    .events li:last-child {{ border-bottom: none; }}
    .time {{
      font-size: 0.78rem;
      color: #c4938a;
      min-width: 42px;
      padding-top: 2px;
      font-variant-numeric: tabular-nums;
    }}
    .title {{ font-size: 0.95rem; line-height: 1.6; color: #3d3530; }}
    .free-text {{
      font-size: 1.05rem;
      color: #c4938a;
      font-weight: 500;
      padding: 0.5rem 0;
    }}
    .quote-section blockquote {{
      font-size: 0.93rem;
      line-height: 1.9;
      color: #6b5a55;
      border-left: 3px solid #d4a8b0;
      padding-left: 1.2rem;
    }}
    .footer {{
      margin-top: 2rem;
      text-align: center;
      font-size: 0.72rem;
      color: #c8bab5;
    }}
  </style>
</head>
<body>
  <div class="card">
    <div class="header">
      <div class="name">Bella's LifeOS</div>
      <div class="date">{date_str}</div>
      <div class="weekday">星期{weekday}</div>
    </div>
    <hr class="divider">
    {schedule_html}
    <hr class="divider">
    {quote_block}
    <div class="footer">每日 09:00 台北時間自動更新</div>
  </div>
</body>
</html>"""


def main():
    ical_url = os.environ.get("GCAL_ICAL_URL", "")
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")

    now = datetime.datetime.now(TAIPEI)
    today = now.date()

    events = fetch_calendar_events(ical_url, today) if ical_url else []

    quote = None
    if api_key:
        client = anthropic.Anthropic(api_key=api_key)
        quote = get_quote(client)

    html = generate_html(today, events, quote)

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Generated index.html — {len(events)} events, quote={'yes' if quote else 'no'}")


if __name__ == "__main__":
    main()
