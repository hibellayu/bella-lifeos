import os
import datetime
import random
import urllib.request
from zoneinfo import ZoneInfo
import anthropic

TAIPEI = ZoneInfo("Asia/Taipei")

SOLAR_TERMS = {
    2025: {(1,5):"小寒",(1,20):"大寒",(2,3):"立春",(2,18):"雨水",(3,5):"驚蟄",(3,20):"春分",(4,4):"清明",(4,20):"穀雨",(5,5):"立夏",(5,21):"小滿",(6,5):"芒種",(6,21):"夏至",(7,7):"小暑",(7,22):"大暑",(8,7):"立秋",(8,23):"處暑",(9,7):"白露",(9,23):"秋分",(10,8):"寒露",(10,23):"霜降",(11,7):"立冬",(11,22):"小雪",(12,7):"大雪",(12,21):"冬至"},
    2026: {(1,5):"小寒",(1,20):"大寒",(2,4):"立春",(2,19):"雨水",(3,5):"驚蟄",(3,20):"春分",(4,4):"清明",(4,20):"穀雨",(5,5):"立夏",(5,21):"小滿",(6,5):"芒種",(6,21):"夏至",(7,7):"小暑",(7,22):"大暑",(8,7):"立秋",(8,23):"處暑",(9,7):"白露",(9,23):"秋分",(10,8):"寒露",(10,23):"霜降",(11,7):"立冬",(11,22):"小雪",(12,7):"大雪",(12,21):"冬至"},
    2027: {(1,5):"小寒",(1,20):"大寒",(2,3):"立春",(2,18):"雨水",(3,5):"驚蟄",(3,21):"春分",(4,5):"清明",(4,20):"穀雨",(5,5):"立夏",(5,21):"小滿",(6,6):"芒種",(6,21):"夏至",(7,7):"小暑",(7,23):"大暑",(8,7):"立秋",(8,23):"處暑",(9,7):"白露",(9,23):"秋分",(10,8):"寒露",(10,23):"霜降",(11,7):"立冬",(11,22):"小雪",(12,7):"大雪",(12,22):"冬至"},
}

