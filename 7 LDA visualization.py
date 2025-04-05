# -*- coding: utf-8 -*-
import pyLDAvis
import pyLDAvis.gensim_models as gensimvis
from gensim.models import LdaModel
from gensim.corpora import Dictionary, MmCorpus
import matplotlib.pyplot as plt
# 加载模型
lda_model = LdaModel.load('final分词_20240819-20241118-lda_model_8_topics.model')

# pyLDAvis
# 加载字典和语料
dictionary = Dictionary.load('dictionary.dict')
corpus = MmCorpus('corpus.mm')
print("模型和相关数据已加载！")
# 准备数据
vis = gensimvis.prepare(lda_model, corpus, dictionary)
# 保存为 HTML 文件
pyLDAvis.save_html(vis, 'lda_vis_4_topics.html')
print("交互式可视化已保存为 lda_vis_4_topics.html")

# wordcloud
from wordcloud import WordCloud
font_path = 'C:/Windows/Fonts/Simsun.ttc'
def plot_wordcloud(lda_model, num_words=20, save_dir="wordclouds/"):
    import os
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)  # 如果保存目录不存在，创建它


    for i, topic in enumerate(lda_model.print_topics(num_words=num_words)):
        words = {word.split("*")[1].strip('"'): float(word.split("*")[0]) for word in topic[1].split(" + ")}

        wordcloud = WordCloud(width=800,
                              height=400,
                              background_color="white",
                              font_path=font_path,
                              prefer_horizontal = 1.0
                              ).generate_from_frequencies(words)
        plt.figure(figsize=(10, 6))
        plt.imshow(wordcloud, interpolation="bilinear")
        plt.axis("off")
        plt.title(f"Topic {i} WordCloud", fontsize=16)
        # 保存图片
        file_path = os.path.join(save_dir, f"topic_{i}_wordcloud.png")
        wordcloud.to_file(file_path)
        print(f"Topic {i} 词云已保存到 {file_path}")

        plt.show()
# 绘制词云
plot_wordcloud(lda_model)
