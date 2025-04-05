# -*- coding: utf-8 -*-
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# 读取分词后的文本文件，跳过标题行
text_file = 'updated_file.csv'  # 你的分词结果文件路径
df = pd.read_csv(text_file, header=0)  # header=0 表示跳过第一行作为标题

# 读取词汇表
vocab_file = 'vocabulary.txt'  # 你的词汇表文件路径
vocab_df = pd.read_csv(vocab_file, sep='\t')  # 读取带有性别和类别的词汇表

# 打印列名，确认数据是否正确
print(df.columns)

# 获取每个词的性别相关信息，整理出女性相关词汇和男性相关词汇
female_words = vocab_df[vocab_df['Gender'] == 'Female']['Term'].tolist()
male_words = vocab_df[vocab_df['Gender'] == 'Male']['Term'].tolist()

# 设置中文字体路径，确保词云显示中文
font_path = 'C:/Windows/Fonts/Simsun.ttc'  # 这里是你电脑上 SimSun 字体的路径，确保路径正确
# 创建一个列表来存储分词后的女性和男性词汇
female_related_tokens = set()  # 使用 set 来去重
male_related_tokens = set()  # 使用 set 来去重

# 遍历分词数据，提取与女性和男性相关的词汇
for row in df.itertuples():
    text = getattr(row, 'cleaned_texts', '')  # 获取清洗后的文本
    # 检查文本是否有效
    if pd.notna(text) and isinstance(text, str):  # 确保文本是字符串且非空
        tokens = text.split(',')  # 假设词语是逗号分隔的
        for word in tokens:
            if word in female_words:
                female_related_tokens.add(word)  # 使用 set 自动去重
            elif word in male_words:
                male_related_tokens.add(word)  # 使用 set 自动去重

# 将女性和男性相关词汇分别拼接成一个字符串
female_text = ' '.join(female_related_tokens)
male_text = ' '.join(male_related_tokens)

# 生成女性词云
female_wordcloud = WordCloud(width=800, height=400, background_color='white', font_path=font_path).generate(female_text)

# 生成男性词云
male_wordcloud = WordCloud(width=800, height=400, background_color='white', font_path=font_path).generate(male_text)

# 可视化女性词云
plt.figure(figsize=(10, 5))
plt.imshow(female_wordcloud, interpolation='bilinear')
plt.axis('off')  # 关闭坐标轴
plt.title('Female-related Words WordCloud')
plt.show()

# 可视化男性词云
plt.figure(figsize=(10, 5))
plt.imshow(male_wordcloud, interpolation='bilinear')
plt.axis('off')  # 关闭坐标轴
plt.title('Male-related Words WordCloud')
plt.show()

# 可选：保存词云为图片文件
female_wordcloud.to_file('female_wordcloud.png')
male_wordcloud.to_file('male_wordcloud.png')
