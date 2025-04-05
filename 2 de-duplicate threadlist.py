# -*- coding: utf-8 -*-
# 含有“旭博美”三个字 的 删掉那一行

import csv

def remove_duplicates(input_filename, output_filename):
    """ Remove duplicate entries from the input CSV file without a header and save to a new file. """
    seen = set()
    cleaned_data = []

    try:
        # 读取CSV文件
        with open(input_filename, mode='r', encoding='utf-8') as infile:
            reader = csv.reader(infile)

            for row in reader:
                if len(row) < 2:
                    print("Warning: Skipping row with missing title or URL.")
                    continue

                title, url = row[0], row[1]
                if url not in seen:
                    seen.add(url)
                    cleaned_data.append(row)

        if not cleaned_data:
            print("No data to write after removing duplicates.")
            return

        # 保存过滤后的数据到新的 CSV 文件
        with open(output_filename, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.writer(outfile)
            writer.writerows(cleaned_data)

        print(f"Cleaned data has been saved to {output_filename}")

    except FileNotFoundError:
        print(f"File {input_filename} not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    # 手动输入文件名
    input_file = input("请输入要处理的CSV文件名（包括扩展名，如：data.csv）：")
    output_file = input("请输入保存去重后数据的文件名（包括扩展名，如：cleaned_data.csv）：")
    remove_duplicates(input_file, output_file)
