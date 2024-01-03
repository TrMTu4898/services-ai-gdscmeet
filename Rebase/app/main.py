import time
from datetime import datetime
import app.VietnameseTextNormalizer
import socketio
from app.services.connect_db.config_firebase import ConfigFirebase
from app.services.keyword_generator.keyword_explorer import GoogleGenerative
from dotenv import load_dotenv
import redis
import aioredis
import os
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import requests

load_dotenv(dotenv_path='../PATH.env')

REDIS_HOST = os.getenv("REDIS_HOST", "127.0.0.1")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6080))
REDIS_DB = int(os.getenv("REDIS_DB", 0))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)
CLIENT_NAME = os.getenv("CLIENT_NAME", "AIGDSCMeetKeywords")

if REDIS_PASSWORD is None:
    raise ValueError("Redis password is not set. Please set REDIS_PASSWORD in your .env file.")

REDIS_CLIENT = redis.StrictRedis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    client_name=CLIENT_NAME,
    password=REDIS_PASSWORD,
    decode_responses=True
)

user_data = {}
config_fb = ConfigFirebase('app/serviceAccountKey.json')
KEYWORDS_EXPLORER = GoogleGenerative(api_key=os.getenv("GEMINI_API_KEY"))

app_sio = FastAPI()
app_sio.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS"),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
app_sio.mount('/app/app/static', StaticFiles(directory='/app/app/static'), name='static')
sio = socketio.AsyncServer(async_mode='asgi',
                           cors_allowed_origins="*",
                           cors_allowed_methods=["*"],
                           cors_allowed_headers=["*"]
                           )
combined_asgi_app = socketio.ASGIApp(sio, app_sio)

@app_sio.get('/')
async def index():
    return FileResponse('index.html')

@sio.event
async def connect(sid, environ, user_info):
    user_data[sid] = user_info
    print(f"Client connected: {sid}")
    await sio.emit('hello', {'message': 'Welcome to the server!'}, to=sid)

@sio.event
async def disconnect(sid):
    user_info = user_data.pop(sid, None)
    if user_info:
        print(f"Client disconnected: {sid}")
        meeting_id = user_info.get('MEETINGID')
        if meeting_id:
            data_from = await get_data_from_redis(meeting_id)
            keywords_utf8 = [keyword.decode('utf-8') for keyword in data_from]
            encoded_keywords = [keyword.encode('utf-8') for keyword in keywords_utf8]
            keywords_data = {
                'meeting_id': meeting_id,
                'keywords': encoded_keywords
            }
            # json_to_docx(keywords_data)
            print(encoded_keywords)

    await sio.emit('disconnect_message', {'message': 'You have been disconnected.'}, to=sid)


@sio.event
async def speech_to_text_result(sid, data):
    if is_host(sid):
        meeting_id = user_data[sid]['MEETINGID']
        input_mes = app.VietnameseTextNormalizer.Normalize(data)
        start_time = time.time()
        kw_result = KEYWORDS_EXPLORER.generative(input_mes=input_mes)
        kw_result = await check_and_remove_duplicates(keywords=kw_result, meetingid=meeting_id)
        end_time = time.time()
        date_format = "%d/%m/%Y %H:%M:%S"
        start_at_formatted = datetime.fromtimestamp(start_time).strftime(date_format)
        end_at_formatted = datetime.fromtimestamp(end_time).strftime(date_format)

        await config_fb.create_document(source=input_mes, keywords=kw_result)
        result = {
            'startAt': start_at_formatted,
            'endAt': end_at_formatted,
            'keywords': kw_result
        }
        await sio.emit('speechToKeywords', data=result, to=sid)
        for participant_sid, participant_info in user_data.items():
            if participant_info['MEETINGID'] == meeting_id and not is_host(sid=participant_sid):
                await sio.emit('speechToKeywords', data=result, to=participant_sid)

def authenticate_user(token):
    # Gọi API để xác nhận token
    pass

# sau khi disconnect room tạo file gửi về BE
def is_host(sid):
    return user_data.get(sid, {}).get('ROLE') == 'HOST'

async def check_and_remove_duplicates(meetingid, keywords):
    key = f"meeting:{meetingid}:keywords"

    async with aioredis.from_url(f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}") as redis_client:
        keywords_utf8 = [keyword.decode('utf-8') if isinstance(keyword, bytes) else keyword for keyword in keywords]
        if await redis_client.exists(key):
            current_keywords = await redis_client.smembers(key)
            current_keywords_utf8 = [keyword.decode('utf-8') if isinstance(keyword, bytes) else keyword for keyword in current_keywords]
            duplicate = set(current_keywords_utf8).intersection(current_keywords)
            unique = list(set(current_keywords_utf8) - duplicate)
            await redis_client.delete(key)
            await redis_client.sadd(key, *unique)
            return [keyword.encode('utf-8') if isinstance(keyword, str) else keyword for keyword in unique]
        else:
            await redis_client.sadd(key, *keywords_utf8)
            return keywords


async def get_data_from_redis(meeting_id):
    key = f"meeting:{meeting_id}:keywords"
    async with aioredis.from_url(f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}") as redis_client:
        if await redis_client.exists(key):
            data_from_redis = await redis_client.smembers(key)
            return data_from_redis
        else:
            return None


# def json_to_docx(json_data):
#     # Create an in-memory buffer
#     import io
#     buffer = io.BytesIO()
#
#     # Create a new Word document
#     doc = Document()
#
#     for key, value in json_data.items():
#         doc.add_heading(key, level=1)
#         if isinstance(value, list):
#             for item in value:
#                 if isinstance(item, dict):
#                     for nested_key, nested_value in item.items():
#                         doc.add_heading(nested_key, level=2)
#                         doc.add_paragraph(str(nested_value))
#                 else:
#                     doc.add_paragraph(str(item))
#         elif isinstance(value, dict):
#             for nested_key, nested_value in value.items():
#                 doc.add_heading(nested_key, level=2)
#                 doc.add_paragraph(str(nested_value))
#         else:
#             doc.add_paragraph(str(value))
#
#     doc.save(buffer)
#
#     buffer.seek(0)
#
#     send_to_api(buffer)
#
#
# def send_to_api(buffer):
#     # Replace 'YOUR_API_ENDPOINT' with the actual API endpoint
#     api_endpoint = os.environ.get('API_SEND_FILE')
#
#     # Create a files dictionary with the buffer content
#     files = {'file': ('document.docx', buffer)}
#
#     response = requests.post(api_endpoint, files=files)
#
#     # Check the API response
#     if response.status_code == 200:
#         print('File successfully sent to the API.')
#     else:
#         print(f'Failed to send file. Status code: {response.status_code}, Response: {response.text}')
#
#     pass

if __name__ == '__main__':
    uvicorn.run(combined_asgi_app, host='127.0.0.1', port=5000)
