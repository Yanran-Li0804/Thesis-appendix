# -*- coding: utf-8 -*-
from gensim.corpora import Dictionary
from gensim.models import LdaModel
from gensim.models import CoherenceModel

import pandas as pd
import re
import jieba
import emoji
import csv
# 加载自定义词典和停用词
jieba.load_userdict(r'D:\ma\pythonProject1 自学\测试文件\playwright\custom_dict.txt')

def load_stop_words(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return set(line.strip() for line in f)

def load_synonyms(file_path):
    synonyms = {}
    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            key, value = line.strip().split(": ")
            synonyms[key] = value
    return synonyms


def clean_text(text):
    # 将文本转为小写
    text = text.lower()
    # 去除特定的文本模式
    text = re.sub(r'\[表情\]|\[图片\]|\[lbk\]|\[rbk\]|标题五个字', '', text)
    # 去除 smiley 类的 emoji 表情符号（U+1F600 - U+1F64F 和 U+1F910 - U+1F917）
    text = re.sub(r'[\U0001F600-\U0001F637'
                  r'\U0001F60A-\U0001F60F'
                  r'\U0001F61A-\U0001F61F'
                  r'\U0001F62A-\U0001F62F'
                  r'\U0001F641-\U0001F644'
                  r'\U0001F910-\U0001F917'
                  r'\U0001F920\U0001F922-\U0001F925\U0001F927-\U0001F929'
                  r'\U0001F92A-\U0001F92F'
                  r'\U0001F970-\U0001F976\U0001F97A\U0001F9D0]', '', text)
    # 移除所有数字
    text = re.sub(r'\d+', '', text)
    # 清除多余的空白符
    return re.sub(r'\s+', ' ', text).strip()

# 获取文件名的输入
input_file = input("请输入要读取的 CSV 文件名（包含扩展名，例如 '0819-0919.csv'）：")
output_file_part1 = input("请输入第一个中间结果 CSV 文件名（例如 '分词_0819-0919.csv'）：")
output_file_final = input("请输入最终输出的 CSV 文件名（例如 'final分词_0819-0926.csv'）：")

# 1. 数据读取
df = pd.read_csv(input_file)

# 2. 数据清洗
df['title'] = df['title'].fillna('').astype(str)
df['content'] = df['content'].fillna('').astype(str)
df['combined'] = df['title'] + " " + df['content']

# 加载停用词和同义词
stop_words = load_stop_words('stop_words.txt')
synonyms_dict = load_synonyms("synonyms.txt")

# 分词处理
def tokenize_and_clean(df):
    cleaned_texts = []
    for index, row in df.iterrows():
        text = clean_text(row['combined'])
        words = [synonyms_dict.get(word, word) for word in jieba.cut(text) if word not in stop_words]
        cleaned_texts.append([word for word in words if word.strip()])  # 移除空字符串
    return cleaned_texts

cleaned_texts = tokenize_and_clean(df)

# 保存处理后的结果到中间文件
pd.DataFrame({'cleaned_texts': cleaned_texts}).to_csv(output_file_part1, index=False, encoding='utf-8-sig')

# 处理包含 emoji 的分词结果
def process_emojis(df):
    cleaned_texts = []
    for index, row in df.iterrows():
        text_with_emojis = row['cleaned_texts'].strip()
        if text_with_emojis:
            text_converted = emoji.demojize(text_with_emojis)
            try:
                words = eval(text_converted)  # 转换为列表格式
                filtered_words = [re.sub(r'[^a-zA-Z0-9\u4e00-\u9fff\u2700-\u27BF\u1F300-\u1F5FF\u1F680-\u1F6FF\u1F700-\u1F77F\s]', '', word)
                                  for word in words if len(word) > 1]  # 筛选长度大于 1 的词汇
                cleaned_texts.append([emoji.emojize(word) if ":" in word else word for word in filtered_words])
            except Exception as e:
                print(f"Error processing row {index}: {e}")
                cleaned_texts.append([])  # 如果出错，保留一个空列表
    return cleaned_texts

# 读取中间文件
df = pd.read_csv(output_file_part1)
if 'cleaned_texts' not in df.columns:
    raise ValueError("CSV文件中没有'cleaned_texts'列")

# 处理表情符号
final_cleaned_texts = process_emojis(df)

# 去除全空行并保存结果到最终文件
final_cleaned_df = pd.DataFrame(final_cleaned_texts).dropna(how='all')

# 确保每一行都是一个字符串而不是列表，并去除引号
final_cleaned_df['cleaned_texts'] = final_cleaned_df.apply(lambda x: ','.join(filter(None, x.dropna())), axis=1)

# 保存最终结果到用户指定的 CSV 文件，并添加表头
final_cleaned_df[['cleaned_texts']].to_csv(output_file_final, index=False, header=True, encoding='utf-8')

print(f"处理完成，结果已保存到 '{output_file_final}'")