# 精選語錄庫 50 句：靈性／療癒心理／職涯成長三大主線
QUOTES = [
    # ── 心經（3）──
    {"text": "色不異空，空不異色；色即是空，空即是色。", "zh": None, "source": "《般若波羅蜜多心經》"},
    {"text": "心無罣礙，無罣礙故，無有恐怖，遠離顛倒夢想，究竟涅槃。", "zh": None, "source": "《般若波羅蜜多心經》"},
    {"text": "照見五蘊皆空，度一切苦厄。", "zh": None, "source": "《般若波羅蜜多心經》"},

    # ── 金剛經（4）──
    {"text": "一切有為法，如夢幻泡影，如露亦如電，應作如是觀。", "zh": None, "source": "《金剛般若波羅蜜經》"},
    {"text": "凡所有相，皆是虛妄。若見諸相非相，即見如來。", "zh": None, "source": "《金剛般若波羅蜜經》"},
    {"text": "應無所住而生其心。", "zh": None, "source": "《金剛般若波羅蜜經》"},
    {"text": "過去心不可得，現在心不可得，未來心不可得。", "zh": None, "source": "《金剛般若波羅蜜經》"},

    # ── 楞嚴經（3）──
    {"text": "狂心若歇，歇即菩提。", "zh": None, "source": "《大佛頂首楞嚴經》卷六"},
    {"text": "若能轉物，則同如來。", "zh": None, "source": "《大佛頂首楞嚴經》卷二"},
    {"text": "因地不真，果招紆曲。", "zh": None, "source": "《大佛頂首楞嚴經》卷六"},

    # ── 一行禪師（7）──
    {"text": "The present moment is the only moment available to us, and it is the door to all moments.", "zh": "當下這一刻是我們唯一擁有的，也是通往一切時刻的門。", "source": "一行禪師《正念的奇蹟》The Miracle of Mindfulness"},
    {"text": "Walk as if you are kissing the Earth with your feet.", "zh": "行走時，如同用你的雙腳親吻大地。", "source": "一行禪師《步步安樂行》Peace Is Every Step"},
    {"text": "Letting go gives us freedom, and freedom is the only condition for happiness.", "zh": "放下給予我們自由，而自由是幸福的唯一條件。", "source": "一行禪師《佛陀之心》The Heart of the Buddha's Teaching"},
    {"text": "Because you are alive, everything is possible.", "zh": "因為你還活著，一切皆有可能。", "source": "一行禪師《沒有泥土，就沒有蓮花》No Mud, No Lotus"},
    {"text": "The most precious gift we can offer anyone is our attention.", "zh": "我們能給予他人最珍貴的禮物，是我們的專注與臨在。", "source": "一行禪師《與自己和好》Being Peace"},
    {"text": "Smile, breathe and go slowly.", "zh": "微笑，呼吸，慢慢走。", "source": "一行禪師《步步安樂行》Peace Is Every Step"},
    {"text": "In true love, you attain freedom.", "zh": "在真愛之中，你獲得自由。", "source": "一行禪師《真愛》True Love"},

    # ── Carl Jung・榮格（5）──
    {"text": "Who looks outside, dreams; who looks inside, awakes.", "zh": "向外看的人在做夢；向內看的人才是清醒的。", "source": "Carl Jung 致 Fanny Bowditch 信函（1916），收錄於《榮格書信集》"},
    {"text": "Until you make the unconscious conscious, it will direct your life and you will call it fate.", "zh": "在你將潛意識化為意識之前，它將主導你的人生，而你會稱之為命運。", "source": "Carl Jung，收錄於《榮格文集》第十一卷"},
    {"text": "The privilege of a lifetime is to become who you truly are.", "zh": "一生最大的特權，是成為你真正的自己。", "source": "Carl Jung"},
    {"text": "Your vision will become clear only when you can look into your own heart.", "zh": "唯有當你能看見自己內心時，你的視野才會清晰。", "source": "Carl Jung"},
    {"text": "Everything that irritates us about others can lead us to an understanding of ourselves.", "zh": "他人身上令我們惱怒的一切，都可以引領我們認識自己。", "source": "Carl Jung《記憶、夢、省思》Memories, Dreams, Reflections"},

    # ── Brené Brown（3）──
    {"text": "Vulnerability is not winning or losing; it's having the courage to show up and be seen when we have no control over the outcome.", "zh": "脆弱不是輸贏的問題，而是在無法掌控結果時，仍有勇氣現身並讓人看見你。", "source": "Brené Brown《脆弱的力量》Daring Greatly"},
    {"text": "Owning our story and loving ourselves through that process is the bravest thing we'll ever do.", "zh": "承認自己的故事，並在這個過程中愛自己，是我們能做的最勇敢的事。", "source": "Brené Brown《不完美的禮物》The Gifts of Imperfection"},
    {"text": "The most dangerous stories we make up are the narratives that diminish our inherent worthiness of love and belonging.", "zh": "我們所編造的最危險的故事，是那些削弱我們天生值得被愛、值得歸屬的敘事。", "source": "Brené Brown《勇氣的力量》Rising Strong"},

    # ── Viktor Frankl（3）──
    {"text": "Everything can be taken from a man but one thing: the last of the human freedoms—to choose one's attitude in any given set of circumstances.", "zh": "人可以被奪走一切，唯有一樣不能——在任何處境下選擇自己態度的自由。", "source": "Viktor Frankl《活出意義來》Man's Search for Meaning"},
    {"text": "When we are no longer able to change a situation, we are challenged to change ourselves.", "zh": "當我們無法改變處境時，我們被挑戰去改變自己。", "source": "Viktor Frankl《活出意義來》Man's Search for Meaning"},
    {"text": "Life is never made unbearable by circumstances, but only by lack of meaning and purpose.", "zh": "生命從不因處境而變得無法承受，唯有缺乏意義與目的，才使人難以為繼。", "source": "Viktor Frankl《活出意義來》Man's Search for Meaning"},

    # ── Carl Rogers（2）──
    {"text": "The curious paradox is that when I accept myself just as I am, then I can change.", "zh": "奇妙的悖論是：當我完全接受現在的自己，我才能真正改變。", "source": "Carl Rogers《成為一個人》On Becoming a Person"},
    {"text": "What is most personal is most universal.", "zh": "最個人的，往往也是最普世的。", "source": "Carl Rogers《成為一個人》On Becoming a Person"},

    # ── Virginia Satir・薩提爾（2）──
    {"text": "Life is not what it's supposed to be. It is what it is. The way you cope with it is what makes the difference.", "zh": "生命不是它應該有的樣子，它就是它本來的樣子。你如何應對，才是真正的差別所在。", "source": "Virginia Satir"},
    {"text": "I am me. In all the world, there is no one else exactly like me.", "zh": "我就是我。在這個世界上，沒有任何人和我完全一樣。", "source": "Virginia Satir〈自我價值宣言〉My Declaration of Self-Esteem"},

    # ── Eckhart Tolle（2）──
    {"text": "Realize deeply that the present moment is all you ever have.", "zh": "深刻地認識到，當下這一刻是你唯一真正擁有的。", "source": "Eckhart Tolle《當下的力量》The Power of Now"},
    {"text": "You find peace not by rearranging the circumstances of your life, but by realizing who you are at the deepest level.", "zh": "平靜不是透過重新安排生命的處境得來的，而是透過認識你在最深層是誰。", "source": "Eckhart Tolle《當下的力量》The Power of Now"},

    # ── 納瓦爾寶典（6）──
    {"text": "Seek wealth, not money or status. Wealth is having assets that earn while you sleep.", "zh": "追求財富，而非金錢或地位。財富是讓你在睡眠中持續產生收益的資產。", "source": "Naval Ravikant《納瓦爾寶典》The Almanack of Naval Ravikant"},
    {"text": "Play long-term games with long-term people.", "zh": "和願意長期合作的人，玩長期的遊戲。", "source": "Naval Ravikant《納瓦爾寶典》The Almanack of Naval Ravikant"},
    {"text": "Happiness is a choice and a skill and you can dedicate yourself to learning that skill.", "zh": "快樂是一種選擇，也是一種技能，你可以全心投入去學習它。", "source": "Naval Ravikant《納瓦爾寶典》The Almanack of Naval Ravikant"},
    {"text": "Specific knowledge is knowledge you cannot be trained for. If society can train you, it can train someone else and replace you.", "zh": "專屬知識是無法被訓練出來的。若社會能訓練你，就能訓練別人來取代你。", "source": "Naval Ravikant《納瓦爾寶典》The Almanack of Naval Ravikant"},
    {"text": "Escape competition through authenticity.", "zh": "用你的獨特性，逃離競爭。", "source": "Naval Ravikant《納瓦爾寶典》The Almanack of Naval Ravikant"},
    {"text": "All the returns in life, whether in wealth, relationships, or knowledge, come from compound interest.", "zh": "人生所有的回報，無論是財富、關係還是知識，都來自複利。", "source": "Naval Ravikant《納瓦爾寶典》The Almanack of Naval Ravikant"},

    # ── Marcus Aurelius《沉思錄》（4）──
    {"text": "You have power over your mind—not outside events. Realize this, and you will find strength.", "zh": "你能掌控的是你的心，而非外在的事件。認清這一點，你將找到力量。", "source": "Marcus Aurelius《沉思錄》Meditations，第六卷"},
    {"text": "Waste no more time arguing about what a good man should be. Be one.", "zh": "別再浪費時間爭論何謂好人，直接去做一個好人。", "source": "Marcus Aurelius《沉思錄》Meditations，第十卷"},
    {"text": "The impediment to action advances action. What stands in the way becomes the way.", "zh": "阻礙行動之物，反而推進了行動。擋路之物，即成為路本身。", "source": "Marcus Aurelius《沉思錄》Meditations，第五卷"},
    {"text": "Confine yourself to the present.", "zh": "把自己限定在當下。", "source": "Marcus Aurelius《沉思錄》Meditations，第八卷"},

    # ── Seneca（3）──
    {"text": "Omnia aliena sunt, tempus tantum nostrum est.", "zh": "萬物皆屬他人，唯有時間是我們的。", "source": "Seneca《致魯奇里烏斯書信集》Epistulae Morales，第一封"},
    {"text": "We suffer more in imagination than in reality.", "zh": "我們在想像中受的苦，遠多於現實。", "source": "Seneca《致魯奇里烏斯書信集》Epistulae Morales，第十三封"},
    {"text": "Dum differtur vita transcurrit.", "zh": "我們拖延之際，生命正在飛逝。", "source": "Seneca《致魯奇里烏斯書信集》Epistulae Morales，第一封"},

    # ── Epictetus（3）──
    {"text": "Make the best use of what is in your power, and take the rest as it happens.", "zh": "善用你能掌控的，其餘的就順其自然。", "source": "Epictetus《手冊》Enchiridion，第一章"},
    {"text": "It's not what happens to you, but how you react to it that matters.", "zh": "重要的不是發生了什麼，而是你如何回應。", "source": "Epictetus《手冊》Enchiridion，第五章"},
    {"text": "Seek not that the things which happen should happen as you wish; but wish the things which happen to be as they are, and you will have a tranquil flow of life.", "zh": "不要期望事情按你所願發生，而是願意接受事情本來的樣子，你將擁有平靜的人生。", "source": "Epictetus《手冊》Enchiridion，第八章"},

    # ── 做自己的生命設計師（2）──
    {"text": "我們要從現在的立足點出發，而不是從自己想抵達的地方出發，更不是從自認為該在的地方出發。一定要從腳下的這塊地出發。", "zh": None, "source": "Bill Burnett & Dave Evans《做自己的生命設計師》Designing Your Life"},
    {"text": "一旦開始設計一件事，那件事就能改變未來。", "zh": None, "source": "Bill Burnett & Dave Evans《做自己的生命設計師》Designing Your Life"},
]


