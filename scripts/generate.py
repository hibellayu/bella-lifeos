import os
import datetime
import random
import urllib.request
from zoneinfo import ZoneInfo
import anthropic

TAIPEI = ZoneInfo("Asia/Taipei")

# 精選語錄庫：所有引用均有明確出處，涵蓋哲學、心理學、佛學、禪宗、道教
QUOTES = [
    # ── 一行禪師 ──
    {
        "text": "The present moment is the only moment available to us, and it is the door to all moments.",
        "zh": "當下這一刻是我們唯一擁有的，也是通往一切時刻的門。",
        "source": "一行禪師《正念的奇蹟》The Miracle of Mindfulness",
    },
    {
        "text": "Smile, breathe and go slowly.",
        "zh": "微笑，呼吸，慢慢走。",
        "source": "一行禪師《步步安樂行》Peace Is Every Step",
    },
    {
        "text": "The most precious gift we can offer anyone is our attention.",
        "zh": "我們能給予他人最珍貴的禮物，是我們的專注與臨在。",
        "source": "一行禪師《與自己和好》Being Peace",
    },
    {
        "text": "Because you are alive, everything is possible.",
        "zh": "因為你還活著，一切皆有可能。",
        "source": "一行禪師《沒有泥土，就沒有蓮花》No Mud, No Lotus",
    },
    {
        "text": "Walk as if you are kissing the Earth with your feet.",
        "zh": "行走時，如同用你的雙腳親吻大地。",
        "source": "一行禪師《步步安樂行》Peace Is Every Step",
    },
    {
        "text": "Sometimes your joy is the source of your smile, but sometimes your smile can be the source of your joy.",
        "zh": "有時是喜悅帶來微笑，但有時，是微笑帶來喜悅。",
        "source": "一行禪師《正念的奇蹟》The Miracle of Mindfulness",
    },
    {
        "text": "To be beautiful means to be yourself. You don't need to be accepted by others. You need to accept yourself.",
        "zh": "美麗意味著做你自己。你不需要被他人接受，你需要接受自己。",
        "source": "一行禪師《真愛》True Love",
    },
    # ── 道德經・老子 ──
    {
        "text": "知人者智，自知者明。勝人者有力，自勝者強。",
        "zh": None,
        "source": "老子《道德經》第三十三章",
    },
    {
        "text": "上善若水。水善利萬物而不爭，處衆人之所惡，故幾於道。",
        "zh": None,
        "source": "老子《道德經》第八章",
    },
    {
        "text": "致虛極，守靜篤。萬物並作，吾以觀復。",
        "zh": None,
        "source": "老子《道德經》第十六章",
    },
    {
        "text": "為學日益，為道日損。損之又損，以至於無為。無為而無不為。",
        "zh": None,
        "source": "老子《道德經》第四十八章",
    },
    {
        "text": "信言不美，美言不信。善者不辯，辯者不善。",
        "zh": None,
        "source": "老子《道德經》第八十一章",
    },
    # ── 莊子 ──
    {
        "text": "相濡以沫，不如相忘於江湖。",
        "zh": None,
        "source": "莊子《大宗師》",
    },
    {
        "text": "吾生也有涯，而知也無涯。以有涯隨無涯，殆已。",
        "zh": None,
        "source": "莊子《養生主》",
    },
    {
        "text": "天地有大美而不言，四時有明法而不議，萬物有成理而不說。",
        "zh": None,
        "source": "莊子《知北遊》",
    },
    # ── 禪宗 ──
    {
        "text": "菩提本無樹，明鏡亦非台。本來無一物，何處惹塵埃。",
        "zh": None,
        "source": "惠能《六祖壇經·行由品》",
    },
    {
        "text": "日日是好日。",
        "zh": None,
        "source": "雲門文偃禪師，收錄於《碧巖錄》第六則",
    },
    # ── 論語・孔子 ──
    {
        "text": "學而不思則罔，思而不學則殆。",
        "zh": None,
        "source": "孔子《論語·為政》",
    },
    {
        "text": "吾日三省吾身：為人謀而不忠乎？與朋友交而不信乎？傳不習乎？",
        "zh": None,
        "source": "曾子語，《論語·學而》",
    },
    {
        "text": "知之為知之，不知為不知，是知也。",
        "zh": None,
        "source": "孔子《論語·為政》",
    },
    # ── Marcus Aurelius ──
    {
        "text": "You have power over your mind—not outside events. Realize this, and you will find strength.",
        "zh": "你能掌控的是你的心，而非外在的事件。認清這一點，你將找到力量。",
        "source": "Marcus Aurelius《沉思錄》Meditations，第六卷",
    },
    {
        "text": "Waste no more time arguing about what a good man should be. Be one.",
        "zh": "別再浪費時間爭論何謂好人，直接去做一個好人。",
        "source": "Marcus Aurelius《沉思錄》Meditations，第十卷",
    },
    {
        "text": "Confine yourself to the present.",
        "zh": "把自己限定在當下。",
        "source": "Marcus Aurelius《沉思錄》Meditations，第八卷",
    },
    # ── Viktor Frankl ──
    {
        "text": "When we are no longer able to change a situation, we are challenged to change ourselves.",
        "zh": "當我們無法改變處境時，我們被挑戰去改變自己。",
        "source": "Viktor Frankl《活出意義來》Man's Search for Meaning",
    },
    {
        "text": "Everything can be taken from a man but one thing: the last of the human freedoms—to choose one's attitude in any given set of circumstances.",
        "zh": "人可以被奪走一切，唯有一樣不能——在任何處境下選擇自己態度的自由。",
        "source": "Viktor Frankl《活出意義來》Man's Search for Meaning",
    },
    # ── Rainer Maria Rilke ──
    {
        "text": "Be patient toward all that is unsolved in your heart and try to love the questions themselves.",
        "zh": "對心中一切未解的事保持耐心，試著去愛那些問題本身。",
        "source": "Rainer Maria Rilke《給一位年輕詩人的信》Letters to a Young Poet，第四封信",
    },
    # ── Albert Camus ──
    {
        "text": "In the midst of winter, I found there was, within me, an invincible summer.",
        "zh": "在嚴冬之中，我發現自己內心有一個不可征服的夏天。",
        "source": "Albert Camus《重返提帕薩》Return to Tipasa（1952）",
    },
    # ── Epictetus ──
    {
        "text": "Make the best use of what is in your power, and take the rest as it happens.",
        "zh": "善用你能掌控的，其餘的就順其自然。",
        "source": "Epictetus《手冊》Enchiridion，第一章",
    },
    # ── Carl Jung ──
    {
        "text": "Who looks outside, dreams; who looks inside, awakes.",
        "zh": "向外看的人在做夢；向內看的人才是清醒的。",
        "source": "Carl Jung 致 Fanny Bowditch 信函（1916），收錄於《榮格書信集》",
    },
    # ── Khalil Gibran ──
    {
        "text": "The deeper that sorrow carves into your being, the more joy you can contain.",
        "zh": "悲傷在你內心挖得越深，你所能承載的喜悅就越多。",
        "source": "Khalil Gibran《先知》The Prophet，〈論喜與悲〉",
    },
    {
        "text": "Your pain is the breaking of the shell that encloses your understanding.",
        "zh": "你的痛苦，是包裹著你理解力的那個殼正在破裂。",
        "source": "Khalil Gibran《先知》The Prophet，〈論痛苦〉",
    },
]


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


