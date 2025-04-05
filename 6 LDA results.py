# -*- coding: utf-8 -*-
import pandas as pd
from gensim import corpora
from gensim.models import LdaModel
from gensim.models import CoherenceModel
import matplotlib.pyplot as plt

def train_and_save_lda_model(filename, num_topics, no_below=10, no_above=0.5):
    # 读取清洗后的文本数据
    try:
        df = pd.read_csv(filename)
    except FileNotFoundError:
        print(f"文件 {filename} 不存在，请检查路径。")
        return

    # 确保数据格式正确
    if 'cleaned_texts' not in df.columns:
        raise ValueError("CSV文件中没有'cleaned_texts'列，请检查输入文件。")

    # 提取文本数据，去除缺失值并确保每个值是字符串
    texts = df['cleaned_texts'].dropna().astype(str).tolist()
    texts = [text.split(',') for text in texts]  # 根据逗号分隔符将文本转换为列表

    # 创建词典并过滤极端值
    dictionary = corpora.Dictionary(texts)
    dictionary.filter_extremes(no_below=no_below, no_above=no_above)

    # 创建语料库
    corpus = [dictionary.doc2bow(text) for text in texts]

    # 训练 LDA 模型
    print(f"正在训练 LDA 模型，主题数: {num_topics}")
    lda_model = LdaModel(corpus, num_topics=num_topics, id2word=dictionary, passes=10, random_state=42)

    # 保存 LDA 模型
    model_filename = filename.replace('.csv', f'-lda_model_{num_topics}_topics.model')
    lda_model.save(model_filename)
    print(f"LDA 模型已保存至: {model_filename}")
    # 保存 dictionary 和 corpus，确保完整性

    dictionary.save('dictionary.dict')
    corpus_path = 'corpus.mm'  # 使用 Matrix Market 格式
    from gensim.corpora import MmCorpus
    MmCorpus.serialize(corpus_path, corpus)

    print("模型和相关数据已保存！")

if __name__ == '__main__':
    # 输入参数
    filename = input("请输入分词结果的CSV 文件名（包含路径）：")
    num_topics = int(input("请输入主题数："))
    no_below = int(input("请输入 no_below 参数值（低频词过滤阈值，默认10）：") or 10)
    no_above = float(input("请输入 no_above 参数值（高频词过滤阈值，默认0.5）：") or 0.5)

    # 运行建模和保存
    train_and_save_lda_model(filename, num_topics, no_below, no_above)
