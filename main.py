from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api.message_components import Plain, Image
from utils import get_user_state, reset_user_state
from logger import get_logger

_log = get_logger()


@register("contribution", "xiaoH", "匿名投稿插件", "1.0.0",
          "https://github.com/2591617897/xiaoH.git ")
class ContributionPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)

    @filter.command("投稿")
    async def start_contribution(self, event: AstrMessageEvent):
        try:
            raw_user_id = event.get_sender_id()
        except Exception:
            raw_user_id = event.message_obj.sender.user_openid

        user_openid = raw_user_id
        state = get_user_state(user_openid)
        reset_user_state(user_openid)

        help_text = (
            '👋 欢迎使用匿名投稿！\n\n'
            '请开始发送你的内容吧~\n'
            '完成后发送【结束】提交审核\n\n'
            '📌 请注意：\n'
            '禁止发布以下内容：\n'
            '❌ 涉及国家、社会、学校敏感话题\n'
            '❌ 不文明用语或攻击性言论\n'
            '❌ 任何形式的广告、推广信息\n\n'
            '📷 当前不支持图片发送，请仅发送文字内容\n\n'
            '💡 随时可用指令：\n'
            '【查看内容】预览当前稿件\n'
            '【清空内容】从头开始\n'
            '【取消】退出投稿流程'
        )
        yield event.plain_result(help_text)
        state["started"] = True

    @filter.command("结束")
    async def end_contribution(self, event: AstrMessageEvent):
        try:
            raw_user_id = event.get_sender_id()
        except Exception:
            raw_user_id = event.message_obj.sender.user_openid

        user_openid = raw_user_id
        state = get_user_state(user_openid)

        if not state["buffer"]:
            yield event.plain_result("⚠️ 还没有输入任何内容哦~")
            return

        state["is_confirming"] = True
        state["pending_content"] = state["buffer"]

        confirm_text = (
            '🔍 请确认要发送的内容：\n'
            f'{state["pending_content"]}\n\n'
            '📌 确认无误后，请发送【确认发送】\n'
            '🚫 若需修改，请发送【取消】'
        )
        yield event.plain_result(confirm_text)

    @filter.command("确认发送")
    async def confirm_send(self, event: AstrMessageEvent):
        try:
            raw_user_id = event.get_sender_id()
        except Exception:
            raw_user_id = event.message_obj.sender.user_openid

        user_openid = raw_user_id
        state = get_user_state(user_openid)

        if not state["is_confirming"]:
            yield event.plain_result("⚠️ 没有待确认的内容哦~")
            return

        target_channel_id = "11521792"  # 替换为实际频道 ID
        content_with_time = f"{state['pending_content']}\n\n🕒 提交时间：{event.message_obj.timestamp}"

        # 发送消息到目标频道
        await self.context.send_message(target_channel_id, content_with_time)

        yield event.plain_result("🎉 内容已成功推送到频道！感谢你的投稿~")

        # 重置状态
        reset_user_state(user_openid)

    @filter.command("取消")
    async def cancel_operation(self, event: AstrMessageEvent):
        try:
            raw_user_id = event.get_sender_id()
        except Exception:
            raw_user_id = event.message_obj.sender.user_openid

        user_openid = raw_user_id
        state = get_user_state(user_openid)

        if state["is_confirming"]:
            state["is_confirming"] = False
            yield event.plain_result("↩️ 已退出确认模式，你可以继续编辑内容或重新发送【结束】")
        else:
            yield event.plain_result("⚠️ 当前没有可取消的操作哦")

    @filter.command("查看内容")
    async def show_content(self, event: AstrMessageEvent):
        try:
            raw_user_id = event.get_sender_id()
        except Exception:
            raw_user_id = event.message_obj.sender.user_openid

        user_openid = raw_user_id
        state = get_user_state(user_openid)

        if not state["buffer"]:
            yield event.plain_result("📄 当前还没有输入任何内容呢~")
        else:
            yield event.plain_result(
                f'📝 当前已输入内容：\n{state["buffer"]}\n\n'
                '输入:\n【清空内容】清空重新投稿\n【结束】结束投稿'
            )

    @filter.command("清空内容")
    async def clear_content(self, event: AstrMessageEvent):
        try:
            raw_user_id = event.get_sender_id()
        except Exception:
            raw_user_id = event.message_obj.sender.user_openid

        user_openid = raw_user_id
        reset_user_state(user_openid)
        yield event.plain_result("🧹 已帮你清空所有输入内容啦！")

    @filter.event_message_type(filter.EventMessageType.ALL)
    async def handle_normal_input(self, event: AstrMessageEvent):
        try:
            raw_user_id = event.get_sender_id()
        except Exception:
            raw_user_id = event.message_obj.sender.user_openid

        user_openid = raw_user_id
        state = get_user_state(user_openid)

        if not state["started"]:
            return

        if state["is_confirming"]:
            yield event.plain_result("⚠️ 请先完成当前操作：发送【确认发送】或【取消】")
            return

        message_str = event.message_str.strip()
        if not message_str:
            return

        state["buffer"] += message_str + '\n'

        if len(state["buffer"].split('\n')) % 5 == 0:
            prompt = '\n✨ 发送【结束】完成投稿，【查看内容】可预览'
            yield event.plain_result(prompt)