def get_solar_term(today: datetime.date) -> str:
    return SOLAR_TERMS.get(today.year, {}).get((today.month, today.day), "")


def get_lunar_date(today: datetime.date) -> str:
    try:
        from lunardate import LunarDate
        lunar = LunarDate.fromSolarDate(today.year, today.month, today.day)
        month_ch = ["正","二","三","四","五","六","七","八","九","十","十一","十二"]
        day_ch = ["初一","初二","初三","初四","初五","初六","初七","初八","初九","初十",
                  "十一","十二","十三","十四","十五","十六","十七","十八","十九","二十",
                  "廿一","廿二","廿三","廿四","廿五","廿六","廿七","廿八","廿九","三十"]
        leap = "閏" if lunar.isLeapMonth else ""
        return f"農曆 {leap}{month_ch[lunar.month-1]}月{day_ch[lunar.day-1]}"
    except Exception:
        return ""


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
                        if start.endswith("Z"):
                            dt = datetime.datetime.strptime(start[:15], "%Y%m%dT%H%M%S")
                            dt = dt.replace(tzinfo=datetime.timezone.utc).astimezone(TAIPEI)
                        else:
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

    question = ""
    if api_key:
        client = anthropic.Anthropic(api_key=api_key)
        text = quote["text"]
        source = quote["source"]
        try:
            msg = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=80,
                messages=[{
                    "role": "user",
                    "content": (
                        f"這句話：「{text}」（出自 {source}）\n"
                        "請根據這句話，用繁體中文寫一個引導自我探索的問題，30 字以內，"
                        "語氣溫和像在邀請對話，直接輸出問題（含問號），不要任何前綴。"
                    ),
                }],
            )
            question = msg.content[0].text.strip()
        except Exception as e:
            print(f"Claude API error (question): {e}")

    return {**quote, "question": question}


