import re
import json
import gzip
import pickle
from collections import defaultdict, Counter
from itertools import combinations

import pandas as pd
import numpy as np

from util import normalize_html_tag, normalize_markup, is_ignore_pages, is_number_or_year


np.random.seed(42)

entity2mention = defaultdict(list)
mention2entity = defaultdict(set)
with gzip.open("jawiki-20200224-cirrussearch-content.json.gz") as f:
    for line in f:
        json_line = json.loads(line)
        if "index" not in json_line:
            doc = json_line

            for link in re.findall("\[\[(.*?)\]\]", doc["source_text"]):
                if is_ignore_pages(link):
                    continue

                link = normalize_markup(link)
                link = normalize_html_tag(link)

                if "|" not in link:
                    entity2mention["Entity_" + link].append(link)
                    mention2entity[link].add("Entity_" + link)
                else:
                    if len(link.split("|")) != 2:
                        print("https://ja.wikipedia.org/wiki/" + doc["title"], "//", link)
                        continue

                    entity, mention = link.split("|")
                    entity2mention["Entity_" + entity].append(mention)
                    mention2entity[mention].add("Entity_" + entity)

n_entity2mention = len(entity2mention)
n_mention2entity = len(mention2entity)
print(f"Size of entity: {n_entity2mention}")
print(f"Size of mention: {n_mention2entity}")

# 特定Entityを削除
delete_entities = []
delete_entities.append("Entity_#外部リンク")
delete_entities.append("Entity_#年表")

for entity, _ in entity2mention.items():
    # 1文字のEntityを除去
    if len(entity.replace("Entity_", "")) == 1:
        delete_entities.append(entity)
    # 数字や年、日付を除去
    if is_number_or_year(entity, is_entity=True):
        delete_entities.append(entity)
    # 日本語以外のEntityを除去
    if re.match(r"^Entity_:?\w{1,2}:", entity):
        delete_entities.append(entity)
    if re.match(r"^Entity_#.*", entity):
        delete_entities.append(entity)


for delete_entity in delete_entities:
    if delete_entity in entity2mention:
        del entity2mention[delete_entity]

print("# Remove specific entities")
print(f"Size of entity: {n_entity2mention} -> {len(entity2mention)}")

# entityに対してのmentionが`n_below`件以上あるものだけを抽出
n_below = 5
entity2mention_filtered = defaultdict(set)
for entity, mentions in entity2mention.items():
    m_counter = Counter(mentions)
    for m, count in m_counter.most_common():
        if count >= n_below:
            entity2mention_filtered[entity].add(m)

# 上記で抽出したentityに対応するmentionだけを抽出
# 数字や年、日付のmentionを除去
mention2entity_filtered = defaultdict(set)
for mention, entities in mention2entity.items():
    if is_number_or_year(mention, is_entity=False):
        continue
    for entity in entities:
        if entity in entity2mention_filtered.keys():
            mention2entity_filtered[mention].add(entity)

print("# Filtered mentions with lower than `n_below` and thier entities")
print(f"Size of entity: {n_entity2mention} -> {len(entity2mention)} -> {len(entity2mention_filtered)}")
print(f"Size of mention: {n_mention2entity} -> {len(mention2entity)} -> {len(mention2entity_filtered)}")

# save as pkl
with open("alias_mention/data/entity2mention.pkl", "wb") as f:
    pickle.dump(entity2mention_filtered, f)

with open("alias_mention/data/mention2entity.pkl", "wb") as f:
    pickle.dump(mention2entity_filtered, f)
