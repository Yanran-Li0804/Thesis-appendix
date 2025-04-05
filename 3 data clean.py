# -*- coding: utf-8 -*-
import pandas as pd

# 手动输入文件名
input_file = input("请输入要处理的CSV文件名（包括扩展名，如：data.csv）：")
output_file = input("请输入保存过滤后数据的文件名（包括扩展名，如：filtered_data.csv）：")

# 读取 CSV 文件
df = pd.read_csv(input_file)

# 移除 'last_reply_time' 和 'url' 列为空的条目
df = df.dropna(subset=['last_reply_time', 'url'])
# 删除 'last_reply_time' 列中包含 ':' 的条目
df = df[~df['last_reply_time'].str.contains(":", na=False)]
# 将 'last_reply_time' 列转换为 datetime 类型
df['last_reply_time'] = pd.to_datetime(df['last_reply_time'], format='%Y-%m-%d')

# 手动输入时间范围
start_date = pd.to_datetime(input("请输入起始日期（格式：YYYY-MM-DD）："))
end_date = pd.to_datetime(input("请输入结束日期（格式：YYYY-MM-DD）："))

# 过滤数据，保留在时间范围内的条目
filtered_df = df[(df['last_reply_time'] >= start_date) & (df['last_reply_time'] <= end_date)]

# 保存过滤后的数据到新的 CSV 文件
filtered_df.to_csv(output_file, index=False)

print(f"过滤后的数据已保存至 {output_file}")
