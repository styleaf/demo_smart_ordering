import agent.chat


def show_stream():
    """逐块产出非空文本。"""
    pieces = agent.chat.restaurant_agent.stream(
        {"messages": [{"role": "user", "content": "你好"}]},
        config={"configurable": {"thread_id": "stream-test"}},
        stream_mode="messages",
    )
    for message, metadata in pieces:
        if message.content :          # 过滤掉空 content
            yield message.content


if __name__ == "__main__":
    for text in show_stream():
        print(text, end="", flush=True)