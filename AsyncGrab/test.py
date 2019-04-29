#-*-coding:utf-8-*-
#@author:lijinxi
from collections import Counter

words = []
with open('data.txt', 'w', encoding='utf-8') as f:
    for i in f:
        words.append(i[3:len(i) - 3])
num = len(words)
word_counts = Counter(words)
top_one = word_counts.most_common(1)
