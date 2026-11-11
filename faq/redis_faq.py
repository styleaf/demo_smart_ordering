import redis
from difflib import SequenceMatcher


def add_redis(input_id: str, question: str, answer: str) -> None:
    """把一条固定问答写入 Redis。

    参数:
        input_id: 短名字，例如 business_hours。不要自己加 faq: 前缀。
        question: 问题原文。
        answer: 对应答案原文。

    返回:
        无。哈希键是 faq:短名字，目录集合是 faq:ids。
    """
    client = redis.Redis(host="localhost", port=6379, decode_responses=True)
    client.hset(
        "faq:" + input_id,
        mapping={"question": question, "answer": answer},
    )
    client.sadd("faq:ids", input_id)


def read_question_answer() -> list[dict]:
    """读出 Redis 里全部固定问答。

    参数:
        无。

    返回:
        字典列表。每个字典含 question 和 answer。空哈希会被跳过。
    """
    client = redis.Redis(host="localhost", port=6379, decode_responses=True)
    redis_list = []
    for faq_id in client.smembers("faq:ids"):
        item = client.hgetall("faq:" + faq_id)
        if item:
            redis_list.append(item)
    return redis_list


def find_similar_question(user_text: str) -> dict:
    """按字面重叠，找和顾客输入最接近的一条固定问答。

    参数:
        user_text: 顾客正在输入的那句话。

    返回:
        匹配到时返回含 question、answer 的字典。
        最高分低于 0.2 时返回 {"answer": None}。
        比较的是字符重叠，不是语义。
    """
    similar_dict = None
    best_score = -1
    for qa_dict in read_question_answer():
        score = SequenceMatcher(None, user_text, qa_dict["question"]).ratio()
        if score > best_score:
            best_score = score
            similar_dict = qa_dict
    if best_score < 0.2:
        return {"answer": None}
    return similar_dict