def get_daily_quote(today: datetime.date, api_key: str) -> dict:
    random.seed(today.toordinal())
    quote = random.choice(QUOTES)

    reflection = ""
    if api_key:
        try:
            client = anthropic.Anthropic(api_key=api_key)
            text = quote["text"]
            source = quote["source"]
            message = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=120,
                messages=[{
                    "role": "user",
                    "content": (
                        f"這句話：「{text}」（出自 {source}）\n"
                        "請用繁體中文寫一句 25 字以內的短句反思，語氣輕鬆像朋友分享心得，"
                        "不要重複引文內容，直接輸出反思句子，不要任何前綴標籤。"
                    ),
                }],
            )
            reflection = message.content[0].text.strip()
        except Exception as e:
            print(f"Claude API error: {e}")

    return {**quote, "reflection": reflection}


def generate_html(today: datetime.date, events: list[dict], quote: dict) -> str:
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

    q_text = quote["text"]
    q_zh = quote.get("zh") or ""
    q_source = quote["source"]
    q_reflection = quote.get("reflection") or ""

    zh_line = f'<p class="quote-zh">{q_zh}</p>' if q_zh else ""
    reflection_line = f'<p class="quote-reflection">🍺 {q_reflection}</p>' if q_reflection else ""

    quote_html = f"""
        <div class="section quote-section">
          <h2>✨ 今日金句</h2>
          <blockquote>
            <p class="quote-text">{q_text}</p>
            {zh_line}
            <p class="quote-source">── {q_source}</p>
            {reflection_line}
          </blockquote>
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
      color: #9dbaa0;
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
      border-left: 3px solid #d4a8b0;
      padding-left: 1.2rem;
    }}
    .quote-text {{
      font-size: 0.95rem;
      line-height: 1.8;
      color: #3d3530;
      font-style: italic;
    }}
    .quote-zh {{
      font-size: 0.88rem;
      line-height: 1.7;
      color: #6b5a55;
      margin-top: 0.5rem;
    }}
    .quote-source {{
      font-size: 0.75rem;
      color: #b09a95;
      margin-top: 0.6rem;
      letter-spacing: 0.03em;
    }}
    .quote-reflection {{
      font-size: 0.85rem;
      color: #8a7570;
      margin-top: 0.8rem;
      line-height: 1.6;
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
    {quote_html}
    <div class="footer">每小時自動更新</div>
  </div>
</body>
</html>"""


def main():
    ical_url = os.environ.get("GCAL_ICAL_URL", "")
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")

    now = datetime.datetime.now(TAIPEI)
    today = now.date()

    events = fetch_calendar_events(ical_url, today) if ical_url else []
    quote = get_daily_quote(today, api_key)

    html = generate_html(today, events, quote)

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Generated index.html — {len(events)} events, quote: {quote['source']}")


if __name__ == "__main__":
    main()
