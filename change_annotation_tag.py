"""
转换注释标志（py>=3.9)

API 文档里的实例数据一般都是 json 的，其中的注释标志是 `//`，本脚本将其转换为 `#`

utools 快捷命令配置
    - 环境：python（调用的本机解释器）
    - 特殊命令：{{ClipText}（剪切板内容）
"""


def convert(api_text: str) -> str:
    lines = []
    for line in api_text.split("\n"):
        index = line.find("//")
        if index == -1:
            lines.append(line)
            continue

        left_str, right_str = line[:index], line[index + 2 :]

        # // 开头的情况
        if left_str.strip() == "":
            lines.append(left_str + "# " + right_str.strip())
            continue

        # // 前面是逗号的情况
        if left_str.rstrip()[-1] == ",":
            lines.append(left_str.rstrip() + "  # " + right_str.strip())
            continue

        # 无法识别的情况
        lines.append(line)

    return "\n".join(lines)


def test():
    # 测试用例：内容、命令、结果
    test_case: list[tuple[str, str]] = [
        ("", ""),
        (
            """
//hhh

    //  hhh  
    abc,//kk
""",
            """
# hhh

    # hhh
    abc,  # kk
""",
        ),
    ]
    for input_text, result in test_case:
        now_result = convert(input_text)
        if now_result == result:
            print(".", end="")
        else:
            print("测试失败")
            print(f"{input_text=}")
            print(f"{result=}")
            print(f"{now_result=}")

    print()


def main():
    print(convert("""{{ClipText}}"""))


if __name__ == "__main__":
    test()
    # main()
