import os
import base64
import pillow_heif
import io

from PIL.ExifTags import TAGS, GPSTAGS
from openai import AzureOpenAI
from PIL import Image
from geopy.geocoders import Nominatim

# Azure OpenAI設定
client = AzureOpenAI(
    api_key="01efc2d639a7464facdc50fc40407d9f",
    api_version="2024-05-01-preview",
    azure_endpoint="https://ssdl-gpt-4o.openai.azure.com/"
)

# GPS情報の抽出部分
def get_gps_info(gps_info):
    gps_data = {}
    for key in gps_info.keys():
        decode = GPSTAGS.get(key, key)
        gps_data[decode] = gps_info[key]
    return gps_data

# 画像ファイルのmeta dataを抽出
def get_image_metadata(image_path):
    image = Image.open(image_path)
    exif_data = {}
    if hasattr(image, '_getexif'):
        exif = image._getexif()
        if exif:
            for tag_id, value in exif.items():
                tag = TAGS.get(tag_id, tag_id)
                if tag == 'GPSInfo':
                    exif_data[tag] = get_gps_info(value)
                elif tag == 'DateTime':
                    exif_data[tag] = value
    return exif_data

# 画像のパス メタデータの辞書 を引数に持って1つに固める関数
def convert_to_image_data(img_path, metadata):
    # 緯度の変換
    try:
        lat = metadata['GPSInfo']['GPSLatitude']
    except:
        lat = ""

    # 経度の変換
    try:
        lon = metadata['GPSInfo']['GPSLongitude']
    except:
        lon = ""

    # 撮影日時の取得
    try:
        date_time = metadata['DateTime']
    except:
        date_time = ""

    # 変換後のデータ構造
    image_data = {
        'image_path': img_path,
        'metadata': {
            '緯度': lat,
            '経度': lon,
            '撮影日時': date_time
        }
    }
    return image_data

# 緯度経度から住所を特定
def get_location_info(latitude, longitude):
    # 緯度経度を10進数に変換
    lat = float(latitude[0] + latitude[1]/60 + latitude[2]/3600)
    lon = float(longitude[0] + longitude[1]/60 + longitude[2]/3600)

    # Nominatimジオコーダーを初期化
    geolocator = Nominatim(user_agent="my_app")

    # 逆ジオコーディングを実行
    location = geolocator.reverse(f"{lat}, {lon}", language="ja")

    if location:
        address = location.raw['address']
        prefecture = [item.strip() for item in location.raw['display_name'].split(',')][-3]
        
        city = address.get('city', '')
        place = address.get('suburb', '') or address.get('neighbourhood', '')
        name = location.raw["name"]
        return prefecture, city, place, name
    else:
        return "", "", "", ""

# 画像をエンコードする関数
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# 画像分析
def analyze_multiple_images(image_paths):
    image_contents = []
    for image_path in image_paths:
        base64_image = encode_image(image_path)
        metadata = get_image_metadata(image_path)
        image_data = convert_to_image_data(image_path, metadata)

        prefecture, city, place, name = get_location_info(image_data['metadata']['緯度'], image_data['metadata']['経度'])
        
        image_contents.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image}"
            }
        })

        image_contents.append({
            "type": "text",
            "text": f"""
            撮影日時: {image_data['metadata']['撮影日時']}
            位置情報: {prefecture} {city} {place}
            場所名：{name}
            """
        })

    prompt = f"""
    これらの{len(image_paths)}枚の写真とそれぞれのメタデータを分析してください。
    各写真について以下の点を説明し、最後に全体的な幸福度を評価してください：
    1. 各写真に写っている主な要素や場面
    2. それぞれの写真から感じ取れる幸せな出来事や感情
    3. 撮影時期や場所の特徴とそれが幸福感にどう影響しているか

    最後に、これらの写真全体から読み取れる幸福度を10段階で評価し、その理由を説明してください。
    """

    messages = [
        {
            "role": "user",
            "content": [{"type": "text", "text": prompt}] + image_contents
        }
    ]

    response = client.chat.completions.create(
        model="ssdl-gpt-4o",
        messages=messages,
        max_tokens=500 * len(image_paths)
    )

    print("分析結果:")
    print(response.choices[0].message.content)

if __name__ == "__main__":
    image_paths = [
        "/content/drive/MyDrive/ハッカソン/sample_img1.JPG",
        "/content/drive/MyDrive/ハッカソン/sample_img2.jpg"
    ]

    analyze_multiple_images(image_paths)