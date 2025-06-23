# **注意**

## 音色克隆

model_type=1/2/3时，在合成时需要替换cluster。

如使用字符版，控制台显示的旧cluster为volcano_mega，需替换为volcano_icl;

如使用并发版，控制台显示的旧cluster为volcano_mega_concurr，需替换为volcano_icl_concurr

在使用大模型语音合成-双向流式API时，

X-Api-Resource-Id：volc.megatts.default（小时版）

volc.megatts.concurr（并发版）

## 克隆音色合成

音色训练成功后，需要通过调用TTS接口来使用音色合成指定文本的音频。

接口与TTS参数有差别，需要将`cluster`换成`volcano_`icl，`voice_type`传`声音id`。

# 音色克隆

## **创建音色**

### 请求方式

**域名：** https://openspeech.bytedance.com

### 训练（upload接口）

**接口路径:** `POST`/api/v1/mega_tts/audio/upload

**接口描述: 提交音频训练音色**

认证方式使用Bearer Token，在请求的header中加上`"Authorization": "Bearer; {token}"`，并在请求的json中填入对应的appid。

### **请求参数Header:**

| **参数名称** | **参数类型** | **必须参数** | **备注** |
| --- | --- | --- | --- |
| Authorization | string | 必填 | Bearer;${Access Token} |
| Resource-Id | string | 必填 | volc.megatts.voiceclone
（声音复刻2.0目前已经支持双向流式） |

### **请求参数Body:**

| **参数名称** | **层级** | **参数类型** | **必须参数** | **备注** |
| --- | --- | --- | --- | --- |
| appid | 1 | string | 必填 |  |
| speaker_id | 1 | string | 必填 | 唯一音色代号 |
| audios | 1 | list | 必填 | 音频格式支持：wav、mp3、ogg、m4a、aac、pcm，其中pcm仅支持24k 单通道目前限制单文件上传最大10MB，每次最多上传1个音频文件 |
| audio_bytes | 2 | string | 必填 | 二进制音频字节，需对二进制音频进行base64编码 |
| audio_format | 2 | string |  | 音频格式，pcm、m4a必传，其余可选 |
| text | 2 | string |  | 可以让用户按照该文本念诵，服务会对比音频与该文本的差异。若差异过大会返回1109 WERError |
| source | 1 | int | 必填 | 固定值：2 |
| language | 1 | int |  | model_type为0或者1时候，支持以下语种
cn = 0 中文（默认）
en = 1 英文
ja = 2 日语
es = 3 西班牙语
id = 4 印尼语
pt = 5 葡萄牙语
model_type为2或者3时候，仅支持以下语种
cn = 0 中文（默认）
en = 1 英文 |
| model_type | 1 | int |  | 默认为0
1为2.0效果（ICL），0为1.0效果
2为DiT标准版效果（音色、不还原用户的风格）
3为DiT还原版效果（音色、还原用户口音、语速等风格） |

### **json示例**

```json
{
        "speaker_id": "S_*******",（需从控制台获取，参考文档：声音复刻下单及使用指南）
        "appid": "your appid",
        "audios": [{
                "audio_bytes": "base64编码后的音频",
                "audio_format": "wav"
        }],
        "source": 2,
        "language": 0,
        "model_type": 1
}

```

### **返回数据**

### **Body:**

| **参数名称** | **层级** | **参数类型** | **必须参数** | **备注** |
| --- | --- | --- | --- | --- |
| BaseResp | 1 | object | 必填 |  |
| StatusCode | 2 | int | 必填 | 成功:0 |
| StatusMessage | 2 | string |  | 错误信息 |
| speaker_id | 1 | string | 必填 | 唯一音色代号 |

### **json示例**

```json
{
    "BaseResp":{
        "StatusCode":0,
        "StatusMessage":""
    },
    "speaker_id":"S_*******"
}
JSON

```

### 返回码：

| **Success** | **0** | **成功** |
| --- | --- | --- |
| BadRequestError | 1001 | 请求参数有误 |
| AudioUploadError | 1101 | 音频上传失败 |
| ASRError | 1102 | ASR（语音识别成文字）转写失败 |
| SIDError | 1103 | SID声纹检测失败 |
| SIDFailError | 1104 | 声纹检测未通过，声纹跟名人相似度过高 |
| GetAudioDataError | 1105 | 获取音频数据失败 |
| SpeakerIDDuplicationError | 1106 | SpeakerID重复 |
| SpeakerIDNotFoundError | 1107 | SpeakerID未找到 |
| AudioConvertError | 1108 | 音频转码失败 |
| WERError | 1109 | wer检测错误，上传音频与请求携带文本对比字错率过高 |
| AEDError | 1111 | aed检测错误，通常由于音频不包含说话声 |
| SNRError | 1112 | SNR检测错误，通常由于信噪比过高 |
| DenoiseError | 1113 | 降噪处理失败 |
| AudioQualityError | 1114 | 音频质量低，降噪失败 |
| ASRNoSpeakerError | 1122 | 未检测到人声 |
| 已达上传次数限制 | 1123 | 上传接口已经达到次数限制，目前同一个音色支持10次上传 |

## 状态查询（status接口）

**接口路径:** `POST`/api/v1/mega_tts/status

**接口描述: 查询音色训练状态**

### **请求参数Header:**

| **参数名称** | **参数类型** | **必须参数** | **备注** |
| --- | --- | --- | --- |
| Authorization | string | 必填 | Bearer;${Access Token} |
| Resource-Id | string | 必填 | 填入volc.megatts.voiceclone |

### **请求参数Body:**

| **参数名称** | **层级** | **类型** | **必填** | **备注** |
| --- | --- | --- | --- | --- |
| appid | 1 | string | 必填 |  |
| speaker_id | 1 | string | 必填 | 唯一音色代号 |

### **json示例**

```
{
    "appid": "your appid",
    "speaker_id": "S_*******"（需从控制台获取，参考文档：声音复刻下单及使用指南）
}
JSON

```

### **返回数据**

**Body:**

