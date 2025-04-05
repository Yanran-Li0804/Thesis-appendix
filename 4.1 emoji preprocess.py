# -*- coding: utf-8 -*-
import pandas as pd
import emoji

# 创建自定义的 emoji 到文字的映射字典
emoji_to_text = {
    ":turtle:": "龟",
    ":chicken:": "鸡",
    ":mouse_face:": "鼠"
    # 可以在这里添加更多的 emoji 映射
}

# 读取 CSV 文件
df = pd.read_csv('final分词_0819-1018.csv')


# 定义函数，将文本中的 emoji 描述转为中文字符
def replace_emoji_with_custom_text(text):
    # 确保 text 是字符串类型
    if isinstance(text, str):
        # 使用 emoji.demojize() 获取 emoji 描述
        text_with_descriptions = emoji.demojize(text)

        # 替换所有的 emoji 描述为对应的中文字符
        for emj, ch in emoji_to_text.items():
            text_with_descriptions = text_with_descriptions.replace(emj, ch)

        return text_with_descriptions
    else:
        # 如果不是字符串类型，直接返回原始值或可以替换为默认值
        return text


# 处理 'cleaned_texts' 列
df['cleaned_texts'] = df['cleaned_texts'].apply(replace_emoji_with_custom_text)

# 保存更新后的 DataFrame 到新的 CSV 文件
df.to_csv('updated_file.csv', index=False)
