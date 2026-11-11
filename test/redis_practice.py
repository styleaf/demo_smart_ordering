import redis

INDEX = 0

client = redis.Redis(
    host="localhost", port=6379, decode_responses=True, db=2
)




def random_str(min_len=3, max_len=6) -> str:
    import random
    import string
    length = random.randint(min_len, max_len)
    chars = string.ascii_letters + string.digits   # a-z A-Z 0-9
    return ''.join(random.choices(chars, k=length))


# 测试



"""生成短链接并且存入redis中,短-长对应"""
def create_long_url(input_long:str) -> str:
    create_short_url = random_str()
    while is_no_unique(create_short_url):
        create_short_url = random_str()
    id = "id:"+str(INDEX)
    client.hset(id,mapping={"short_url":create_short_url,"long_url":input_long,"click_times":0})
    client.expire(id,604800)
    client.set(create_short_url,input_long)
    client.expire(create_short_url, 604800)
    #存储一个短url到id 的索引，好找到id
    client.set(create_short_url,id,ex=604800)
    return {"state":"200"}

"""访问短链接得到长连接"""
def by_short_to_long(input_short:str) -> str:
    if client.exists(input_short)==1:
        long_url = client.get(input_short)
        return long_url
    else:
        return "找不到"

"""点击短链接的统计"""
    #访问短链接，点击次数加1
def add_click_times(input_short:str):
    if client.exists(input_short)==1:
        client.hincrby(id, "click_times", 1)

def account_click_times(input_short:str) -> int:
    if client.exists(input_short)==1:
        id = client.get(input_short)
        times = client.hget(id,"click_times")
        return times
    else:
        return 0




"""判断短url是否唯一"""
def is_no_unique(input_short:str) -> bool:
    keys_list = client.keys("id:*")
    for key in keys_list:
        short_url = client.hget(key,"short_url")
        if short_url == input_short:
            return True
    return False

if __name__ == "__main__":
    pass
    # print(random_str())