| **参数名称** | **层级** | **参数类型** | **必须参数** | **备注** |
| --- | --- | --- | --- | --- |
| BaseResp | 1 | object | 必填 |  |
| StatusCode | 2 | int | 必填 | 成功:0 |
| StatusMessage | 2 | string |  | 错误信息 |
| speaker_id | 1 | string | 必填 | 唯一音色代号 |
| status | 1 | enum { NotFound = 0 Training = 1 Success = 2 Failed = 3 Active = 4 } | 必填 | 训练状态，状态为2或4时都可以调用tts |
| create_time | 1 | int | 必填 | 创建时间 |
| version | 1 | string | 选填 | 训练版本 |
| demo_audio | 1 | string | 选填 | Success状态时返回，一小时有效，若需要，请下载后使用 |

### **json示例**

```
{
    "BaseResp":{
        "StatusCode":0,
        "StatusMessage":""
    },
    "creaet_time":1701055304000,
    "version": "V1",
    "demo_audio": "http://**********.wav"
    "speaker_id":"S_*******",
    "status":2
}
JSON
```

## python 示例代码

```python
import base64
import os
import requests

host = "https://openspeech.bytedance.com"

def train(appid, token, audio_path, spk_id):
    url = host + "/api/v1/mega_tts/audio/upload"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer;" + token,
        "Resource-Id": "volc.megatts.voiceclone",
    }
    encoded_data, audio_format = encode_audio_file(audio_path)
    audios = [{"audio_bytes": encoded_data, "audio_format": audio_format}]
    data = {"appid": appid, "speaker_id": spk_id, "audios": audios, "source": 2,"language": 0, "model_type": 1}
    response = requests.post(url, json=data, headers=headers)
    print("status code = ", response.status_code)
    if response.status_code != 200:
        raise Exception("train请求错误:" + response.text)
    print("headers = ", response.headers)
    print(response.json())

def get_status(appid, token, spk_id):
    url = host + "/api/v1/mega_tts/status"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer;" + token,
        "Resource-Id": "volc.megatts.voiceclone",
    }
    body = {"appid": appid, "speaker_id": spk_id}
    response = requests.post(url, headers=headers, json=body)
    print(response.json())

def encode_audio_file(file_path):
    with open(file_path, 'rb') as audio_file:
        audio_data = audio_file.read()
        encoded_data = str(base64.b64encode(audio_data), "utf-8")
        audio_format = os.path.splitext(file_path)[1][1:]  # 获取文件扩展名作为音频格式
        return encoded_data, audio_format

if __name__ == "__main__":
    appid = "填入appid"
    token = "填入access token"
    spk_id = "填入声音ID"
    train(appid=appid, token=token, audio_path="填入音频路径", spk_id=spk_id)
    get_status(appid=appid, token=token, spk_id=spk_id)
    
```

# **TTS 语音合成接口（WS/HTTP）**

音色训练成功后，需要通过调用TTS接口来使用音色合成指定文本的音频。

## **Websocket**

使用账号申请部分申请到的appid&access_token进行调用

文本一次性送入，后端边合成边返回音频数据

### **1. 接口说明**

接口地址为 wss://openspeech.bytedance.com/api/v1/tts/ws_binary

### **2. 身份认证**

认证方式使用Bearer Token，在请求的header中加上`"Authorization": "Bearer; {token}"`，并在请求的json中填入对应的appid。

Bearer和token使用分号 ; 分隔，替换时请勿保留{}

### **3. 请求方式**

**报文格式(Message format)，**报文格式中各字节的定义：

第0字节：

- 高4位(7-4位): 协议版本
- 低4位(3-0位): 报头大小

第1字节：

- 高4位(7-4位): 消息类型
- 低4位(3-0位): 消息类型特定标志

第2字节：

- 高4位(7-4位): 消息序列化方法
- 低4位(3-0位): 消息压缩方法

第3字节：保留字段

第4字节及以后：可选的报头扩展

第5字节及以后：根据消息类型不同的负载数据

第6字节及以后：更多数据

### **字段描述**

| **字段 Field (大小, 单位bit)** | **描述 Description** | **值 Values** |
| --- | --- | --- |
| 协议版本(Protocol version) (4) | 可能会在将来使用不同的协议版本，所以这个字段是为了让客户端和服务器在版本上保持一致。 | `0b0001` - 版本 1 (目前只有版本1) |
| 报头大小(Header size) (4) | header实际大小是 `header size value x 4` bytes.
这里有个特殊值 `0b1111` 表示header大小大于或等于60(15 x 4 bytes)，也就是会存在header extension字段。 | `0b0001` - 报头大小 = 4 (1 x 4)
`0b0010` - 报头大小 = 8 (2 x 4)
`0b1010` - 报头大小 = 40 (10 x 4)
`0b1110` - 报头大小 = 56 (14 x 4)
`0b1111` - 报头大小为60或更大; 实际大小在header extension中定义 |
| 消息类型(Message type) (4) | 定义消息类型。 | `0b0001` - full client request.
`~~0b1001~~` ~~- full server response(弃用).~~
`0b1011` - Audio-only server response (ACK).
`0b1111` - Error message from server (例如错误的消息类型，不支持的序列化方法等等) |
| Message type specific flags (4) | flags含义取决于消息类型。
具体内容请看消息类型小节. |  |
| 序列化方法(Message serialization method) (4) | 定义序列化payload的方法。
注意：它只对某些特定的消息类型有意义 (例如Audio-only server response `0b1011` 就不需要序列化). | `0b0000` - 无序列化 (raw bytes)
`0b0001` - JSON
`0b1111` - 自定义类型, 在header extension中定义 |
| 压缩方法(Message Compression) (4) | 定义payload的压缩方法。
Payload size字段不压缩(如果有的话，取决于消息类型)，而且Payload size指的是payload压缩后的大小。
Header不压缩。 | `0b0000` - 无压缩
`0b0001` - gzip
`0b1111` - 自定义压缩方法, 在header extension中定义 |
| 保留字段(Reserved) (8) | 保留字段，同时作为边界 (使整个报头大小为4个字节). | `0x00` - 目前只有0 |

### **消息类型详细说明**

目前所有TTS websocket请求都使用full client request格式，无论"query"还是"submit"。

### **Full client request**

