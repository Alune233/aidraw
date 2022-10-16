import json
import re
import nonebot
from nonebot.adapters.onebot.v11 import (
    Bot,
    Message,
    MessageEvent,
    MessageSegment,
    unescape,
)
from typing import Type
from nonebot.matcher import Matcher
import httpx
from io import BytesIO
import base64
from PIL import Image
from configs.path_config import TEXT_PATH
import hashlib
from utils.http_utils import AsyncHttpx


async def get_img(
tool: int, style: str, img_url: str, matcher: Type[Matcher], bot: Bot, event: MessageEvent
):
    await matcher.send("真寻开始画画了...")
    # 读取数据
    data_se = {}
    path_set = TEXT_PATH / "aidraw_setting.json"
    with open(path_set)as f:
        data_se = json.load(f)
    
    picture = ''
    
    url_end = "api/predict" if data_se["setting"][0]["url"].endswith("/") else "/api/predict"
    url = data_se["setting"][0]["url"]+url_end
    negative_prompt = data_se["setting"][0]["negative_prompt"]
    step = data_se["setting"][0]["step"]
    denoising = float(data_se["setting"][0]["denoising"])
    size = data_se["setting"][0]["size"]
    method_ls = data_se["setting"][1]["method_ls"]
    resize_ls = data_se["setting"][1]["resize_ls"]
    method = data_se["setting"][0]["method"]
    resize = data_se["setting"][0]["resize"]
    b_count = data_se["setting"][0]["b_count"]
    b_size = data_se["setting"][0]["b_size"]
    
    try:
        async with httpx.AsyncClient(timeout=None) as client:  # 创建一个异步client
            data = ''
            if tool == 31:

                img_upload = await client.get(img_url)
                picture = str(base64.b64encode(BytesIO(img_upload.content).read()))[2:-1]
                image = Image.open(BytesIO(img_upload.content)) 
                image_type = str(image).split(".")[1].replace("ImagePlugin","").lower()

                data = json.dumps({"fn_index":31,"data":[0, style, negative_prompt,"None","None",f"data:image/{image_type};base64,{picture}",None,None,None,"Draw mask",step,method_ls[method],4,"original",False,False,b_count,b_size,7,denoising,-1,-1,0,0,0,False,size['height'],size['width'],resize_ls[resize],False,32,"Inpaint masked","","","None","","",1,50,0,False,4,1,"",128,8,["left","right","up","down"],1,0.05,128,4,"fill",["left","right","up","down"],False,False,None,"","",64,"None","Seed","","Steps","",True,False,None,"",""],"session_hash":"e0xb1bctmt6"})

            elif tool == 12:
        
                data = json.dumps({"fn_index":tool,"data":[f"{style}",negative_prompt,"None","None",step,method_ls[method],False,False,b_count,b_size,7,-1,-1,0,0,0,False,size['height'],size['width'],False,False,0.7,"None",False,False,None,"","Seed","","Steps","",True,False,None,"",""],"session_hash":"i861rv5ueqg"})

            res = (await client.post(url=url,data=data)).json()
            picture_64 = 'base64://'+ res['data'][0][0].split(',')[1]
            process_time = round(res['duration'],3)
            
            # 设备信息 可以自选是否send
            gpu_situation = re.findall("</p><p class='vram'>(.*?), <wbr>(.*?)</p>",res['data'][-1],re.S | re.M)
    
            ai2img = f"[CQ:image,file={picture_64}]\n花费时间:{process_time}s"
            return ai2img

    except Exception as e:
        msg = f"出错了,可能管理员把设备关闭了。。{type(e)}:{e}"
        return msg


def split_msg(event: MessageEvent):
    def _is_at_me_seg(segment: MessageSegment):
        return segment.type == "at" and str(segment.data.get("qq", "")) == str(
        event.self_id
        )
    msg: msg = event.get_message()
    if event.reply:
        args = []
        for img in event.reply.message["image"]:
            img_url=str(img.data.get("url", ""))
        for msg_seg in msg:
            if msg_seg.type == "text":
                raw_text = str(msg_seg)
                raw_text = raw_text.replace("aii2i","").strip()
                texts = raw_text.split(",")
                print(raw_text)
                for text in texts:
                        text = unescape(text).strip()
                        if text:
                            args.append(text)
        style = (",").join(args)
    else:
        #if "image" not in [str(type(msg_seg)) for msg_seg in msg]:
        #   await i2i.finish("没有图也要转图？")
        #_msg: Message = state["REGEX_ARG"]
        if event.to_me:
            raw_msg = Message(event.raw_message)
            i = -1
            last_msg_seg = raw_msg[i]
            if (
                last_msg_seg.type == "text"
                and not last_msg_seg.data["text"].strip()
                and len(raw_msg) >= 2
            ):
                i -= 1
                last_msg_seg = raw_msg[i]
            if _is_at_me_seg(last_msg_seg):
                msg.append(last_msg_seg)
        args = []
        
        for msg_seg in msg:
            if msg_seg.type == "at":
                qq=str(msg_seg.data.get("qq", ""))
                img_url = get_url(qq)

            elif msg_seg.type == "image":
                img_url=str(msg_seg.data.get("url", ""))
            elif msg_seg.type == "text":
                raw_text = str(msg_seg)
                raw_text = raw_text.replace("aii2i","").strip()
                print(raw_text)
                texts = raw_text.split()
                if len(texts)>1:
                    texts = [texts[0]]+(" ").join(texts[1:]).split(',')
                print(texts)
                for text in texts:
                    if is_qq(text):
                        img_url = get_url(str(text))
                    elif text == "自己":
                        qq=str(event.user_id)
                        img_url = get_url(qq)
                    else:
                        text = unescape(text).strip()
                        if text:
                            args.append(text)
        #img_url = get_message_img(event.json())[0]
        style = (',').join(args)
        
    return img_url,style
        
def get_url(user_id: str) -> str:
    url = f"http://q1.qlogo.cn/g?b=qq&nk={user_id}&s=640"
    #data = test_url(url)
    #if hashlib.md5(data).hexdigest() == "acef72340ac0e914090bd35799f5594e":
    #    url = f"http://q1.qlogo.cn/g?b=qq&nk={user_id}&s=100"
    return url


async def test_url(url: str) -> bytes:
    try:
        resp = await AsyncHttpx.get(url, timeout=20)
        resp.raise_for_status()
        return resp.content
    except Exception as e:
        logger.warning(f"Error downloading {url}, retry: {e}")
        await asyncio.sleep(3)
    raise Exception(f"{url} 下载失败！")
    
def is_qq(msg: str):
    return msg.isdigit() and 11 >= len(msg) >= 5


async def show_info(
what: str, matcher: Type[Matcher], bot: Bot, event: MessageEvent
):
    try:
        with open(path_set,"r")as f:
            data = json.load(f)
            if what == "setting" or what == "s":
                what_name = "现在的设置如下：\n"
                data["setting"][0]["negative_prompt"]="too much"
                info = what_name+json.dumps(data["setting"][0],indent=2)
            elif what == "method" or what == "m":
                what_name = "拥有的风格和尺寸调整方式如下：\n"
                info = what_name+json.dumps(data["setting"][1],indent=2)
                
            else:
                msg="错误的指定！"
                return msg
            img = image(b64=(await text2image(info, font_size=25, color="#f9f6f2")).pic2bs4())
            
        msg = img
            
    except Exception as e:
        
        msg = f"aidraw配置展示出错了,查看报错{type(e)}:{e}"
    
    return msg


    
