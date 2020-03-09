from util import normalize_html_tag, normalize_markup, is_ignore_pages, is_complete_substring, is_number_or_year


def test_normalize_html_tag():
    assert normalize_html_tag("テスト") == "テスト"
    assert normalize_html_tag("PAST < FUTURE") == "PAST < FUTURE"
    assert normalize_html_tag("美男<イケメン>ですね～Fabulous★Boys（台湾リメイク版）") == "美男<イケメン>ですね～Fabulous★Boys（台湾リメイク版）"
    assert normalize_html_tag("SKE48「未来とは?<初回盤A>」のブックレット") == "SKE48「未来とは?<初回盤A>」のブックレット"
    assert normalize_html_tag("誓い < Gabber's hands up remix>") == "誓い < Gabber's hands up remix>"
    assert normalize_html_tag("W-KEYAKIZAKAの詩<32人ver.>") == "W-KEYAKIZAKAの詩<32人ver.>"

    assert normalize_html_tag("α<sub>1A</sub>") == "α1A"
    assert normalize_html_tag("実行<br>ユニット") == "実行ユニット"
    assert normalize_html_tag("<span style=""font-size:0.9em; color:goldenrod;"">ネヴェス</span>") == "ネヴェス"
    assert normalize_html_tag("与<br />四<br />球") == "与四球"
    assert normalize_html_tag("<span style=""color: black;"">'''羅甸県'''</span>") == "'''羅甸県'''"
    assert normalize_html_tag("江 <small>〜姫たちの戦国〜") == "江 〜姫たちの戦国〜"
    assert normalize_html_tag(
        "夏の憂鬱 <nowiki>[</nowiki>time to say good-bye<nowiki>]</nowiki>") == "夏の憂鬱 [time to say good-bye]"
    assert normalize_html_tag("2005年8月13日</ref>。") == "2005年8月13日。"
    assert normalize_html_tag("サンクト<BR>ペテルブルク") == "サンクトペテルブルク"
    assert normalize_html_tag("<ruby><rb>未亡人</rb><rp>（</rp><rt>ごけ</rt><rp>）</rp></ruby>ごろしの帝王") == "未亡人（ごけ）ごろしの帝王"
    assert normalize_html_tag(":en:tzarina<!-- 存在せずリンク元がない -->") == ":en:tzarina"
    assert normalize_html_tag("''R''<sub>⊕</sub>") == "''R''⊕"
    assert normalize_html_tag(":en:David Deutsch<!-- [[:ja:デイヴィッド・ドイッチュ") == ":en:David Deutsch"
    assert normalize_html_tag('郭務<span lang="zh">悰</span>') == "郭務悰"
    assert normalize_html_tag("ユダヤ系<ref>[[筒井功") == "ユダヤ系[[筒井功"
    assert normalize_html_tag("<nowiki/>") == ""
    assert normalize_html_tag("ハミルトニアン<math>H</math>") == "ハミルトニアンH"
    assert normalize_html_tag("<center>[[大脇英夫") == "[[大脇英夫"
    assert normalize_html_tag("<s>カヌー</s>") == "カヌー"


def test_normalize_markup():
    assert normalize_markup("'''BPP'''") == "BPP"
    assert normalize_markup("''Molecular Phylogenetics and Evolution''") == "Molecular Phylogenetics and Evolution"


def test_is_ignore_pages():
    # "Entity_"を付与する前の処理
    assert is_ignore_pages(":ファイル:ICCard Connection.svg") == True
    assert is_ignore_pages("ファイル:ICCard Connection.svg") == True
    assert is_ignore_pages(":Template:Infobox 作家/doc") == True
    assert is_ignore_pages(":wikt:陸") == True
    assert is_ignore_pages("Wikipedia:リダイレクト#ループするリンク、重複するリンクを作成しない") == True

    assert is_ignore_pages("テンプレートエンジン") == False
    assert is_ignore_pages("チャンピオンジョッキー:ギャロップレーサー&ジーワンジョッキー") == False
    assert is_ignore_pages("CSI:ニューヨーク") == False
    assert is_ignore_pages("Entity_UTC+5:30") == False


def test_is_complete_substring():
    assert is_complete_substring("9000系", "南海9000系電車") == True
    assert is_complete_substring("900系", "南海9000系電車") == False
    assert is_complete_substring("2011年", "2011年12月11日") == True
    assert is_complete_substring("2011年10月", "2011年12月11日") == False
    assert is_complete_substring("高速4号線", "4号線") == True
    assert is_complete_substring("高速4号線", "4号線1番") == False


def test_is_number_or_year():
    assert is_number_or_year("1986") == True
    assert is_number_or_year("1986年") == True
    assert is_number_or_year("10") == True
    assert is_number_or_year("19860101") == True
    assert is_number_or_year("'06") == True  # 'が先頭に付く場合
    assert is_number_or_year("07月15日") == True
    assert is_number_or_year("7月5日") == True
    assert is_number_or_year(" 7月5日") == True

    assert is_number_or_year("Entity_1986年", is_entity=True) == True
    assert is_number_or_year("Entity_5月3日_(旧暦)", is_entity=True) == True
    assert is_number_or_year("Entity_11月5日#記念日・年中行事", is_entity=True) == True
    assert is_number_or_year("Entity_ 7月5日", is_entity=True) == True

    assert is_number_or_year("1Q86") == False
    assert is_number_or_year("世にも奇妙な物語 '06秋の特別編") == False
    assert is_number_or_year("05系") == False
    assert is_number_or_year("2017年アジア冬季競技大会") == False
    assert is_number_or_year("Entity_10月14日の戦車戦#イスラエル軍の配備", is_entity=True) == False
    assert is_number_or_year("Entity_1996年アメリカ合衆国大統領選挙", is_entity=True) == False
