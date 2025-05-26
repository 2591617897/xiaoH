import hashlib

# 多用户状态字典
user_states = {}

def normalize_user_id(user_id: str) -> str:
    """标准化用户 ID，使用 MD5 哈希"""
    return hashlib.md5(user_id.encode('utf-8')).hexdigest()

def get_user_state(user_openid: str):
    """获取或创建用户状态"""
    user_openid = normalize_user_id(user_openid)
    if user_openid not in user_states:
        user_states[user_openid] = {
            "buffer": "",
            "is_confirming": False,
            "pending_content": "",
            "started": False
        }
    return user_states[user_openid]

def reset_user_state(user_openid: str):
    """重置用户状态"""
    user_openid = normalize_user_id(user_openid)
    user_states[user_openid] = {
        "buffer": "",
        "is_confirming": False,
        "pending_content": "",
        "started": False
    }