import pandas as pd
from gensim import corpora
from gensim.models import LdaModel
from gensim.models import CoherenceModel
import matplotlib.pyplot as plt

def main(filename, num_topics_start, num_topics_end, step, no_below=10, no_above=0.5):
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

    # 初始化用于存储得分的列表
    coherence_scores = []
    perplexity_scores = []

    # 遍历不同的主题数目
    for num_topics in range(num_topics_start, num_topics_end + 1, step):
        print(f"正在训练 LDA 模型，主题数: {num_topics}")

        # 创建 LDA 模型
        lda_model = LdaModel(corpus, num_topics=num_topics, id2word=dictionary, passes=10, random_state=42)

        # 计算一致性得分
        coherence_model = CoherenceModel(model=lda_model, texts=texts, dictionary=dictionary, coherence='c_v')
        coherence_lda = coherence_model.get_coherence()
        coherence_scores.append((num_topics, coherence_lda))

        # 计算困惑度
        perplexity = lda_model.log_perplexity(corpus)
        perplexity_scores.append((num_topics, perplexity))

        print(f'num_topics: {num_topics}, c_v: {coherence_lda}, perplexity: {perplexity}')

    # 将结果写入文本文件
    output_file = filename.replace('.csv', '-lda_metrics.txt')
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("num_topics, c_v, perplexity\n")
        for num, coh, perp in zip(range(num_topics_start, num_topics_end + 1, step),
                                  [score for _, score in coherence_scores],
                                  [score for _, score in perplexity_scores]):
            f.write(f"{num}, {coh}, {perp}\n")

    print(f"一致性得分和困惑度已保存到 {output_file}")

    # 绘制主题数量与一致性得分、困惑度的关系图
    topics, coherence_vals = zip(*coherence_scores)
    _, perplexity_vals = zip(*perplexity_scores)

    plt.figure(figsize=(12, 6))
    plt.plot(topics, coherence_vals, marker='o', label='Coherence Score (c_v)')
    plt.plot(topics, perplexity_vals, marker='x', label='Perplexity', color='red')
    plt.xlabel('Number of Topics')
    plt.ylabel('Score')
    plt.title('LDA Metrics by Number of Topics')
    plt.legend()
    plt.grid(True)
    plt.xticks(range(num_topics_start, num_topics_end + 1, step))
    plt.show()

if __name__ == '__main__':
    # 输入参数
    filename = input("请输入分词结果的CSV 文件名（包含路径）：")
    num_topics_start = int(input("请输入起始主题数："))
    num_topics_end = int(input("请输入结束主题数："))
    step = int(input("请输入步长："))
    no_below = int(input("请输入 no_below 参数值（低频词过滤阈值，默认10）：") or 10)
    no_above = float(input("请输入 no_above 参数值（高频词过滤阈值，默认0.5）：") or 0.5)

    main(filename, num_topics_start, num_topics_end, step, no_below, no_above)
