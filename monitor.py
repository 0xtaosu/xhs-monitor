from xhs import XhsClient
import time
from typing import List
from config import XHS_CONFIG, MONITOR_CONFIG
from utils import xhs_sign
from db import Database
from comment_generator import CommentGenerator

class XHSMonitor:
    def __init__(self, cookie: str):
        """
        初始化监控类
        :param cookie: 小红书cookie
        """
        self.client = XhsClient(cookie=cookie, sign=xhs_sign)
        self.db = Database()
        self.error_count = 0
        self.comment_generator = CommentGenerator()
        
    def send_error_notification(self, error_msg: str):
        """
        发送错误通知
        :param error_msg: 错误信息
        """
        print(f"Error: {error_msg}")
    
    def get_latest_notes(self, user_id: str) -> List[dict]:
        """
        获取用户最新笔记
        :param user_id: 用户ID
        :return: 笔记列表
        """
        try:
            res_data = self.client.get_user_notes(user_id)
            self.error_count = 0
            return res_data.get('notes', [])
            
        except Exception as e:
            error_msg = str(e)

            print(f"获取用户笔记失败: {error_msg}")

            time.sleep(60)

            self.error_count += 1

            if self.error_count >= MONITOR_CONFIG["ERROR_COUNT"]:
                self.send_error_notification(f"API 请求失败\n详细信息：{error_msg}")
                exit(-1)

            return []

    def like_note(self, note_id: str) -> bool:
        """
        点赞笔记
        :param note_id: 笔记ID
        :return: 是否成功
        """
        try:
            time.sleep(MONITOR_CONFIG["LIKE_DELAY"])  # 添加延迟，避免操作过快
            self.client.like_note(note_id)
            print(f"点赞成功: {note_id}")
            return True
        except Exception as e:
            print(f"点赞失败: {e}")
            return False

    def get_note_detail(self, note_id: str, xsec: str) -> dict:
        """
        获取笔记详细信息
        :param note_id: 笔记ID
        :return: 笔记详细信息
        """
        try:
            uri = '/api/sns/web/v1/feed'
            data = {"source_note_id":note_id,"image_formats":["jpg","webp","avif"],"extra":{"need_body_topic":"1"},"xsec_source":"pc_search","xsec_token": xsec}
            res = self.client.post(uri, data=data)
            note_detail = res["items"][0]["note_card"]
            return note_detail
        except Exception as e:
            print(f"获取笔记详情失败: {e}")
            return {}

    def comment_note(self, note_id: str, note_data: dict) -> dict:
        """
        评论笔记
        :param note_id: 笔记ID
        :param note_data: 笔记数据
        :return: 评论结果
        """
        try:
            print(f"开始处理评论 - note_id: {note_id}")
            time.sleep(MONITOR_CONFIG["COMMENT_DELAY"])
            
            print(f"获取笔记详情 - xsec_token: {note_data.get('xsec_token', '')}")
            note_detail = self.get_note_detail(note_id, note_data.get('xsec_token', ''))
            print(f"笔记详情: {note_detail}")
            
            title = note_detail.get('title', '')
            content = note_detail.get('desc', '')
            
            note_type = '视频' if note_detail.get('type') == 'video' else '图文'
            content = f"这是一个{note_type}笔记。{content}"
            
            print(f"生成评论 - 标题: {title}, 内容: {content}")
            comment = self.comment_generator.generate_comment(title, content)
            print(f"生成的评论内容: {comment}")
            
            self.client.comment_note(note_id, comment)
            
            print(f"评论成功: {note_id} - {comment}")
            return { "comment_status": True, "comment_content": comment }
        except Exception as e:
            print(f"评论失败，详细错误: {str(e)}")
            return { "comment_status": False, "comment_content": "" }

    def interact_with_note(self, note_data: dict) -> dict:
        """
        与笔记互动（点赞+评论）
        :param note_data: 笔记数据
        :return: 互动结果
        """
        result = {
            "like_status": False,
            "comment_status": False,
            "comment_content": ""
        }
        
        if not MONITOR_CONFIG.get("AUTO_INTERACT"):
            return result

        note_id = note_data.get('note_id')
        if not note_id:
            return result

        result["like_status"] = self.like_note(note_id)
        
        comment_result = self.comment_note(note_id, note_data)

        result["comment_status"] = comment_result["comment_status"]
        
        result["comment_content"] = comment_result["comment_content"]
        
        return result

    def send_note_notification(self, note_data: dict, interact_result: dict = None):
        """
        发送笔记通知
        :param note_data: 笔记数据
        :param interact_result: 互动结果
        """
        note_url = f"https://www.xiaohongshu.com/explore/{note_data.get('note_id')}"
        user_name = note_data.get('user', {}).get('nickname', '未知用户')
        title = note_data.get('display_title', '无标题')
        type = note_data.get('type', '未知类型')
        time_str = time.strftime('%Y-%m-%d %H:%M:%S')
        
        content = [
            "小红书用户发布新笔记",
            f"用户：{user_name}",
            f"标题：{title}",
            f"链接：{note_url}",
            f"类型：{type}",
        ]
        
        if interact_result and MONITOR_CONFIG.get("AUTO_INTERACT"):
            like_status = "成功" if interact_result["like_status"] else "失败"
            content.append(f"点赞：{like_status}")
            
            if interact_result["comment_status"]:
                content.append(f"评论：成功")
                content.append(f"评论内容：{interact_result['comment_content']}")
            else:
                content.append(f"评论：失败")
        
        content.append(f"监控时间：{time_str}")
        
        print("\n".join(content))

    def monitor_user(self, user_id: str, interval: int):
        """
        监控用户动态
        :param user_id: 用户ID
        :param interval: 检查间隔(秒)
        """
        print(f"开始监控用户: {user_id}")
        
        while True:
            try:
                latest_notes = self.get_latest_notes(user_id)
                
                existing_notes = self.db.get_user_notes_count(user_id)
                is_first_monitor = existing_notes == 0 and len(latest_notes) > 1
                
                if is_first_monitor:
                    welcome_msg = (
                        f"欢迎使用 xhs-monitor 系统\n"
                        f"监控用户：{latest_notes[0].get('user', {}).get('nickname', user_id)}\n"
                        f"首次监控某用户时，不会对历史笔记进行自动点赞和评论，仅保存笔记记录\n"
                        f"以防止被系统以及用户发现"
                    )
                    print(welcome_msg)
                    
                    for note in latest_notes:
                        self.db.add_note_if_not_exists(note)
                else:
                    for note in latest_notes:
                        if self.db.add_note_if_not_exists(note):
                            print(f"发现新笔记: {note.get('display_title')}")
                            interact_result = self.interact_with_note(note)
                            self.send_note_notification(note, interact_result)
                        
            except Exception as e:
                error_msg = str(e)
                print(f"监控过程发生错误: {error_msg}")
            time.sleep(interval)

def main():
    monitor = XHSMonitor(
        cookie=XHS_CONFIG["COOKIE"],
    )

    monitor.monitor_user(
        user_id=MONITOR_CONFIG["USER_ID"],
        interval=MONITOR_CONFIG["CHECK_INTERVAL"]
    )

if __name__ == "__main__":
    main() 