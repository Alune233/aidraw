import nonebot
from nonebot import on_command
from nonebot.adapters.onebot.v11 import (
    Bot,
    Message,
    MessageEvent,
    unescape,
)
from nonebot.params import CommandArg
from nonebot.typing import T_State
from typing import Type
from configs.config import Config
from nonebot.matcher import Matcher
from PIL import Image
from .data_source import get_img,split_msg,show_info
#from utils.utils import get_message_img

__zx_plugin_name__ = "A酱绘图"
__plugin_usage__ = """
usage：
    A酱绘图
    指令：
        ait2i+描述(英文)
        aii2i+描述(英文)+图片
        aii2i+@群友/qq号/回复图片+描述(英文)
        drawshow+s/m 查看当前(设置)/
        (拥有的风格、尺寸调整方式)
        加号组成部分以空格隔开
        
""".strip()
__plugin_des__ = "A酱绘图"
__plugin_cmd__ = [
    "ait2i/aii2i",
    "drawshow"
]
__plugin_type__ = ("一些工具",)
__plugin_version__ = 0.1
__plugin_author__ = "lazi-pr"
__plugin_settings__ = {
    "level": 5,
    "default_status": True,
    "limit_superuser": False,
    "cmd": [
        "ait2i",
        "aii2i",
        "drawshow"
    ],
}


t2i = on_command("ait2i", priority=5, block=True)
i2i = on_command("aii2i", priority=5, block=True)
show_aidraw = on_command(
    "drawshow", priority=5, block=True
)

@t2i.handle()
async def _(bot: Bot, event: MessageEvent, state: T_State, msg: Message = CommandArg()):
    msg = msg.extract_plain_text().strip()

    if len(msg) < 1:
        await t2i.finish("没有描述也要画图？")
    
    style = msg
    result = await get_img(12, style,'', t2i, bot, event)
    await t2i.send(Message(result))

@i2i.handle()
async def _(bot: Bot, event: MessageEvent, state: T_State):
    
    try:
        img_url,style = split_msg(event)
        result = await get_img(31, style,img_url, t2i, bot, event)
    except:
        result = "格式错误...或者你根本没图！"
    await i2i.send(Message(result))


@show_aidraw.handle()
async def _(bot: Bot, event: MessageEvent, state: T_State, msg: Message = CommandArg()):
    msg = msg.extract_plain_text().strip()

    if len(msg) < 1:
        await show_aidraw.finish("没有指定也要show？")
    
    what = msg
    msg = await show_info(what,show_aidraw,bot, event)
    
    await show_aidraw.send(msg)


