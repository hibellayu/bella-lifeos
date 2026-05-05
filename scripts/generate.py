import os
import datetime
import random
import urllib.request
from zoneinfo import ZoneInfo
import anthropic

TAIPEI = ZoneInfo("Asia/Taipei")

# 精選語錄庫 100 句：所有引用均有明確出處，涵蓋哲學、心理學、佛學、禪宗、道教、文學
QUOTES = [
    # ── 一行禪師（12）──
    {"text": "The present moment is the only moment available to us, and it is the door to all moments.", "zh": "當下這一刻是我們唯一擁有的，也是通往一切時刻的門。", "source": "一行禪師《正念的奇蹟》The Miracle of Mindfulness"},
    {"text": "Smile, breathe and go slowly.", "zh": "微笑，呼吸，慢慢走。", "source": "一行禪師《步步安樂行》Peace Is Every Step"},
    {"text": "The most precious gift we can offer anyone is our attention.", "zh": "我們能給予他人最珍貴的禮物，是我們的專注與臨在。", "source": "一行禪師《與自己和好》Being Peace"},
    {"text": "Because you are alive, everything is possible.", "zh": "因為你還活著，一切皆有可能。", "source": "一行禪師《沒有泥土，就沒有蓮花》No Mud, No Lotus"},
    {"text": "Walk as if you are kissing the Earth with your feet.", "zh": "行走時，如同用你的雙腳親吻大地。", "source": "一行禪師《步步安樂行》Peace Is Every Step"},
    {"text": "Sometimes your joy is the source of your smile, but sometimes your smile can be the source of your joy.", "zh": "有時是喜悅帶來微笑，但有時，是微笑帶來喜悅。", "source": "一行禪師《正念的奇蹟》The Miracle of Mindfulness"},
    {"text": "To be beautiful means to be yourself. You don't need to be accepted by others. You need to accept yourself.", "zh": "美麗意味著做你自己。你不需要被他人接受，你需要接受自己。", "source": "一行禪師《真愛》True Love"},
    {"text": "Letting go gives us freedom, and freedom is the only condition for happiness.", "zh": "放下給予我們自由，而自由是幸福的唯一條件。", "source": "一行禪師《佛陀之心》The Heart of the Buddha's Teaching"},
    {"text": "The seed of suffering in you may be strong, but don't wait until you have no more suffering before allowing yourself to be happy.", "zh": "你內心痛苦的種子也許很強，但別等到痛苦全消才讓自己快樂。", "source": "一行禪師《沒有泥土，就沒有蓮花》No Mud, No Lotus"},
    {"text": "Drink your tea slowly and reverently, as if it is the axis on which the world earth revolves.", "zh": "慢慢地、虔誠地喝你的茶，彷彿它是世界轉動的軸心。", "source": "一行禪師《享受》Savor"},
    {"text": "People usually consider walking on water or in thin air a miracle. But I think the real miracle is to walk on earth.", "zh": "人們常把在水上行走視為奇蹟，但我認為真正的奇蹟，是在大地上行走。", "source": "一行禪師《正念的奇蹟》The Miracle of Mindfulness"},
    {"text": "In true love, you attain freedom.", "zh": "在真愛之中，你獲得自由。", "source": "一行禪師《真愛》True Love"},

    # ── 道德經・老子（8）──
    {"text": "知人者智，自知者明。勝人者有力，自勝者強。", "zh": None, "source": "老子《道德經》第三十三章"},
    {"text": "上善若水。水善利萬物而不爭，處衆人之所惡，故幾於道。", "zh": None, "source": "老子《道德經》第八章"},
    {"text": "致虛極，守靜篤。萬物並作，吾以觀復。", "zh": None, "source": "老子《道德經》第十六章"},
    {"text": "為學日益，為道日損。損之又損，以至於無為。無為而無不為。", "zh": None, "source": "老子《道德經》第四十八章"},
    {"text": "信言不美，美言不信。善者不辯，辯者不善。", "zh": None, "source": "老子《道德經》第八十一章"},
    {"text": "曲則全，枉則直，窪則盈，弊則新，少則得，多則惑。", "zh": None, "source": "老子《道德經》第二十二章"},
    {"text": "知足者富。", "zh": None, "source": "老子《道德經》第三十三章"},
    {"text": "天下莫柔弱於水，而攻堅強者莫之能勝。", "zh": None, "source": "老子《道德經》第七十八章"},

    # ── 莊子（6）──
    {"text": "相濡以沫，不如相忘於江湖。", "zh": None, "source": "莊子《大宗師》"},
    {"text": "吾生也有涯，而知也無涯。以有涯隨無涯，殆已。", "zh": None, "source": "莊子《養生主》"},
    {"text": "天地有大美而不言，四時有明法而不議，萬物有成理而不說。", "zh": None, "source": "莊子《知北遊》"},
    {"text": "至人無己，神人無功，聖人無名。", "zh": None, "source": "莊子《逍遙遊》"},
    {"text": "獨與天地精神往來，而不傲倪於萬物。", "zh": None, "source": "莊子《天下篇》"},
    {"text": "夫大道不稱，大辯不言，大仁不仁，大廉不嗛，大勇不忮。", "zh": None, "source": "莊子《齊物論》"},

    # ── 禪宗（6）──
    {"text": "菩提本無樹，明鏡亦非台。本來無一物，何處惹塵埃。", "zh": None, "source": "惠能《六祖壇經·行由品》"},
    {"text": "日日是好日。", "zh": None, "source": "雲門文偃禪師，收錄於《碧巖錄》第六則"},
    {"text": "春有百花秋有月，夏有涼風冬有雪。若無閒事掛心頭，便是人間好時節。", "zh": None, "source": "無門慧開《無門關·頌》"},
    {"text": "平常心是道。", "zh": None, "source": "馬祖道一禪師，《景德傳燈錄》卷六"},
    {"text": "不思善，不思惡，正恁麼時，那個是明上座本來面目？", "zh": None, "source": "惠能《六祖壇經·行由品》"},
    {"text": "搬柴運水，無非妙道。", "zh": None, "source": "禪宗語錄，《景德傳燈錄》"},

    # ── 論語・孔子（6）──
    {"text": "學而不思則罔，思而不學則殆。", "zh": None, "source": "孔子《論語·為政》"},
    {"text": "吾日三省吾身：為人謀而不忠乎？與朋友交而不信乎？傳不習乎？", "zh": None, "source": "曾子語，《論語·學而》"},
    {"text": "知之為知之，不知為不知，是知也。", "zh": None, "source": "孔子《論語·為政》"},
    {"text": "己所不欲，勿施於人。", "zh": None, "source": "孔子《論語·顏淵》"},
    {"text": "三人行，必有我師焉。擇其善者而從之，其不善者而改之。", "zh": None, "source": "孔子《論語·述而》"},
    {"text": "見賢思齊焉，見不賢而內自省也。", "zh": None, "source": "孔子《論語·里仁》"},

    # ── 王陽明（3）──
    {"text": "知行合一。", "zh": None, "source": "王陽明《傳習錄》，心學核心命題"},
    {"text": "此心光明，亦復何言。", "zh": None, "source": "王陽明臨終語，《王文成公全書·年譜》"},
    {"text": "破山中賊易，破心中賊難。", "zh": None, "source": "王陽明《王文成公全書》書信"},

    # ── 佛陀・法句經 Dhammapada（5）──
    {"text": "Mind is the forerunner of all actions. All deeds are led by mind, created by mind.", "zh": "心是一切行為的先驅。一切行為皆由心引領、由心創造。", "source": "《法句經》Dhammapada，第一偈"},
    {"text": "Hatred is never appeased by hatred in this world. By non-hatred alone is hatred appeased. This is a law eternal.", "zh": "恨意永遠無法以恨化解，唯有不恨，才能平息恨意，此乃永恆之法。", "source": "《法句經》Dhammapada，第五偈"},
    {"text": "Better than a thousand hollow words is one word that brings peace.", "zh": "勝過千句空洞之言的，是一句帶來平靜的話。", "source": "《法句經》Dhammapada，第一百偈"},
    {"text": "It is easy to see the faults of others, but difficult to see one's own faults.", "zh": "見他人之過易，見自身之過難。", "source": "《法句經》Dhammapada，第二百五十二偈"},
    {"text": "All conditioned things are impermanent—when one sees this with wisdom, one turns away from suffering.", "zh": "一切有為法皆無常——以智慧觀此，即能遠離苦。", "source": "《法句經》Dhammapada，第二百七十七偈"},

    # ── Marcus Aurelius（5）──
    {"text": "You have power over your mind—not outside events. Realize this, and you will find strength.", "zh": "你能掌控的是你的心，而非外在的事件。認清這一點，你將找到力量。", "source": "Marcus Aurelius《沉思錄》Meditations，第六卷"},
    {"text": "Waste no more time arguing about what a good man should be. Be one.", "zh": "別再浪費時間爭論何謂好人，直接去做一個好人。", "source": "Marcus Aurelius《沉思錄》Meditations，第十卷"},
    {"text": "Confine yourself to the present.", "zh": "把自己限定在當下。", "source": "Marcus Aurelius《沉思錄》Meditations，第八卷"},
    {"text": "The impediment to action advances action. What stands in the way becomes the way.", "zh": "阻礙行動之物，反而推進了行動。擋路之物，即成為路本身。", "source": "Marcus Aurelius《沉思錄》Meditations，第五卷"},
    {"text": "Never let the future disturb you. You will meet it, if you have to, with the same weapons of reason which today arm you against the present.", "zh": "莫讓未來擾亂你。若必須面對，你將以同樣的理性武裝自己。", "source": "Marcus Aurelius《沉思錄》Meditations，第七卷"},

    # ── Viktor Frankl（3）──
    {"text": "When we are no longer able to change a situation, we are challenged to change ourselves.", "zh": "當我們無法改變處境時，我們被挑戰去改變自己。", "source": "Viktor Frankl《活出意義來》Man's Search for Meaning"},
    {"text": "Everything can be taken from a man but one thing: the last of the human freedoms—to choose one's attitude in any given set of circumstances.", "zh": "人可以被奪走一切，唯有一樣不能——在任何處境下選擇自己態度的自由。", "source": "Viktor Frankl《活出意義來》Man's Search for Meaning"},
    {"text": "Life is never made unbearable by circumstances, but only by lack of meaning and purpose.", "zh": "生命從不因處境而變得無法承受，唯有缺乏意義與目的，才使人難以為繼。", "source": "Viktor Frankl《活出意義來》Man's Search for Meaning"},

    # ── Epictetus（3）──
    {"text": "Make the best use of what is in your power, and take the rest as it happens.", "zh": "善用你能掌控的，其餘的就順其自然。", "source": "Epictetus《手冊》Enchiridion，第一章"},
    {"text": "It's not what happens to you, but how you react to it that matters.", "zh": "重要的不是發生了什麼，而是你如何回應。", "source": "Epictetus《手冊》Enchiridion，第五章"},
    {"text": "Seek not that the things which happen should happen as you wish; but wish the things which happen to be as they are, and you will have a tranquil flow of life.", "zh": "不要期望事情按你所願發生，而是願意接受事情本來的樣子，你將擁有平靜的人生。", "source": "Epictetus《手冊》Enchiridion，第八章"},

    # ── Seneca（3）──
    {"text": "Dum differtur vita transcurrit. (While we are postponing, life speeds by.)", "zh": "我們拖延之際，生命正在飛逝。", "source": "Seneca《致魯奇里烏斯書信集》Epistulae Morales，第一封"},
    {"text": "We suffer more in imagination than in reality.", "zh": "我們在想像中受的苦，遠多於現實。", "source": "Seneca《致魯奇里烏斯書信集》Epistulae Morales，第十三封"},
    {"text": "Omnia aliena sunt, tempus tantum nostrum est. (Everything belongs to others; time alone is ours.)", "zh": "萬物皆屬他人，唯有時間是我們的。", "source": "Seneca《致魯奇里烏斯書信集》Epistulae Morales，第一封"},

    # ── Rainer Maria Rilke（2）──
    {"text": "Be patient toward all that is unsolved in your heart and try to love the questions themselves.", "zh": "對心中一切未解的事保持耐心，試著去愛那些問題本身。", "source": "Rainer Maria Rilke《給一位年輕詩人的信》Letters to a Young Poet，第四封信"},
    {"text": "I live my life in widening circles that reach out across the world.", "zh": "我的生命在不斷擴大的圓圈中展開，延伸至整個世界。", "source": "Rainer Maria Rilke《時禱書》Book of Hours，第一卷"},

    # ── Albert Camus（2）──
    {"text": "In the midst of winter, I found there was, within me, an invincible summer.", "zh": "在嚴冬之中，我發現自己內心有一個不可征服的夏天。", "source": "Albert Camus《重返提帕薩》Return to Tipasa（1952）"},
    {"text": "One must imagine Sisyphus happy.", "zh": "我們必須想像薛西弗斯是快樂的。", "source": "Albert Camus《薛西弗斯的神話》The Myth of Sisyphus，結語"},

    # ── Carl Jung（3）──
    {"text": "Who looks outside, dreams; who looks inside, awakes.", "zh": "向外看的人在做夢；向內看的人才是清醒的。", "source": "Carl Jung 致 Fanny Bowditch 信函（1916），收錄於《榮格書信集》"},
    {"text": "Everything that irritates us about others can lead us to an understanding of ourselves.", "zh": "他人身上令我們惱怒的一切，都可以引領我們認識自己。", "source": "Carl Jung《記憶、夢、省思》Memories, Dreams, Reflections"},
    {"text": "Until you make the unconscious conscious, it will direct your life and you will call it fate.", "zh": "在你將潛意識化為意識之前，它將主導你的人生，而你會稱之為命運。", "source": "Carl Jung，收錄於《榮格文集》第十一卷"},

    # ── Khalil Gibran（4）──
    {"text": "The deeper that sorrow carves into your being, the more joy you can contain.", "zh": "悲傷在你內心挖得越深，你所能承載的喜悅就越多。", "source": "Khalil Gibran《先知》The Prophet，〈論喜與悲〉"},
    {"text": "Your pain is the breaking of the shell that encloses your understanding.", "zh": "你的痛苦，是包裹著你理解力的那個殼正在破裂。", "source": "Khalil Gibran《先知》The Prophet，〈論痛苦〉"},
    {"text": "Yesterday is but today's memory, and tomorrow is today's dream.", "zh": "昨日不過是今日的記憶，明日不過是今日的夢想。", "source": "Khalil Gibran《先知》The Prophet，〈論時間〉"},
    {"text": "You give but little when you give of your possessions. It is when you give of yourself that you truly give.", "zh": "給予財物，所給甚少；給予自己，才是真正的給予。", "source": "Khalil Gibran《先知》The Prophet，〈論給予〉"},

    # ── Brené Brown（3）──
    {"text": "Vulnerability is not winning or losing; it's having the courage to show up and be seen when we have no control over the outcome.", "zh": "脆弱不是輸贏的問題，而是在無法掌控結果時，仍有勇氣現身並讓人看見你。", "source": "Brené Brown《脆弱的力量》Daring Greatly"},
    {"text": "Owning our story and loving ourselves through that process is the bravest thing we'll ever do.", "zh": "承認自己的故事，並在這個過程中愛自己，是我們能做的最勇敢的事。", "source": "Brené Brown《不完美的禮物》The Gifts of Imperfection"},
    {"text": "Connection is why we're here. It is what gives purpose and meaning to our lives.", "zh": "連結是我們存在的理由，它賦予生命目的與意義。", "source": "Brené Brown《不完美的禮物》The Gifts of Imperfection"},

    # ── Carl Rogers（2）──
    {"text": "The curious paradox is that when I accept myself just as I am, then I can change.", "zh": "奇妙的悖論是：當我完全接受現在的自己，我才能真正改變。", "source": "Carl Rogers《成為一個人》On Becoming a Person"},
    {"text": "The only person who is educated is the one who has learned how to learn and change.", "zh": "真正受過教育的人，是那個學會了如何學習與改變的人。", "source": "Carl Rogers《學習的自由》Freedom to Learn"},

    # ── Antoine de Saint-Exupéry（3）──
    {"text": "It is only with the heart that one can see rightly; what is essential is invisible to the eye.", "zh": "唯有用心，才能看清本質；真正重要的東西，肉眼是看不見的。", "source": "Antoine de Saint-Exupéry《小王子》The Little Prince，第二十一章"},
    {"text": "You become responsible, forever, for what you have tamed.", "zh": "你要永遠對你所馴服的負責。", "source": "Antoine de Saint-Exupéry《小王子》The Little Prince，第二十一章"},
    {"text": "It is such a mysterious place, the land of tears.", "zh": "淚水之地，是如此神秘的所在。", "source": "Antoine de Saint-Exupéry《小王子》The Little Prince，第七章"},

    # ── 蘇軾（3）──
    {"text": "竹杖芒鞋輕勝馬，誰怕？一蓑煙雨任平生。", "zh": None, "source": "蘇軾《定風波·莫聽穿林打葉聲》"},
    {"text": "但願人長久，千里共嬋娟。", "zh": None, "source": "蘇軾《水調歌頭·明月幾時有》"},
    {"text": "人有悲歡離合，月有陰晴圓缺，此事古難全。", "zh": None, "source": "蘇軾《水調歌頭·明月幾時有》"},

    # ── Nietzsche（3）──
    {"text": "That which does not kill us makes us stronger.", "zh": "那些殺不死我們的，終將使我們更強大。", "source": "Friedrich Nietzsche《偶像的黃昏》Twilight of the Idols，〈格言與箭〉§8"},
    {"text": "Without music, life would be a mistake.", "zh": "沒有音樂，人生將是一個錯誤。", "source": "Friedrich Nietzsche《偶像的黃昏》Twilight of the Idols，〈格言與箭〉§33"},
    {"text": "There is always some madness in love. But there is also always some reason in madness.", "zh": "愛情中永遠有些瘋狂，瘋狂中卻也永遠有些道理。", "source": "Friedrich Nietzsche《查拉圖斯特拉如是說》Thus Spoke Zarathustra，〈論閱讀與寫作〉"},

    # ── Socrates / Plato（3）──
    {"text": "The unexamined life is not worth living.", "zh": "未經審視的人生，不值得活。", "source": "蘇格拉底語，柏拉圖《申辯篇》Apology，38a"},
    {"text": "I know that I know nothing.", "zh": "我所知道的，就是我一無所知。", "source": "蘇格拉底悖論，柏拉圖《申辯篇》Apology，21d（意譯）"},
    {"text": "Wonder is the beginning of wisdom.", "zh": "驚奇是智慧的起點。", "source": "蘇格拉底語，柏拉圖《泰阿泰德篇》Theaetetus，155d"},

    # ── Hermann Hesse（2）──
    {"text": "If you hate a person, you hate something in him that is part of yourself. What isn't part of ourselves doesn't disturb us.", "zh": "若你憎恨一個人，你是在憎恨他身上屬於你自己的某樣東西。不屬於我們的，不會讓我們不安。", "source": "Hermann Hesse《德米安》Demian"},
    {"text": "I wanted only to try to live in accord with the promptings of my true self. Why was that so very difficult?", "zh": "我只想嘗試按照內心真實的呼喚而活。為什麼這竟如此困難？", "source": "Hermann Hesse《德米安》Demian，序言"},

    # ── Dostoevsky（2）──
    {"text": "Pain and suffering are always inevitable for a large intelligence and a deep heart.", "zh": "對於一個深邃的頭腦與豐富的心靈，痛苦與磨難永遠是不可避免的。", "source": "Fyodor Dostoevsky《罪與罰》Crime and Punishment，第五部第四章"},
    {"text": "Beauty will save the world.", "zh": "美將拯救世界。", "source": "Fyodor Dostoevsky《白痴》The Idiot，第三部第五章"},

    # ── Aristotle（2）──
    {"text": "Happiness depends upon ourselves.", "zh": "幸福取決於我們自己。", "source": "Aristotle《尼各馬可倫理學》Nicomachean Ethics，第一卷"},
    {"text": "For the things we have to learn before we can do them, we learn by doing them.", "zh": "凡是我們必須先學才能做的事，我們是在做中學會的。", "source": "Aristotle《尼各馬可倫理學》Nicomachean Ethics，第二卷第一章"},

    # ── Simone Weil（2）──
    {"text": "Attention is the rarest and purest form of generosity.", "zh": "專注是最稀有、最純粹的慷慨。", "source": "Simone Weil《等待上帝》Waiting for God"},
    {"text": "The love of our neighbor in all its fullness simply means being able to say to him: 'What are you going through?'", "zh": "對鄰人完整的愛，不過是能夠問他：「你正在經歷什麼？」", "source": "Simone Weil《等待上帝》Waiting for God"},

    # ── 王維（2）──
    {"text": "行到水窮處，坐看雲起時。", "zh": None, "source": "王維《終南別業》"},
    {"text": "獨坐幽篁裡，彈琴復長嘯。深林人不知，明月來相照。", "zh": None, "source": "王維《竹里館》"},

    # ── Leo Tolstoy（2）──
    {"text": "Everyone thinks of changing the world, but no one thinks of changing himself.", "zh": "人人都想改變世界，卻沒有人想到要改變自己。", "source": "Leo Tolstoy《三種方法》Three Methods of Reform"},
    {"text": "The two most powerful warriors are patience and time.", "zh": "最強大的兩位戰士，是耐心與時間。", "source": "Leo Tolstoy《戰爭與和平》War and Peace，第三卷第二部"},
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
