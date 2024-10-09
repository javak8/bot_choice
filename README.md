# bot_choice
BotChoice项目插件, 根据提示词调用不同bot/model,可以实现多指令执行

目前bot/model只支持openai接口规范

可以多指令执行 ，比如 /热点文案 /搜图片 杭州超市女老板走红

![wechat_mp](./docs/images/1725859906729.png))
![red](./docs/images/1725859997497.png))

config.json 配置说明
```json
{
  "max_words":1000,
 "bot_list":[
    {"url":"http://xxxx/v1","keyword":"/视频文案", "model":"/视频文案","key": "pat_5Dd01WUPwTK4"},
   {"url":"http://xxx/v1","keyword":"/热点文案", "model":"/热点文案","key": "pat_5Dd0BYoD3BmwTK4"},
   {"url":"http://xxxx/v1","keyword":"/搜图片", "model":"/搜图片","key": "pat_5Ddkw0TK4"}
 ],
  "short_help_text": "发送特定指令以调度不同任务的bot！",
  "long_help_text":  "📚 发送关键词执行任务bot！\n🎉 娱乐与资讯：\n🌅 搜图: 发送“/搜图片 xxx”搜索你想要的图片。\n🐟 视频文案: 发送“/视频文案 链接地址”解析视频文案。\n🔥 文章: 发送“/文章 话题”生成爆款文案。\n"
}

```

# 广告
最小化开发成本（近免费）可落地AI项目：本项目文档讲述利用头条，微头条/文章的AI自动生成的方式赚取收益
学习到python技术，服务器部署，国内模型有效利用，AI应用开发，AI应用平台使用，行业热门工具，系统架构集成
价值：启发，启蒙，编程，超级个体
https://icnyfaw3mn0d.feishu.cn/wiki/EahJwFXmji6RY0k4QAbcPodRnoc?from=from_copylink

