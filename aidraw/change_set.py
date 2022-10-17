import nonebot
from nonebot.adapters.onebot.v11 import (
    Bot,
    MessageEvent,
    Message,
    unescape,
)
from nonebot.permission import SUPERUSER
from nonebot import on_command
from nonebot.typing import T_State
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from typing import Type
from configs.path_config import TEXT_PATH
import json
from utils.message_builder import image
from utils.image_utils import text2image

__zx_plugin_name__ = "修改aidraw配置 [Superuser]"
__plugin_usage__ = """
usage：
    修改aidraw配置
    指令：
        drawset+name+value
""".strip()
__plugin_des__ = "修改aidraw配置"
__plugin_cmd__ = [
    "drawset+name+value",
]
__plugin_version__ = 0.1
__plugin_author__ = "lazi-pr"

math_se_list = ["step","denoising","b_count","b_size"]
path_set = TEXT_PATH / "aidraw_setting.json"
reload_aidraw = on_command("drawset", permission=SUPERUSER, priority=1, block=True)

@reload_aidraw.handle()
async def _(bot: Bot, event: MessageEvent, state: T_State, msg: Message = CommandArg()):
    msg = msg.extract_plain_text().strip().split()
    set_name = msg[0]
    set_value = msg[1]
    if set_name == "size":
        set_value = [x for x in msg[1:]]
    elif set_name == "negative_prompt":
        set_value = (" ").join(msg[1:]).split(",")
        set_value_ = []
        for value in set_value:
            value = unescape(value).strip()
            if value:
                set_value_.append(value)
        set_value = (",").join(set_value_)
    
    msg = await set_change(set_name,set_value,reload_aidraw,bot, event)

    await reload_aidraw.send(msg)

async def set_change(
set_name: str, set_value: str, matcher: Type[Matcher], bot: Bot, event: MessageEvent
):  
    
    
    try:
        with open(path_set,"r")as f:
            data = json.load(f)
        keys = list(data["setting"][0].keys())
        if set_name not in keys:
            msg = "参数不存在，请检查"
        else:
            if type(set_value) == list:
                keys_sn = list(data["setting"][0][set_name].keys())
                for num in range(len(set_value)):
                    data["setting"][0][set_name][keys_sn[num]] = int(set_value[num])
            else:
                # 对数字类型的参数数学化存储，方便setting_show观看
                data["setting"][0][set_name] = eval(set_value) if set_name in math_se_list else set_value
        
            with open(path_set, "w") as f:
                json.dump(data, f ,indent=4) 
            new_value = data["setting"][0][set_name]
            if set_name == "negative_prompt":
                msg = f"aidraw set Successful: {set_name} -> ok"
            else:
                msg = f"aidraw set Successful: {set_name}->{new_value}"
            
    except Exception as e:
        
        msg = f"修改出错了,查看报错{type(e)}:{e}"
    
    return msg
    

        


