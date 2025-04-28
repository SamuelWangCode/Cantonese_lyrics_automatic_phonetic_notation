import argparse
import json
import re
import time
import urllib.parse
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from zhconv import convert

# 缓存文件路径
CACHE_FILE = "pronunciation_cache.json"


def is_chinese(char):
    """判断字符是否为中文字符"""
    return re.match(r'[\u4e00-\u9fff]', char) is not None


def load_cache():
    try:
        if Path(CACHE_FILE).exists():
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"⚠️ 缓存加载失败: {str(e)}")
    return {}


def save_cache(cache):
    try:
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"⚠️ 缓存保存失败: {str(e)}")


pronunciation_cache = load_cache()


def get_cantonese_pronunciation(word):
    """查询单个字的粤语发音（自动转简体）"""
    simplified_char = convert(word, 'zh-hans')
    if simplified_char in pronunciation_cache:
        return pronunciation_cache[simplified_char]

    encoded_word = urllib.parse.quote(simplified_char.encode('utf-8'))
    url = f"https://shyyp.net/search?q={encoded_word}"

    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        pronunciation_tags = soup.find_all('span', class_='PS_jp_dig')
        pron = pronunciation_tags[0].text if pronunciation_tags else '?'
        pronunciation_cache[simplified_char] = pron
        return pron
    except Exception as e:
        print(f"查询 {word} 时出错: {e}")
        return '?'
    finally:
        time.sleep(0.5)


def process_lyrics(lyrics, traditional=False):
    """处理歌词生成注音（跳过非汉语内容）"""
    print("🎵 开始处理歌词注音...")
    output = []
    lines = lyrics.split('\n')

    for index, line in enumerate(lines, 1):
        if not line.strip():
            continue

        # 繁简转换处理
        converted_line = convert(line, 'zh-hant' if traditional else 'zh-hans')
        print(f"\n🔍 正在处理第 {index}/{len(lines)} 行: {converted_line}")

        pinyin = []
        for char in converted_line:
            if char.strip():
                # 跳过非汉语字符（直接保留）
                if not is_chinese(char):
                    pinyin.append(char)
                    print(f"  ⏩ 跳过非汉语字符: 「{char}」")
                    continue

                pron = get_cantonese_pronunciation(char)
                pinyin.append(pron)
                print(f"  ✅ 「{char}」: {pron.ljust(5)}")
            else:
                pinyin.append(' ')
        output.extend([' '.join(pinyin), converted_line, ''])

    print("\n🎉 所有歌词处理完成！")
    return '\n'.join(output)


def main():
    parser = argparse.ArgumentParser(description='粤语歌词注音工具')
    parser.add_argument('-f', '--file', default='lyrics.txt', help='歌词文件路径（默认为lyrics.txt）')
    parser.add_argument('-o', '--output', help='自定义输出文件名')
    parser.add_argument('-t', '--traditional', action='store_true', help='保存繁体字歌词')
    args = parser.parse_args()

    try:
        input_path = Path(args.file)
        print(f"📖 正在读取文件：{input_path}")
        with open(input_path, 'r', encoding='utf-8') as f:
            lyrics = f.read().strip()

        # 自动生成输出文件名
        if args.output:
            output_path = Path(args.output)
        else:
            output_path = input_path.with_name(f"{input_path.stem}_Cantonese{input_path.suffix}")

        print("⏳ 正在生成注音...")
        result = process_lyrics(lyrics, args.traditional)

        # 确保输出目录存在
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(result)

        print(f"\n✅ 成功生成注音文件：{output_path}")
        print(f"📊 统计信息：")
        print(f"   输入行数：{len(lyrics.splitlines())}")
        print(f"   缓存字数：{len(pronunciation_cache)}")
        print(f"   繁简模式：{'繁体' if args.traditional else '简体'}")

    except FileNotFoundError:
        print(f"❌ 错误：文件 {args.file} 不存在")
    except Exception as e:
        print(f"❌ 发生错误：{str(e)}")
    finally:
        save_cache(pronunciation_cache)


if __name__ == "__main__":
    print("🚀 粤语歌词注音工具 v2.0")
    main()