- Header size为`b0001`(即4B，没有header extension)。
- Message type为`b0001`.
- Message type specific flags固定为`b0000`.
- Message serialization method为`b0001`JSON。字段参考上方表格。
- 如果使用gzip压缩payload，则payload size为压缩后的大小。

### **Audio-only server response**

- Header size应该为`b0001`.
- Message type为`b1011`.
- Message type specific flags可能的值有：
    - `b0000` - 没有sequence number.
    - `b0001` - sequence number > 0.
    - `b0010`or`b0011` - sequence number < 0，表示来自服务器的最后一条消息，此时客户端应合并所有音频片段(如果有多条)。
- Message serialization method为`b0000`(raw bytes).

### python 示例代码

```python
#coding=utf-8

'''
requires Python 3.6 or later

pip install asyncio
pip install websockets

'''

import asyncio
import websockets
import uuid
import json
import gzip
import copy

MESSAGE_TYPES = {11: "audio-only server response", 12: "frontend server response", 15: "error message from server"}
MESSAGE_TYPE_SPECIFIC_FLAGS = {0: "no sequence number", 1: "sequence number > 0",
                               2: "last message from server (seq < 0)", 3: "sequence number < 0"}
MESSAGE_SERIALIZATION_METHODS = {0: "no serialization", 1: "JSON", 15: "custom type"}
MESSAGE_COMPRESSIONS = {0: "no compression", 1: "gzip", 15: "custom compression method"}

appid = "xxx"
token = "xxx"
cluster = "xxx"
voice_type = "xxx"
host = "openspeech.bytedance.com"
api_url = f"wss://{host}/api/v1/tts/ws_binary"

# version: b0001 (4 bits)
# header size: b0001 (4 bits)
# message type: b0001 (Full client request) (4bits)
# message type specific flags: b0000 (none) (4bits)
# message serialization method: b0001 (JSON) (4 bits)
# message compression: b0001 (gzip) (4bits)
# reserved data: 0x00 (1 byte)
default_header = bytearray(b'\x11\x10\x11\x00')

request_json = {
    "app": {
        "appid": appid,
        "token": "access_token",
        "cluster": cluster
    },
    "user": {
        "uid": "388808087185088"
    },
    "audio": {
        "voice_type": "xxx",
        "encoding": "mp3",
        "speed_ratio": 1.0,
        "volume_ratio": 1.0,
        "pitch_ratio": 1.0,
    },
    "request": {
        "reqid": "xxx",
        "text": "字节跳动语音合成。",
        "text_type": "plain",
        "operation": "xxx"
    }
}

async def test_submit():
    submit_request_json = copy.deepcopy(request_json)
    submit_request_json["audio"]["voice_type"] = voice_type
    submit_request_json["request"]["reqid"] = str(uuid.uuid4())
    submit_request_json["request"]["operation"] = "submit"
    payload_bytes = str.encode(json.dumps(submit_request_json))
    payload_bytes = gzip.compress(payload_bytes)  # if no compression, comment this line
    full_client_request = bytearray(default_header)
    full_client_request.extend((len(payload_bytes)).to_bytes(4, 'big'))  # payload size(4 bytes)
    full_client_request.extend(payload_bytes)  # payload
    print("\n------------------------ test 'submit' -------------------------")
    print("request json: ", submit_request_json)
    print("\nrequest bytes: ", full_client_request)
    file_to_save = open("test_submit.mp3", "wb")
    header = {"Authorization": f"Bearer; {token}"}
    async with websockets.connect(api_url, extra_headers=header, ping_interval=None) as ws:
        await ws.send(full_client_request)
        while True:
            res = await ws.recv()
            done = parse_response(res, file_to_save)
            if done:
                file_to_save.close()
                break
        print("\nclosing the connection...")

async def test_query():
    query_request_json = copy.deepcopy(request_json)
    query_request_json["audio"]["voice_type"] = voice_type
    query_request_json["request"]["reqid"] = str(uuid.uuid4())
    query_request_json["request"]["operation"] = "query"
    payload_bytes = str.encode(json.dumps(query_request_json))
    payload_bytes = gzip.compress(payload_bytes)  # if no compression, comment this line
    full_client_request = bytearray(default_header)
    full_client_request.extend((len(payload_bytes)).to_bytes(4, 'big'))  # payload size(4 bytes)
    full_client_request.extend(payload_bytes)  # payload
    print("\n------------------------ test 'query' -------------------------")
    print("request json: ", query_request_json)
    print("\nrequest bytes: ", full_client_request)
    file_to_save = open("test_query.mp3", "wb")
    header = {"Authorization": f"Bearer; {token}"}
    async with websockets.connect(api_url, extra_headers=header, ping_interval=None) as ws:
        await ws.send(full_client_request)
        res = await ws.recv()
        parse_response(res, file_to_save)
        file_to_save.close()
        print("\nclosing the connection...")

def parse_response(res, file):
    print("--------------------------- response ---------------------------")
    # print(f"response raw bytes: {res}")
    protocol_version = res[0] >> 4
    header_size = res[0] & 0x0f
    message_type = res[1] >> 4
    message_type_specific_flags = res[1] & 0x0f
    serialization_method = res[2] >> 4
    message_compression = res[2] & 0x0f
    reserved = res[3]
    header_extensions = res[4:header_size*4]
    payload = res[header_size*4:]
    print(f"            Protocol version: {protocol_version:#x} - version {protocol_version}")
    print(f"                 Header size: {header_size:#x} - {header_size * 4} bytes ")
    print(f"                Message type: {message_type:#x} - {MESSAGE_TYPES[message_type]}")
    print(f" Message type specific flags: {message_type_specific_flags:#x} - {MESSAGE_TYPE_SPECIFIC_FLAGS[message_type_specific_flags]}")
    print(f"Message serialization method: {serialization_method:#x} - {MESSAGE_SERIALIZATION_METHODS[serialization_method]}")
    print(f"         Message compression: {message_compression:#x} - {MESSAGE_COMPRESSIONS[message_compression]}")
    print(f"                    Reserved: {reserved:#04x}")
    if header_size != 1:
        print(f"           Header extensions: {header_extensions}")
    if message_type == 0xb:  # audio-only server response
        if message_type_specific_flags == 0:  # no sequence number as ACK
            print("                Payload size: 0")
            return False
        else:
            sequence_number = int.from_bytes(payload[:4], "big", signed=True)
            payload_size = int.from_bytes(payload[4:8], "big", signed=False)
            payload = payload[8:]
            print(f"             Sequence number: {sequence_number}")
            print(f"                Payload size: {payload_size} bytes")
        file.write(payload)
        if sequence_number < 0:
            return True
        else:
            return False
    elif message_type == 0xf:
        code = int.from_bytes(payload[:4], "big", signed=False)
        msg_size = int.from_bytes(payload[4:8], "big", signed=False)
        error_msg = payload[8:]
        if message_compression == 1:
            error_msg = gzip.decompress(error_msg)
        error_msg = str(error_msg, "utf-8")
        print(f"          Error message code: {code}")
        print(f"          Error message size: {msg_size} bytes")
        print(f"               Error message: {error_msg}")
        return True
    elif message_type == 0xc:
        msg_size = int.from_bytes(payload[:4], "big", signed=False)
        payload = payload[4:]
        if message_compression == 1:
            payload = gzip.decompress(payload)
        print(f"            Frontend message: {payload}")
    else:
        print("undefined message type!")
        return True

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_submit())
    loop.run_until_complete(test_query())

```

