import shelve
from datetime import datetime
from typing import Dict, Optional, List

class TikTokData:
    def __init__(self, db_name: str = 'tiktok_data'):
        """初始化数据管理类
        Args:
            db_name: shelve数据库文件名
        """
        self.db_name = db_name

    def save_user_info(self, nickname: str, sec_uid: str, unique_id: str) -> None:
        """保存用户基本信息
        Args:
            nickname: 用户昵称
            sec_uid: 用户secUid
            unique_id: 用户uniqueId
        """
        with shelve.open(self.db_name) as db:
            user_info = {
                'nickname': nickname,
                'sec_uid': sec_uid,
                'unique_id': unique_id,
                'last_update': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            db[f'user_{sec_uid}'] = user_info

    def save_latest_post(self, sec_uid: str, post_data: Dict) -> None:
        """保存用户最新作品信息
        Args:
            sec_uid: 用户secUid
            post_data: 作品数据，包含创建时间、作品ID、描述等
        """
        with shelve.open(self.db_name) as db:
            key = f'latest_post_{sec_uid}'
            post_info = {
                'create_time': post_data.get('create_time'),
                'id': post_data.get('id'),
                'desc': post_data.get('desc'),
                'last_update': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            db[key] = post_info

    def get_user_info(self, sec_uid: str) -> Optional[Dict]:
        """获取用户信息
        Args:
            sec_uid: 用户secUid
        Returns:
            用户信息字典或None
        """
        with shelve.open(self.db_name) as db:
            return db.get(f'user_{sec_uid}')

    def get_latest_post(self, sec_uid: str) -> Optional[Dict]:
        """获取用户最新作品信息
        Args:
            sec_uid: 用户secUid
        Returns:
            最新作品信息字典或None
        """
        with shelve.open(self.db_name) as db:
            return db.get(f'latest_post_{sec_uid}')

    def get_all_users(self) -> List[Dict]:
        """获取所有已存储的用户信息
        Returns:
            用户信息列表
        """
        users = []
        with shelve.open(self.db_name) as db:
            for key in db.keys():
                if key.startswith('user_'):
                    users.append(db[key])
        return users

    def update_user_data(self, sec_uid: str, user_data: Dict, post_data: Dict) -> None:
        """更新用户信息和最新作品
        Args:
            sec_uid: 用户secUid
            user_data: 用户数据
            post_data: 作品数据
        """
        self.save_user_info(
            nickname=user_data.get('nickname'),
            sec_uid=sec_uid,
            unique_id=user_data.get('unique_id')
        )
        self.save_latest_post(sec_uid, post_data)

    def is_post_updated(self, sec_uid: str, new_post_time: int) -> bool:
        """检查是否有新作品
        Args:
            sec_uid: 用户secUid
            new_post_time: 新作品的创建时间戳
        Returns:
            是否有更新
        """
        latest_post = self.get_latest_post(sec_uid)
        if not latest_post:
            return True
        
        # 获取存储的最新作品时间
        stored_time = latest_post.get('create_time')
        if not stored_time:
            return True
            
        # 转换为整数进行比较
        try:
            stored_time = int(stored_time)
            new_post_time = int(new_post_time)
        except (ValueError, TypeError):
            return True
            
        # 比较时间戳，新的时间戳更大
        return new_post_time > stored_time

# 使用示例
"""
# 创建数据管理实例
data_manager = TikTokData()

# 保存用户信息
data_manager.save_user_info(
    nickname="用户昵称",
    sec_uid="MS4wLjABAAAA...",
    unique_id="username"
)

# 保存最新作品
post_data = {
    'create_time': '1648888888',
    'id': '7123456789',
    'desc': '视频描述'
}
data_manager.save_latest_post("MS4wLjABAAAA...", post_data)

# 获取用户信息
user_info = data_manager.get_user_info("MS4wLjABAAAA...")
print(user_info)

# 获取最新作品
latest_post = data_manager.get_latest_post("MS4wLjABAAAA...")
print(latest_post)

# 检查是否有新作品
has_update = data_manager.is_post_updated("MS4wLjABAAAA...", 1648888999)
print(f"Has new post: {has_update}")
"""