def generate_html(today: datetime.date, events: list[dict], quote: dict,
                  lunar_date: str = "", solar_term: str = "") -> str:
    date_str = today.strftime("%Y 年 %m 月 %d 日")
    weekdays = ["一", "二", "三", "四", "五", "六", "日"]
    weekday = weekdays[today.weekday()]
    day_num = today.strftime("%d")
    month_en = today.strftime("%B").upper()
    year_num = today.strftime("%Y")

    if events:
        items_html = "".join(
            f'<li><span class="time">{e["time"]}</span><span class="event-title">{e["summary"]}</span></li>'
            for e in events
        )
        schedule_html = f'<ul class="events">{items_html}</ul>'
    else:
        schedule_html = '<p class="free-text">今日行程空白，好好留白。</p>'

    q_text = quote["text"]
    q_zh = quote.get("zh") or ""
    q_question = quote.get("question") or ""

    zh_line = f'<p class="quote-zh">{q_zh}</p>' if q_zh else ""
    explore_line = (
        f'<div class="explore-wrap"><div class="explore-label">今日一問</div>'
        f'<p class="explore-text">{q_question}</p></div>'
    ) if q_question else ""

    lunar_html = ""
    if lunar_date or solar_term:
        badge_html = f'<span class="solar-badge">{solar_term}</span>' if solar_term else ""
        lunar_html = f'<div class="lunar-row"><span class="lunar-date">{lunar_date}</span>{badge_html}</div>'

    return f"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Bella's LifeOS｜{date_str}</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400;0,500;1,400&family=Noto+Sans+TC:wght@300;400&family=Noto+Serif+TC:wght@300;400;600&display=swap');
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: "Noto Serif TC", "Songti TC", "Georgia", serif;
      background: #E8E0D5;
      color: #2C2318;
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 2rem 1rem;
    }}
    .page {{
      background: #F7F2EA;
      max-width: 460px;
      width: 100%;
      box-shadow: 0 2px 4px rgba(44,35,24,0.08), 0 12px 40px rgba(44,35,24,0.15);
    }}
    .rings {{
      display: flex;
      justify-content: center;
      gap: 2.8rem;
      padding: 0.7rem 0;
      background: #D4C8BC;
      border-bottom: 1px solid #BFB0A0;
    }}
    .ring {{
      width: 16px;
      height: 16px;
      border-radius: 50%;
      background: #F7F2EA;
      border: 2px solid #A89278;
      box-shadow: inset 0 1px 3px rgba(44,35,24,0.25);
    }}
    .cal-header {{
      padding: 2rem 2.5rem 1.5rem;
      text-align: center;
    }}
    .month-label {{
      font-size: 0.62rem;
      letter-spacing: 0.45em;
      color: #8B3A2A;
      font-family: -apple-system, "PingFang TC", sans-serif;
      font-weight: 500;
      margin-bottom: 0.4rem;
    }}
    .day-number {{
      font-size: 5.5rem;
      font-weight: 300;
      color: #2C2318;
      line-height: 0.9;
      letter-spacing: -0.04em;
      margin-bottom: 0.45rem;
    }}
    .weekday-label {{
      font-size: 0.68rem;
      color: #8A7B68;
      letter-spacing: 0.25em;
      font-family: -apple-system, "PingFang TC", sans-serif;
      margin-bottom: 0.7rem;
    }}
    .lunar-row {{
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 0.5rem;
    }}
    .lunar-date {{
      font-size: 0.62rem;
      color: #8A7B68;
      letter-spacing: 0.08em;
      font-family: -apple-system, "PingFang TC", sans-serif;
    }}
    .solar-badge {{
      display: inline-block;
      font-size: 0.58rem;
      color: #F7F2EA;
      background: #8B3A2A;
      padding: 0.1rem 0.5rem;
      letter-spacing: 0.12em;
      font-family: -apple-system, "PingFang TC", sans-serif;
    }}
    .wave-sep {{
      display: block;
      width: 100%;
      height: 10px;
    }}
    .body {{
      padding: 1.6rem 2.5rem 2rem;
    }}
    .section-label {{
      font-size: 0.58rem;
      letter-spacing: 0.35em;
      color: #8B3A2A;
      font-family: -apple-system, "PingFang TC", sans-serif;
      margin-bottom: 1rem;
      display: flex;
      align-items: center;
      gap: 0.7rem;
    }}
    .section-label::after {{
      content: '';
      flex: 1;
      height: 1px;
      background: #C4B5A0;
    }}
    .events {{ list-style: none; }}
    .events li {{
      display: flex;
      gap: 0.9rem;
      align-items: baseline;
      padding: 0.5rem 0;
      border-bottom: 1px dashed #D4C8BC;
    }}
    .events li:last-child {{ border-bottom: none; }}
    .time {{
      font-size: 0.68rem;
      color: #8B3A2A;
      min-width: 36px;
      font-variant-numeric: tabular-nums;
      font-family: -apple-system, "PingFang TC", sans-serif;
      flex-shrink: 0;
    }}
    .event-title {{
      font-size: 0.88rem;
      line-height: 1.6;
      color: #2C2318;
      font-weight: 300;
    }}
    .free-text {{
      font-size: 0.85rem;
      color: #A89278;
      font-style: italic;
      padding: 0.3rem 0;
      font-weight: 300;
    }}
    .section-gap {{
      margin-top: 1.6rem;
    }}
    .quote-area {{ text-align: center; }}
    .quote-text {{
      font-family: "Lora", "Noto Serif TC", serif;
      font-size: 0.88rem;
      line-height: 2;
      color: #2C2318;
      font-weight: 400;
      letter-spacing: 0.02em;
    }}
    .quote-zh {{
      font-size: 0.83rem;
      line-height: 1.9;
      color: #5A4A38;
      margin-top: 0.6rem;
      font-weight: 300;
    }}
    .explore-wrap {{
      margin-top: 1.3rem;
      padding: 0.85rem 1.1rem;
      background: #EDE8DC;
      border-left: 2px solid #8B3A2A;
      text-align: left;
    }}
    .explore-label {{
      font-size: 0.55rem;
      letter-spacing: 0.3em;
      color: #8B3A2A;
      font-family: -apple-system, "PingFang TC", sans-serif;
      margin-bottom: 0.5rem;
    }}
    .explore-text {{
      font-family: "Noto Sans TC", "PingFang TC", sans-serif;
      font-size: 0.78rem;
      color: #3A2510;
      line-height: 1.9;
      font-weight: 300;
    }}
    .footer {{
      padding: 0.85rem 2.5rem;
      border-top: 1px solid #BFB0A0;
      text-align: center;
      font-size: 0.55rem;
      color: #A89278;
      letter-spacing: 0.15em;
      font-family: -apple-system, "PingFang TC", sans-serif;
      background: #EFE8DF;
    }}
  </style>