## **HTTP**

使用账号申请部分申请到的appid&access_token进行调用

文本全部合成完毕之后，一次性返回全部的音频数据

### **1. 接口说明**

> 接口地址为 https://openspeech.bytedance.com/api/v1/tts
> 

### **2. 身份认证**

认证方式采用 Bearer Token.

1)需要在请求的 Header 中填入"Authorization":"Bearer;${token}"

Bearer和token使用分号 ; 分隔，替换时请勿保留${}

### **3. 注意事项**

- 使用 HTTP Post 方式进行请求，返回的结果为 JSON 格式，需要进行解析
- 因 json 格式无法直接携带二进制音频，音频经base64编码。使用base64解码后，即为二进制音频
- 每次合成时 reqid 这个参数需要重新设置，且要保证唯一性（建议使用 UUID/GUID 等生成）
- websocket demo中单条链接仅支持单次合成，若需要合成多次，需自行实现。每次创建websocket连接后，按顺序串行发送每一包。一次合成结束后，可以发送新的合成请求。

### **参数说明**

| **字段** | **含义** | **层级** | **格式** | **必需** | **备注** |
| --- | --- | --- | --- | --- | --- |
| **app** | 应用相关配置 | 1 | dict | ✓ |  |
| **appid** | 应用标识 | 2 | string | ✓ | 需要申请 |
| **token** | 应用令牌 | 2 | string | ✓ | 可传任意非空字符串 |
| **cluster** | 业务集群 | 2 | string | ✓ | volcano_icl或volcano_icl_concurr |
| **user** | 用户相关配置 | 1 | dict | ✓ |  |
| **uid** | 用户标识 | 2 | string | ✓ | 可传任意非空字符串，传入值可以通过服务端日志追溯 |
| **audio** | 音频相关配置 | 1 | dict | ✓ | 语音合成参考音色列表；声音复刻语音合成请通过下单获取 |
| **voice_type** | 音色类型 | 2 | string | ✓ | 填入S_开头的声音id（SpeakerId） |
| **encoding** | 音频编码格式 | 2 | string |  | wav / pcm / ogg_opus / mp3，默认为 pcm
注意：wav 不支持流式 |
| **rate** | 音频采样率 | 2 | int |  | 默认为 24000，可选8000，16000 |
| **speed_ratio** | 语速 | 2 | float |  | [0.2,3]，默认为1，通常保留一位小数即可 |
| **explicit_language** | 明确语种 | 2 | string |  | 仅读指定语种的文本
• 不给定参数，正常中英混
• crosslingual 启用多语种前端（包含zh/en/ja/es-ms/id/pt-br）
• zh 中文为主，支持中英混
• en 仅英文
• ja 仅日文
• es-mx 仅墨西
• id 仅印尼
• pt-br 仅巴葡
当音色使用过model_type=2或3，即采用dit效果时，必须指定语种，目前支持：
zh 中文为主，支持中英混
en 仅英文 |
| **context_language** | 参考语种 | 2 | string |  | 给模型提供参考的语种
• 不给定 西欧语种采用英语
• id 西欧语种采用印尼
• es 西欧语种采用墨西
• pt 西欧语种采用巴葡 |
| **request** | 请求相关配置 | 1 | dict | ✓ |  |
| **text_type** | 文本类型 | 2 | string |  | plain / ssml, 默认为plain。ssml参考[SSML标记语言--语音技术-火山引擎 (volcengine.com)](https://www.volcengine.com/docs/6561/1330194)
（DiT音色暂不支持ssml） |
| **with_timestamp** | 时间戳相关 | 2 | int
string |  | 传入1时表示启用，可返回原文本的时间戳，而非TN后文本，即保留原文中的阿拉伯数字或者特殊符号等。注意：原文本中的多个标点连用或者空格依然会被处理，但不影响时间戳连贯性 |
| **reqid** | 请求标识 | 2 | string | ✓ | 需要保证每次调用传入值唯一，建议使用 UUID |
| **text** | 文本 | 2 | string | ✓ | 合成语音的文本，长度限制 1024 字节（UTF-8编码） |
| **text_type** | 文本类型 | 2 | string |  | 默认plain纯文本，ssml可以支持ssml |
| **operation** | 操作 | 2 | string | ✓ | query（非流式，http只能query） / submit（流式） |
| **split_sentence** | 复刻1.0语速相关 | 2 | int
string |  | 传入1时表示启用，用以解决1.0的声音复刻合成时语速过快的情况 |
| **extra_param** | 额外参数 | 2 | jsonstring |  |  |
| **cache_config** | 缓存相关参数 | 3 | dict |  | 开启缓存，开启后合成相同文本时，服务会直接读取缓存返回上一次合成该文本的音频，可明显加快相同文本的合成速率，缓存数据保留时间1小时。
（通过缓存返回的数据不会附带时间戳）
Python示例："extra_param": json.dumps({"cache_config": {"text_type": 1,"use_cache": True}}) |
| **text_type** | 缓存相关参数 | 4 | int |  | 和use_cache参数一起使用，需要开启缓存时传1 |
| **use_cache** | 缓存相关参数 | 4 | bool |  | 和text_type参数一起使用，需要开启缓存时传true |

备注：

1. 支持ssml能力，参考[SSML标记语言--语音技术-火山引擎 (volcengine.com)](https://www.volcengine.com/docs/6561/1330194)
2. 暂时不支持音高、音量调节
3. 支持中英混，支持语种自动识别

请求示例

```
{
    "app": {
        "appid": "appid123",
        "token": "access_token",
        "cluster": "volcano_icl"
    },
    "user": {
        "uid": "uid123"
    },
    "audio": {
        "voice_type": "S_xxxx",（需从控制台获取，参考文档：声音复刻下单及使用指南）
        "encoding": "mp3",
        "speed_ratio": 1
    },
    "request": {
        "reqid": "uuid",
        "text": "字节跳动语音合成",
        "operation": "query"
    }
}
JSON

```

### **返回参数**

| **字段** | **含义** | **层级** | **格式** | **备注** |
| --- | --- | --- | --- | --- |
| reqid | 请求 ID | 1 | string | 请求 ID,与传入的参数中 reqid 一致 |
| code | 请求状态码 | 1 | int | 错误码，参考下方说明 |
| message | 请求状态信息 | 1 | string | 错误信息 |
| sequence | 音频段序号 | 1 | int | 负数表示合成完毕 |
| data | 合成音频 | 1 | string | 返回的音频数据，base64 编码 |
| addition | 额外信息 | 1 | string | 额外信息父节点 |
| duration | 音频时长 | 2 | string | 返回音频的长度，单位ms |
- 在 websocket/http 握手成功后，会返回这些 Response header

| **Key** | **说明** | **Value 示例** |
| --- | --- | --- |
| X-Tt-Logid | 服务端返回的 logid，建议用户获取和打印方便定位问题，使用默认格式即可，不要自定义格式 | 202407261553070FACFE6D19421815D605 |

响应示例

```
{
    "reqid": "reqid",
    "code": 3000,
    "operation": "query",
    "message": "Success",
    "sequence": -1,
    "data": "base64 encoded binary data",
    "addition": {
        "duration": "1960"
    }
}
JSON

```

### **返回码说明**

| **错误码** | **错误描述** | **举例** | **建议行为** |
| --- | --- | --- | --- |
| 3000 | 请求正确 | 正常合成 | 正常处理 |
| 3001 | 无效的请求 | 一些参数的值非法，比如operation配置错误 | 检查参数 |
| 3003 | 并发超限 | 超过在线设置的并发阈值 | 重试；使用sdk的情况下切换离线 |
| 3005 | 后端服务忙 | 后端服务器负载高 | 重试；使用sdk的情况下切换离线 |
| 3006 | 服务中断 | 请求已完成/失败之后，相同reqid再次请求 | 检查参数 |
| 3010 | 文本长度超限 | 单次请求超过设置的文本长度阈值 | 检查参数 |
| 3011 | 无效文本 | 参数有误或者文本为空、文本与语种不匹配、文本只含标点 | 检查参数 |
| 3030 | 处理超时 | 单次请求超过服务最长时间限制 | 重试或检查文本 |
| 3031 | 处理错误 | 后端出现异常 | 重试；使用sdk的情况下切换离线 |
| 3032 | 等待获取音频超时 | 后端网络异常 | 重试；使用sdk的情况下切换离线 |
| 3040 | 后端链路连接错误 | 后端网络异常 | 重试 |
| 3050 | 音色不存在 | 检查使用的voice_type代号 | 检查参数 |

### **常见错误返回说明**

1. 错误返回：
    
    "message": "quota exceeded for types: xxxxxxxxx_lifetime"
    
    **错误原因：试用版用量用完了，需要开通正式版才能继续使用**
    
2. 错误返回：

"message": "quota exceeded for types: concurrency"

**错误原因：并发超过了限定值，需要减少并发调用情况或者增购并发**

1. 错误返回：
    
    "message": "Fail to feed text, reason Init Engine Instance failed"
    
    **错误原因：voice_type / cluster 传递错误**
    
2. 错误返回：

"message": "illegal input text!"

**错误原因：传入的text无效，没有可合成的有效文本。比如全部是标点符号或者emoji表情，或者使用中文音色时，传递日语，以此类推。多语种音色，也需要使用language指定对应的语种**

1. 错误返回：

"message": "authenticate request: load grant: requested grant not found"

**错误原因：鉴权失败，需要检查appid&token的值是否设置正确，同时，鉴权的正确格式为**

**headers["Authorization"] = "Bearer;${token}"**

### python 示例代码

```python
#coding=utf-8

'''
requires Python 3.6 or later
pip install requests
'''
import base64
import json
import uuid
import requests

# 填写平台申请的appid, access_token以及cluster
appid = "xxxx"
access_token= "xxxx"
cluster = "xxxx"

voice_type = "xxxx"
host = "openspeech.bytedance.com"
api_url = f"https://{host}/api/v1/tts"

header = {"Authorization": f"Bearer;{access_token}"}

request_json = {
    "app": {
        "appid": appid,
        "token": "access_token",
        "cluster": cluster
    },
    "user": {
        "uid": "388808087185088"
    },
    "audio": {
        "voice_type": voice_type,
        "encoding": "mp3",
        "speed_ratio": 1.0,
        "volume_ratio": 1.0,
        "pitch_ratio": 1.0,
    },
    "request": {
        "reqid": str(uuid.uuid4()),
        "text": "字节跳动语音合成",
        "text_type": "plain",
        "operation": "query",
        "with_frontend": 1,
        "frontend_type": "unitTson"

    }
}

if __name__ == '__main__':
    try:
        resp = requests.post(api_url, json.dumps(request_json), headers=header)
        print(f"resp body: \n{resp.json()}")
        if "data" in resp.json():
            data = resp.json()["data"]
            file_to_save = open("test_submit.mp3", "wb")
            file_to_save.write(base64.b64decode(data))
    except Exception as e:
        e.with_traceback()

```

# **音色管理接口**

## **访问鉴权**

python 参考代码

```python
# coding:utf-8
"""
Copyright (year) Beijing Volcano Engine Technology Ltd.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import datetime
import hashlib
import hmac
import json
from urllib.parse import quote

import requests

# 以下参数视服务不同而不同，一个服务内通常是一致的
Service = "speech_saas_prod"
Version = "2023-11-07"
Region = "cn-north-1"
Host = "open.volcengineapi.com"
ContentType = "application/json; charset=utf-8"

# 请求的凭证，从IAM或者STS服务中获取
AK = ""
SK = ""
# 当使用临时凭证时，需要使用到SessionToken传入Header，并计算进SignedHeader中，请自行在header参数中添加X-Security-Token头
# SessionToken = ""

def norm_query(params):
    query = ""
    for key in sorted(params.keys()):
        if type(params[key]) == list:
            for k in params[key]:
                query = (
                        query + quote(key, safe="-_.~") + "=" + quote(k, safe="-_.~") + "&"
                )
        else:
            query = (query + quote(key, safe="-_.~") + "=" + quote(params[key], safe="-_.~") + "&")
    query = query[:-1]
    return query.replace("+", "%20")

# 第一步：准备辅助函数。
# sha256 非对称加密
def hmac_sha256(key: bytes, content: str):
    return hmac.new(key, content.encode("utf-8"), hashlib.sha256).digest()

# sha256 hash算法
def hash_sha256(content: str):
    return hashlib.sha256(content.encode("utf-8")).hexdigest()

# 第二步：签名请求函数
def request(method, date, query, header, ak, sk, action, body):
    # 第三步：创建身份证明。其中的 Service 和 Region 字段是固定的。ak 和 sk 分别代表
    # AccessKeyID 和 SecretAccessKey。同时需要初始化签名结构体。一些签名计算时需要的属性也在这里处理。
    # 初始化身份证明结构体
    credential = {
        "access_key_id": ak,
        "secret_access_key": sk,
        "service": Service,
        "region": Region,
    }
    # 初始化签名结构体
    request_param = {
        "body": body,
        "host": Host,
        "path": "/",
        "method": method,
        "content_type": ContentType,
        "date": date,
        "query": {"Action": action, "Version": Version, **query},
    }
    if body is None:
        request_param["body"] = ""
    # 第四步：接下来开始计算签名。在计算签名前，先准备好用于接收签算结果的 signResult 变量，并设置一些参数。
    # 初始化签名结果的结构体
    x_date = request_param["date"].strftime("%Y%m%dT%H%M%SZ")
    short_x_date = x_date[:8]
    x_content_sha256 = hash_sha256(request_param["body"])
    sign_result = {
        "Host": request_param["host"],
        "X-Content-Sha256": x_content_sha256,
        "X-Date": x_date,
        "Content-Type": request_param["content_type"],
    }
    # 第五步：计算 Signature 签名。
    signed_headers_str = ";".join(
        ["content-type", "host", "x-content-sha256", "x-date"]
    )
    # signed_headers_str = signed_headers_str + ";x-security-token"
    canonical_request_str = "\n".join(
        [request_param["method"].upper(),
         request_param["path"],
         norm_query(request_param["query"]),
         "\n".join(
             [
                 "content-type:" + request_param["content_type"],
                 "host:" + request_param["host"],
                 "x-content-sha256:" + x_content_sha256,
                 "x-date:" + x_date,
             ]
         ),
         "",
         signed_headers_str,
         x_content_sha256,
         ]
    )

    # 打印正规化的请求用于调试比对
    print(f"##### canonical_request_str: #####\n{canonical_request_str}\n")
    hashed_canonical_request = hash_sha256(canonical_request_str)

    # 打印hash值用于调试比对
    print(f"##### hashed_canonical_request: #####\n{hashed_canonical_request}\n")
    credential_scope = "/".join([short_x_date, credential["region"], credential["service"], "request"])
    string_to_sign = "\n".join(["HMAC-SHA256", x_date, credential_scope, hashed_canonical_request])

    # 打印最终计算的签名字符串用于调试比对
    print(f"##### string_to_sign: #####\n{string_to_sign}\n")
    k_date = hmac_sha256(credential["secret_access_key"].encode("utf-8"), short_x_date)
    k_region = hmac_sha256(k_date, credential["region"])
    k_service = hmac_sha256(k_region, credential["service"])
    k_signing = hmac_sha256(k_service, "request")
    signature = hmac_sha256(k_signing, string_to_sign).hex()

    sign_result["Authorization"] = "HMAC-SHA256 Credential={}, SignedHeaders={}, Signature={}".format(
        credential["access_key_id"] + "/" + credential_scope,
        signed_headers_str,
        signature,
    )
    header = {**header, **sign_result}
    # header = {**header, **{"X-Security-Token": SessionToken}}
    # 第六步：将 Signature 签名写入 HTTP Header 中，并发送 HTTP 请求。
    r = requests.request(method=method,
                         url="https://{}{}".format(request_param["host"], request_param["path"]),
                         headers=header,
                         params=request_param["query"],
                         data=request_param["body"],
                         )
    return r.json()

if __name__ == "__main__":

    now = datetime.datetime.utcnow()

    response_body = request("POST", now, {}, {}, AK, SK, "ListMegaTTSTrainStatus", json.dumps({
        "AppID": "",
        #"SpeakerIDs": ["TODO"], #如果希望获取全量speaker id，可以不传入该参数
    }))
    print(f"response_body: \n{response_body}")

    # response_body = request("POST", now, {}, {}, AK, SK, "ActivateMegaTTSTrainStatus", json.dumps({
    #     "AppID": "",
    #     "SpeakerIDs": [""],
    # }))
    # print(f"response_body: \n{response_body}")

```

### **错误码**

1. 非 **2xx** 开头的HTTP返回状态码被可以认为是**错误**
2. 错误的HTTP返回结构体如下

```
{
    "ResponseMetadata":
    {
        "RequestId": "20220214145719010211209131054BC103",// header中的X-Top-Request-Id参数"Action": "ListMegaTTSTrainStatus",
        "Version": "2023-11-07",
        "Service": "{Service}",// header中的X-Top-Service参数"Region": "{Region}",// header中的X-Top-Region参数"Error":
        {
            "Code": "InternalError.NotCaptured",
            "Message": "xxx"
        }
    }
}
JSON

```

1. **"ResponseMetadata.Error.Code"** 客户端可以依照这个字段判断错误种类，已知种类和含义如下

| **Code** | **Description** |
| --- | --- |
| OperationDenied.InvalidSpeakerID | 账号或AppID无权限操作或无法操作SpeakerID列表中的一个或多个实例 |
| OperationDenied.InvalidParameter | 请求体字段不合法（缺失必填字段、类型错误等） |
| InternalError.NotCaptured | 未知的服务内部错误 |

## **API列表-查询 SpeakerID 状态信息 `ListMegaTTSTrainStatus`**

### **接口说明**

查询已购买的音色状态信息，支持按`SpeakerIDs`和`State`过滤。

如果查询条件为空，返回账号的AppID下所有的列表（音色超过1000，强烈建议使用分页接口`BatchListMegaTTSTrainStatus`）。

### **请求方式**

`POST`

### **请求参数**

| **Parameter** | **Type** | **Must** | **Argument type** | **Description** |
| --- | --- | --- | --- | --- |
| Content-Type | string | Y | header | 固定字符串: application/json; charset=utf-8 |
| Action | string | Y | query | ListMegaTTSTrainStatus |
| Version | string | Y | query | 2023-11-07 |
| AppID | string | Y | body | AppID |
| SpeakerIDs | []string | N | body | SpeakerID的列表，如果忽略SpeakerIDs查询数据，强烈建议使用分页接口：BatchListMegaTTSTrainStatus |
| State | string | N | body | 音色状态，支持取值：Unknown、Training、Success、Active、Expired、Reclaimed
详见附录：State状态枚举值 |
| OrderTimeStart | int64 | N | body | 下单时间检索上边界毫秒级时间戳，受实例交付速度影响，可能比支付完成的时间晚 |
| OrderTimeEnd | int64 | N | body | 下单时间检索下边界毫秒级时间戳，受实例交付速度影响，可能比支付完成的时间晚 |
| ExpireTimeStart | int64 | N | body | 实例到期时间的检索上边界毫秒级时间戳 |
| ExpireTimeEnd | int64 | N | body | 实例到期时间的检索下边界毫秒级时间戳 |

### **返回数据**

```
{
          "ResponseMetadata": {
              "RequestId": "20220214145719010211209131054BC103",// header中的X-Top-Request-Id参数"Action": "",
              "Version": "",
              "Service": "{Service}",// header中的X-Top-Service参数"Region": "{Region}"// header中的X-Top-Region参数},
          "Result":{
                  "Statuses": [
                         {
                              "CreateTime": 1700727790000,// unix epoch格式的创建时间，单位ms"DemoAudio": "https://example.com",// http demo链接"InstanceNO": "Model_storage_meUQ8YtIPm",// 火山引擎实例number"IsActivable":true,// 是否可激活"SpeakerID": "S_VYBmqB0A",// speakerID"State": "Success",// speakerID的状态"Version": "V1",// speakerID已训练过的次数"ExpireTime": 1732895999000,//过期时间"Alias": "",//别名，和控制台同步"AvailableTrainingTimes": 9//剩余训练次数，激活音色为0"OrderTime": 1701771990000,// 下单时间，单位ms},
                        {
                              "SpeakerID": "S_VYBmqB0B",// speakerID"State": "Unknown",// speakerID的状态}
                  ]
          }
      }
JSON

```

## **API列表-分页查询SpeakerID状态 `BatchListMegaTTSTrainStatus`**

### **接口说明**

查询已购买的音色状态；相比`ListMegaTTSTrainStatus` 增加了分页相关参数和返回；支持使用token和声明页数两种分页方式；其中，

- 分页token在最后一页为空
- 分页token采用私有密钥进行加密
- 分页接口为新接口，不影响已有接口行为

### **请求方式**

`POST`

### **请求参数**

| **Parameter** | **Type** | **Must** | **Argument type** | **Description** |
| --- | --- | --- | --- | --- |
| Content-Type |  | Y | header | 固定字符串: application/json; charset=utf-8 |
| Action | string | Y | query | BatchListMegaTTSTrainStatus |
| Version | string | Y | query | 2023-11-07 |
| AppID | string | Y | body | AppID |
| SpeakerIDs | []string | N | body | SpeakerID的列表，传空为返回指定APPID下的全部SpeakerID |
| State | string | N | body | 音色状态，支持取值：Unknown、Training、Success、Active、Expired、Reclaimed
详见附录：State状态枚举值 |
| PageNumber | int | N | body | 页数, 需大于0, 默认为1 |
| PageSize | int | N | body | 每页条数, 必须在范围[1, 100]内, 默认为10 |
| NextToken | string | N | body | 上次请求返回的字符串; 如果不为空的话, 将覆盖PageNumber及PageSize的值 |
| MaxResults | int | N | body | 与NextToken相配合控制返回结果的最大数量; 如果不为空则必须在范围[1, 100]内, 默认为10 |
| OrderTimeStart | int64 | N | body | 下单时间检索上边界毫秒级时间戳，受实例交付速度影响，可能比支付完成的时间晚 |
| OrderTimeEnd | int64 | N | body | 下单时间检索下边界毫秒级时间戳，受实例交付速度影响，可能比支付完成的时间晚 |
| ExpireTimeStart | int64 | N | body | 实例到期时间的检索上边界毫秒级时间戳 |
| ExpireTimeEnd | int64 | N | body | 实例到期时间的检索下边界毫秒级时间戳 |

### **返回数据**

```
{
    "ResponseMetadata":
    {
        "RequestId": "20220214145719010211209131054BC103",// header中的X-Top-Request-Id参数"Action": "BatchListMegaTTSTrainStatus",
        "Version": "2023-11-07",
        "Service": "{Service}",// header中的X-Top-Service参数"Region": "{Region}"// header中的X-Top-Region参数},"Result":
        {
            "AppID": "xxx",
            "TotalCount": 2,// speakerIDs总数量"NextToken": "",// NextToken字符串，可发送请求后面的结果; 如果没有更多结果将为空"PageNumber": 1,// 使用分页参数时的当前页数"PageSize": 2,// 使用分页参数时当前页包含的条数"Statuses":
            [
                {
                    "CreateTime": 1700727790000,// unix epoch格式的创建时间，单位ms"DemoAudio": "https://example.com",// http demo链接"InstanceNO": "Model_storage_meUQ8YtIPm",// 火山引擎实例Number"IsActivable":true,// 是否可激活"SpeakerID": "S_VYBmqB0A",// speakerID"State": "Success",// speakerID的状态"Version": "V1"// speakerID已训练过的次数"ExpireTime": 1964793599000,// 到期时间"OrderTime": 1701771990000,// 下单时间"Alias": "",// 别名，和控制台同步"AvailableTrainingTimes": 10// 剩余训练次数},
                {
                    "SpeakerID": "S_VYBmqB0B",// speakerID"State": "Unknown",// speakerID的状态"Version": "V1"// speakerID已训练过的次数}
            ]
        }
}
JSON

```

## **API列表-音色下单`OrderAccessResourcePacks`**

### **接口说明**

一步下单音色并支付订单，前置条件：

- **AppID已经开通声音复刻**
- **账户里面有足够的余额（或代金券），可以自动支付该订单**
- **频率限制：2分钟内最多下单2000个音色**

### **请求方式**

`POST`

### **请求参数**

| **Parameter** | **Type** | **Must** | **Argument type** | **Description** |
| --- | --- | --- | --- | --- |
| Content-Type |  | Y | header | 固定字符串: application/json; charset=utf-8 |
| Action | string | Y | query | OrderAccessResourcePacks |
| Version | string | Y | query | 2023-11-07 |
| AppID | string | Y | body | AppID |
| ResourceID | string | Y | body | 平台的服务类型资源标识，必填且唯一：volc.megatts.voiceclone |
| Code | string | Y | body | 平台的计费项标识，必填且唯一：
Model_storage |
| Times | int | Y | body | 下单单个音色的时长，单位为月 |
| Quantity | int | Y | body | 下单音色的个数，如100，即为购买100个音色 |
| AutoUseCoupon | bool | N | body | 是否自动使用代金券 |
| CouponID | string | N | body | 代金券ID，通过[代金券管理](https://www.volcengine.com/docs/6269/67339)获取 |
| ResourceTag | object | N | body | 项目&标签账单配置 |
| ResourceTag.CustomTags | map[string]string | N | body | 标签，通过[标签管理](https://www.volcengine.com/docs/6649/189381)获取 |
| ResourceTag.ProjectName | string | N | body | 项目名称，通过[项目管理](https://www.volcengine.com/docs/6649/94336)获取 |

### **请求示例**

```
{
    "AppID": "100000000",
    "ResourceID": "volc.megatts.voiceclone",
    "Code": "Model_storage",
    "Times": 12,
    "Quantity": 2000
}
JSON

```

### **返回数据**

```
{
    "ResponseMetadata":
    {
        "RequestId": "20220214145719010211209131054BC103",// header中的X-Top-Request-Id参数"Action": "OrderAccessResourcePacks",
        "Version": "2023-11-07",
        "Service": "{Service}",// header中的X-Top-Service参数"Region": "{Region}"// header中的X-Top-Region参数},"Result":
        {
            "OrderIDs":
            [
                "Order20010000000000000001"// 购买成功返回的订单号ID]
        }
}
JSON

```

## **API列表-音色续费`RenewAccessResourcePacks`**

### **接口说明**

一步续费音色并支付订单，前置条件：

- **账户里面有足够的余额（或代金券），可以自动支付该订单**
- **频率限制：2分钟内最多续费2000个音色**

### **请求方式**

`POST`

### **请求参数**

| **Parameter** | **Type** | **Must** | **Argument type** | **Description** |
| --- | --- | --- | --- | --- |
| Content-Type |  | Y | header | 固定字符串: application/json; charset=utf-8 |
| Action | string | Y | query | `RenewAccessResourcePacks` |
| Version | string | Y | query | 2023-11-07 |
| Times | int | Y | body | 续费音色的时长，单位为月 |
| SpeakerIDs | []string | N | body | 要续费的SpeakerID的列表，可以通过`BatchListMegaTTSTrainStatus`接口过滤获取 |
| AutoUseCoupon | bool | N | body | 是否自动使用代金券 |
| CouponID | string | N | body | 代金券ID，通过[代金券管理](https://www.volcengine.com/docs/6269/67339)获取 |

### **返回数据**

```
{
    "ResponseMetadata":
    {
        "RequestId": "20220214145719010211209131054BC103",// header中的X-Top-Request-Id参数"Action": "OrderAccessResourcePacks",
        "Version": "2023-11-07",
        "Service": "{Service}",// header中的X-Top-Service参数"Region": "{Region}"// header中的X-Top-Region参数},"Result":
        {
            "OrderIDs":
            [
                "Order20010000000000000001"// 购买成功返回的订单号ID]
        }
}
JSON

```

### **附录**

### **State状态枚举值**

| **State** | **Description** |
| --- | --- |
| Unknown | SpeakerID尚未进行训练 |
| Training | 声音复刻训练中（长时间处于复刻中状态请联系火山引擎技术人员） |
| Success | 声音复刻训练成功，可以进行TTS合成 |
| Active | 已激活（无法再次训练） |
| Expired | 火山控制台实例已过期或账号欠费 |
| Reclaimed | 火山控制台实例已回收 |

### **常见错误枚举值**

| **Error** | **Description** |
| --- | --- |
| InvalidParameter | 请求参数错误 |
| Forbidden.InvalidService | 未开通声音复刻 |
| Forbidden.ErrAccountNotPermission | 账号没有权限 |
| Forbidden.LimitedTradingFrequency | 下单限流错误 |
| InvalidParameter.AppID | AppID错误或者无效 |
| NotFound.ResourcePack | 音色（或资源包）不存在 |
| InvalidParameter.InstanceNumber | 无效的音色（或实例） |