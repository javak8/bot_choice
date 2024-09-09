# encoding:utf-8


import requests

import plugins
from bridge.context import ContextType
from bridge.reply import Reply, ReplyType
from channel.chat_message import ChatMessage
import datetime

from plugins import *

@plugins.register(
    name="BotChoice",
    desire_priority=88,
    hidden=False,
    desc="根据不同关键词调用对应任务型model或bot",
    version="0.0.1",
    author="KevinZhang",
)
class BotChoice(Plugin):

    bot_list = [{"url":"http://10.75.190.8:2029","model":"搜图片"},{"url":"http://10.75.190.8:2029","keyword":"视频文案"}]
    max_words = 8000


    def __init__(self):
        super().__init__()
        try:
            self.config = super().load_config()
            if not self.config:
                self.config = self._load_config_template()
            self.bot_list = self.config.get("bot_list", self.bot_list)
            self.max_words = self.config.get("max_words", self.max_words)
            self.short_help_text = self.config.get("short_help_text",'发送特定指令以调度不同任务的bot！')
            self.long_help_text = self.config.get("long_help_text", "📚 发送关键词执行任务bot！\n🎉 娱乐与资讯：\n🌅 搜图: 发送“/搜图片 xxx”搜索你想要的图片。\n🐟 视频文案: 发送“/视频文案 链接地址”解析视频文案。\n🔥 文章: 发送“/文章 话题”生成爆款文案。\n")
            logger.info(f"[BotChoice] inited, config={self.config}")
            self.handlers[Event.ON_HANDLE_CONTEXT] = self.on_handle_context
        except Exception as e:
            logger.error(f"[BotChoice] 初始化异常：{e}")
            raise "[BotChoice] init failed, ignore "


    def get_help_text(self, verbose=False, **kwargs):
        if not verbose:
            return self.short_help_text

        return self.long_help_text

    def on_handle_context(self, e_context: EventContext, retry_count: int = 0):
        try:
            context = e_context["context"]
            msg:ChatMessage = context["msg"]
            content = context.content
            if context.type != ContextType.TEXT:
                return

            if retry_count == 0:
                logger.debug("[BotChoice] on_handle_context. content: %s" % content)
                reply = Reply(ReplyType.TEXT, "🎉正在执行，请稍候...")
                channel = e_context["channel"]
                channel.send(reply, context)

            content_new = content
            for bot in self.bot_list:
                if bot["keyword"] in content:
                    url = bot["url"]
                    model = bot["model"]
                    key = bot["key"]

                    # 多个指令时 全部处理掉
                    for keywords in self.bot_list:
                        content_new = content_new.replace(keywords["keyword"], "")
                    openai_chat_url = url + "/chat/completions"
                    openai_headers = self._get_openai_headers(key)
                    openai_payload = self._get_openai_payload(content_new, model)
                    headers = {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"}
                    logger.debug(
                        f"[BotChoice] openai_chat_url: {openai_chat_url}, openai_headers: {openai_headers}, openai_payload: {openai_payload}")
                    response = requests.post(openai_chat_url, headers={**openai_headers, **headers},
                                             json=openai_payload, timeout=80)
                    response.raise_for_status()
                    result = response.json()['choices'][0]['message']['content']

                    try:
                        result = json.loads(result)
                    except:
                        pass

                    if isinstance(result, list):
                        for value in result:
                            reply = Reply(self._get_content(value), value)
                            channel = e_context["channel"]
                            channel.send(reply, context)
                    if isinstance(result, str):
                        reply = Reply(ReplyType.TEXT, result)
                        channel = e_context["channel"]
                        channel.send(reply, context)

            e_context.action = EventAction.BREAK_PASS
            return

        except Exception as e:
            if retry_count < 3:
                logger.warning(f"[JinaSum] {str(e)}, retry {retry_count + 1}")
                self.on_handle_context(e_context, retry_count + 1)
                return

            logger.exception(f"[BotChoice] {str(e)}")
            reply = Reply(ReplyType.ERROR, "我暂时无法执行，请稍后再试")
            e_context["reply"] = reply
            e_context.action = EventAction.BREAK_PASS

    def _get_openai_headers(self, open_ai_api_key):
        return {
            'Authorization': f"Bearer {open_ai_api_key}",
            "Content-Type": "application/json"
        }

    def _get_content(self, content):
        imgs = ("jpg", "jpeg", "png", "gif", "img")
        videos= ("mp4", "avi", "mov", "pdf")
        files = ("doc", "docx", "xls", "xlsx", "zip", "rar", "txt")
        # 判断消息类型
        if content.startswith(("http://", "https://")):
            if content.lower().endswith(imgs) or self.contains_str(content, imgs):
                media_type = ReplyType.IMAGE_URL
            elif content.lower().endswith(videos) or self.contains_str(content, videos):
                media_type = ReplyType.VIDEO_URL
            elif content.lower().endswith(files) or self.contains_str(content, files):
                media_type = ReplyType.FILE_URL
            else:
                logger.error("不支持的文件类型")
        else:
            media_type = ReplyType.TEXT
        return media_type

    def _get_openai_payload(self, target_url_content, model):
        target_url_content = target_url_content[:self.max_words] # 通过字符串长度简单进行截断
        messages = [{"role": "user", "content": target_url_content}]
        payload = {
            'model': model,
            'messages': messages
        }
        return payload


    def contains_str(self, content,strs):
        for s in strs:
            if s in content:
                return True
        return False

    def _load_config_template(self):
        logger.debug("No Suno plugin config.json, use plugins/jina_sum/config.json.template")
        try:
            plugin_config_path = os.path.join(self.path, "config.json.template")
            if os.path.exists(plugin_config_path):
                with open(plugin_config_path, "r", encoding="utf-8") as f:
                    plugin_conf = json.load(f)
                    return plugin_conf
        except Exception as e:
            logger.exception(e)
