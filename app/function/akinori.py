import base64
from io import BytesIO
from PIL import Image
from PIL.ExifTags import TAGS
import exif
from openai import AzureOpenAI

# Azure OpenAI設定
client = AzureOpenAI(
    api_key="01efc2d639a7464facdc50fc40407d9f",
    api_version="2024-05-01-preview",
    azure_endpoint="https://ssdl-gpt-4o.openai.azure.com/"
)

def get_gps_info(gps_info):
    gps_data = {}
    if gps_info:
        for key in gps_info.keys():
            decode = TAGS.get(key, key)
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


# 画像ファイルのmeta dataを抽出
def get_image_metadata_deco(image):
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
def convert_to_image_data_deco(image, metadata):
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
        'image_path': "",
        'metadata': {
            '緯度': lat,
            '経度': lon,
            '撮影日時': date_time
        }
    }
    print(image_data)
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
def analyze_multiple_images(base64_images):
    image_contents = []
    for base64_image in base64_images:
        image_contents.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image}"
            }
        })

    prompt = f"""
    以下の{len(base64_images)}枚の写真とそれぞれのメタデータを分析し、総合的な幸福度を評価してください。

    各写真について以下の点を分析してください：
    1. 主要な視覚要素（人物、風景、物体など）
    2. 写真から感じ取れる雰囲気や感情
    3. 撮影時期・場所の特徴とその意義
    4. メタデータ（撮影日時、位置情報、場所名、緯度、経度）の考慮

    全体的な分析：
    1. 写真間の関連性や時系列の変化
    2. 共通するテーマや要素
    3. 環境や背景の多様性とその影響

    幸福度の評価（100%スケール）において、以下の要素を考慮してください：
    - 人物の表情や姿勢
    - 環境や背景の快適さ
    - 活動や行動の種類
    - 社会的つながりの存在
    - 季節や天候の影響

    結論：
    1. 総合的な幸福度を100%スケールで評価してください。
    2. 幸福度判断の根拠を3点以上、簡潔に述べてください。
    3. 写真全体から読み取れる生活の質や満足度について、簡潔に考察してください。

    注意事項：
    - 各要素がどのように幸福度に寄与しているか、具体的に説明してください。
    - 時間経過による変化や成長、場所や環境の影響を考慮してください。
    - 分析は簡潔かつ的確に行い、冗長な説明は避けてください。    
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
        max_tokens=500 * len(base64_images)
    )

    print("分析結果:")
    print(response.choices[0].message.content)

if __name__ == "__main__":
    base64_images = [
        """
        ここにbase64
        """,
        """
        ここにbase64
        """
    ]

    analyze_multiple_images(base64_images)