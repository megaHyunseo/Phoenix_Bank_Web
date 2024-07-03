import re
import uuid
import json
import time
import requests

api_url = 'https://mndkb1dkel.apigw.ntruss.com/custom/v1/32158/9bcc53067767c1d07734fcdd61a2befea09f58cca1366a7a48cf3db8c8b982db/general'
secret_key = 'QUlNTmRQTXltUW9VYlN0WWNRUWFKZXRYZEJRS0xLWmE='

def extract_text_from_image(image_path):
    files = [('file', open(image_path, 'rb'))]

    request_json = {'images': [{'format': 'jpg', 'name': 'demo'}], 'requestId': str(uuid.uuid4()), 'version': 'V2', 'timestamp': int(round(time.time() * 1000))}

    payload = {'message': json.dumps(request_json).encode('UTF-8')}
    headers = {'X-OCR-SECRET': secret_key}

    response = requests.request("POST", api_url, headers=headers, data=payload, files=files)
    result = response.json()

    if 'images' not in result:
        raise KeyError("'images' not found in the response")

    fields = result['images'][0]['fields']
    fields = sorted(fields, key=lambda x: x['boundingPoly']['vertices'][0]['y'])

    name = ""
    registration_number = ""
    id_type = ""

    # 신분증 종류 결정
    for field in fields:
        text = field['inferText']
        if "주민등록증" in text:
            id_type = "resident"
            break
        elif "자동차운전면허증" in text:
            id_type = "driver"
            break

    # 신분증 종류에 따라 정보 추출
    if id_type == "resident":
        if len(fields) > 1:
            name = fields[1]['inferText']
            name = re.sub(r'\(.*\)', '', name).strip()

        for field in fields:
            text = field['inferText']
            if len(text) == 14 and text[6] == '-':
                registration_number = text
                break

    elif id_type == "driver":
        for field in fields:
            text = field['inferText']
            if re.match(r"^[가-힣]{2,4}$", text):  # 한글 이름 추출
                name = text
            if re.match(r"\d{6}-\d{7}", text):  # 주민등록번호 패턴 추출
                registration_number = text

    if not name or not registration_number:
        raise ValueError('이름 또는 주민등록번호를 추출하지 못했습니다')

    return name, registration_number