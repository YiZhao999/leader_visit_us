import os
import numpy as np
import pandas as pd


'line: lines after the initial process, usually include date and activity information'


def remove_nan(line):
    droplist = list(line.index[line.text.isna()])
    df = line.drop(droplist)
    df = df.reset_index()
    df = df.drop('index', axis=1)
    return df


def remove_some_texts(line, texts):
    droplist = []
    for i, t in enumerate(line.text):
        if texts in t:
            droplist.append(i)
    df = line.drop(droplist)
    df = df.reset_index()
    df = df.drop('index', axis=1)
    return df


def remove_all_caps(line):
    droplist = []
    for i, t in enumerate(line.text):
        if t.isupper():
            droplist.append(i)
    df = line.drop(droplist)
    df = df.reset_index()
    df = df.drop('index', axis=1)
    return df


def remove_links(line):
    droplist = []
    for i, t in enumerate(line.text):
        if t[:10] == 'here<https' or t[:8] == 'http://':
            if 'www.state.gov/' not in t:
                droplist.append(i)
    df = line.drop(droplist)
    df = df.reset_index()
    df = df.drop('index', axis=1)
    return df


def remove_duplicates(line):
    unique = list(set(line.text))
    dup_t = []
    dup_v = []
    for u in unique:
        l = sum(line.text == u)
        p = np.arange(len(line.text))[line.text == u]
        if l > 1:
            dup_t.append(u)
            dup_v.append(p)
    dup = pd.DataFrame(dup_t, columns=['texts'])
    dup['position'] = dup_v
    droplist = []
    for pos in dup.position:
        droplist = droplist + list(pos[:-1])
    df = df.reset_index()
    df = df.drop('index', axis=1)
    return df
