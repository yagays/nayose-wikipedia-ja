import pickle
from collections import defaultdict
from itertools import combinations, product

import numpy
import Levenshtein
import numpy as np
import pandas as pd
from tqdm import tqdm

from util import is_complete_substring

np.random.seed(42)

with open("data/entity2mention.pkl", "rb") as f:
    entity2mention = pickle.load(f)

with open("data/mention2entity.pkl", "rb") as f:
    mention2entity = pickle.load(f)

# for levenstein distance
all_mentions = list(mention2entity.keys())
mention_by_length = defaultdict(list)
for mention in tqdm(all_mentions):
    mention_by_length[len(mention)].append(mention)

# for overlap
overlap_n = 4
all_prefix = defaultdict(list)
all_suffix = defaultdict(list)
for mention in tqdm(all_mentions):
    if len(mention) < overlap_n:
        continue
    all_prefix[mention[:overlap_n]].append(mention)
    all_suffix[mention[-overlap_n:]].append(mention)

# for randomly selected
np.random.shuffle(all_mentions)
n_all_mentions = len(all_mentions)


# train/dev/test split
all_entity = list(entity2mention.keys())
np.random.shuffle(all_entity)

train, dev, test = np.split(all_entity,
                            [int(.6 * len(all_entity)),
                             int(.8 * len(all_entity))])
datasets = {"train": train, "dev": dev, "test": test}


print("make pos/neg pairs")
for dataset_name, dataset in datasets.items():
    output = []
    stats = []

    for entity in tqdm(dataset):
        entity_mentions = entity2mention[entity]

        # positive
        combination_pair = combinations(entity_mentions, 2)
        # 1文字以上重複しているもののみ抽出
        positives = [(s1, s2, 1, "positive", entity) for s1, s2 in combination_pair if set(s1) & set(s2)]

        if not positives:
            # pos/negの候補を作れない場合
            continue

        # negative
        n_negative = len(positives)
        negative_candidate = {}

        negative_leven = []
        negative_overlap = []
        negative_alias = []
        for mention in entity_mentions:
            # 0: Levenstein dist. of 1 or 2
            if len(mention) <= 2:
                continue
            for m in mention_by_length[len(mention)]:
                if Levenshtein.distance(mention, m) <= 2 and len(mention2entity[mention] & mention2entity[m]) == 0:
                    negative_leven.append((mention, m, 0, "levenstein", entity))

            # 1: 4-gram overlap
            negative_overlap += [(mention, m, 0, "overlap", entity) for m in all_prefix[mention[:overlap_n]]]
            negative_overlap += [(mention, m, 0, "overlap", entity) for m in all_suffix[mention[-overlap_n:]]]

            # 2: Alias of true positives
            other_entity = mention2entity[mention]
            if entity in other_entity:
                other_entity.remove(entity)
            if len(other_entity) >= 1:
                for negative_entity in other_entity:
                    candidate_negative_mention = entity2mention[negative_entity]
                    for negative_mention in candidate_negative_mention:
                        if negative_mention not in entity_mentions and set(negative_mention) and set(mention):
                            negative_alias.append((mention,
                                                   negative_mention,
                                                   0,
                                                   "alias_of_tp",
                                                   f"{entity}_{negative_entity}"))

        # 3: randomly selected (select up to `n_negative`)
        random_index = np.random.randint(n_all_mentions)
        random_mention_pair = []
        n_random_mention = 0
        while n_negative >= n_random_mention:
            candidate_mention = all_mentions[random_index]
            if candidate_mention not in entity_mentions:
                for s1, s2 in product(entity_mentions, [candidate_mention]):
                    if set(s1) & set(s2) and not is_complete_substring(s1, s2):
                        random_mention_pair.append((s1, s2, 0, "random", entity))
                        n_random_mention += 1

            if random_index == n_all_mentions - 1:
                random_index = 0
            else:
                random_index += 1

        # filter
        negative_leven = [t for t in negative_leven if not is_complete_substring(t[0], t[1])]
        negative_overlap = [t for t in negative_overlap if not is_complete_substring(t[0], t[1])]
        negative_alias = [t for t in negative_alias if not is_complete_substring(t[0], t[1])]

        # prepare for negative sampling
        np.random.shuffle(negative_leven)
        np.random.shuffle(negative_overlap)
        np.random.shuffle(negative_alias)
        np.random.shuffle(random_mention_pair)
        negative_candidate[0] = negative_leven
        negative_candidate[1] = negative_overlap
        negative_candidate[2] = negative_alias
        negative_candidate[3] = random_mention_pair

        # sampling negatives from candidates
        negatives = []
        i = 0  # random_samplingのindex。
        random_sampling_index = np.random.choice([0, 1, 2, 3], size=100000, p=[0.25, 0.25, 0.25, 0.25])
        i_type = [0, 0, 0, 0]  # それぞれのtypeのcounter
        while n_negative > len(negatives) or i == 100001:
            target_type = random_sampling_index[i]
            if len(negative_candidate[target_type]) > i_type[target_type]:
                negatives.append(negative_candidate[target_type][i_type[target_type]])
                i_type[target_type] += 1
            i += 1

        output += positives
        output += negatives
        stats.append([
            len(negative_leven),
            len(negative_overlap),
            len(negative_alias),
            len(random_mention_pair)
        ])

    output_columns = ["lhs", "rhs", "label", "type", "comment"]
    pd.DataFrame(output, columns=output_columns).to_csv(f"alias_mention/data/{dataset_name}.tsv", index=None, sep="\t")
    pd.DataFrame(stats).to_csv(f"alias_mention/data/{dataset_name}.stats", index=None, sep="\t")
