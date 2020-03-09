import regex as re
from bs4 import BeautifulSoup


def normalize_html_tag(string):
    if not "<" in string:
        return string

    # 括弧の処理
    for s in re.findall(r"<(.*?)>", string.lower()):
        # 一つでもasciiで書かれたタグっぽいものがあった場合
        if re.match(r"[a-z/\!]", s):
            return BeautifulSoup(string, "lxml").text
    if "<!--" in string:
        # コメントが正しく閉じられていない場合
        return BeautifulSoup(string, "lxml").text
    return string


def normalize_markup(s):
    # remove bold and italic markup
    # https://en.wikipedia.org/wiki/Help:HTML_in_wikitext
    s = s.replace("'''", "").replace("''", "")

    return s


def is_ignore_pages(string):
    if ":" not in string:
        return False

    ignore_set = {"ファイル", "file",
                  "カテゴリ", "category",
                  "画像", "image",
                  "template",
                  "ノート",
                  "プロジェクト",
                  "wikipedia",
                  "help",
                  "wikt", "b", "s"  # wiktionary, wikibooks, wikisource
                  }
    for ignore_word in ignore_set:
        for ignore_prefix in [ignore_word + ":", ":" + ignore_word + ":"]:
            if string.lower().startswith(ignore_prefix):
                return True
    return False


def is_complete_substring(string1, string2):
    if string1 in string2 or string2 in string1:
        return True
    else:
        return False


def is_number_or_year(string, is_entity=False):
    string = string.replace(" ", "")
    if is_entity:
        string = string.replace("Entity_", "")

    if re.match(r"^'?\d*年?$", string):
        return True
    elif re.match(r"^\d{1,2}月\d{1,2}日(\_\(旧暦\))?(#記念日・年中行事)?$", string):
        return True
    else:
        return False
