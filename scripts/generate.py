import os
import datetime
import urllib.request
from zoneinfo import ZoneInfo
import anthropic

TAIPEI = ZoneInfo("Asia/Taipei")


def fetch_calendar_events(ical_url: str, today: datetime.date) -> list[dict]:
    """Fetch and parse today's events from a Google Calendar iCal URL."""
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
                        # datetime event
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
    """Use Claude to generate a motivational quote."""
    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=300,
        messages=[{
            "role": "user",
            "content": (
                "請給我一句來自書籍或哲學家的金句，可以是中文或英文。"
                "如果是英文，請附上中文翻譯與一句簡短解說（30字以內）。"
                "格式：\n金句本文\n\n── 出處\n\n（如為英文附：📖 中文：...）\n解說：..."
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
        content_html = f"""
        <div class="section">
          <h2>📅 今日行程</h2>
          <ul class="events">{items_html}</ul>
        </div>"""
    else:
        quote_html = quote.replace("\n", "<br>") if quote else "今日靜心，明日前行。"
        content_html = f"""
        <div class="section quote-section">
          <h2>✨ 今日金句</h2>
          <blockquote>{quote_html}</blockquote>
        </div>"""

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
      background: #0f0f14;
      color: #e8e0f0;
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 2rem 1rem;
    }}
    .card {{
      background: #1a1a2e;
      border: 1px solid #2e2e4a;
      border-radius: 20px;
      padding: 2.5rem 2rem;
      max-width: 600px;
      width: 100%;
      box-shadow: 0 8px 40px rgba(0,0,0,0.4);
    }}
    .header {{ margin-bottom: 2rem; text-align: center; }}
    .header .name {{
      font-size: 0.85rem;
      color: #a78bfa;
      letter-spacing: 0.15em;
      text-transform: uppercase;
      margin-bottom: 0.4rem;
    }}
    .header .date {{
      font-size: 1.6rem;
      font-weight: 700;
      color: #f3eeff;
    }}
    .header .weekday {{
      font-size: 0.9rem;
      color: #6b6b8a;
      margin-top: 0.2rem;
    }}
    .section h2 {{
      font-size: 1rem;
      color: #a78bfa;
      margin-bottom: 1.2rem;
      letter-spacing: 0.05em;
    }}
    .events {{ list-style: none; }}
    .events li {{
      display: flex;
      gap: 1rem;
      align-items: flex-start;
      padding: 0.75rem 0;
      border-bottom: 1px solid #2a2a3e;
    }}
    .events li:last-child {{ border-bottom: none; }}
    .time {{
      font-size: 0.8rem;
      color: #a78bfa;
      min-width: 42px;
      padding-top: 2px;
      font-variant-numeric: tabular-nums;
    }}
    .title {{ font-size: 1rem; line-height: 1.5; color: #e8e0f0; }}
    .quote-section blockquote {{
      font-size: 1rem;
      line-height: 1.9;
      color: #d0c8e8;
      border-left: 3px solid #a78bfa;
      padding-left: 1.2rem;
    }}
    .footer {{
      margin-top: 2rem;
      text-align: center;
      font-size: 0.75rem;
      color: #3a3a5a;
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
    {content_html}
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
    if not events and api_key:
        client = anthropic.Anthropic(api_key=api_key)
        quote = get_quote(client)

    html = generate_html(today, events, quote)

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Generated index.html — {len(events)} events, quote={'yes' if quote else 'no'}")


if __name__ == "__main__":
    main()