</head>
<body>
  <div class="page">
    <div class="rings">
      <div class="ring"></div>
      <div class="ring"></div>
      <div class="ring"></div>
      <div class="ring"></div>
      <div class="ring"></div>
    </div>
    <div class="cal-header">
      <div class="month-label">{month_en} · {year_num}</div>
      <div class="day-number">{day_num}</div>
      <div class="weekday-label">星期{weekday}</div>
      {lunar_html}
    </div>
    <svg class="wave-sep" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 460 10" preserveAspectRatio="none">
      <path d="M0,5 C23,2 46,8 69,5 C92,2 115,8 138,5 C161,2 184,8 207,5 C230,2 253,8 276,5 C299,2 322,8 345,5 C368,2 391,8 414,5 C437,2 460,8 460,5" stroke="#C4B5A0" stroke-width="1.5" fill="none"/>
    </svg>
    <div class="body">
      <div class="section-label">今日行程</div>
      {schedule_html}
      <div class="quote-area section-gap">
        <div class="section-label">今日金句</div>
        <p class="quote-text">{q_text}</p>
        {zh_line}
        {explore_line}
      </div>
    </div>
    <div class="footer">BELLA'S LIFEOS · 每小時自動更新</div>
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
    lunar_date = get_lunar_date(today)
    solar_term = get_solar_term(today)

    html = generate_html(today, events, quote, lunar_date, solar_term)

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Generated index.html — {len(events)} events, quote: {quote['source']}")


if __name__ == "__main__":
    main()
