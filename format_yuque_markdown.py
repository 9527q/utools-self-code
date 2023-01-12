"""
格式化语雀导出的 markdown（py>=3.9)

语雀导出的 markdown 内容格式较乱，将其格式化为标准 markdown

utools 快捷命令配置
    - 环境：python（调用的本机解释器）

现有功能：

- 格式化标题
    - 给标题降低一级
    - 标题前后加空行
"""
import re
from typing import ClassVar, Iterable


def filter_class_family(objects: Iterable, top_class: ClassVar) -> list[ClassVar]:
    """过滤出一个类的家族（类自己、子类）"""
    class_list = []
    for obj in objects:
        if obj is top_class or (isinstance(obj, type) and issubclass(obj, top_class)):
            class_list.append(obj)

    return class_list


class Content:
    """记录内容"""

    def __init__(self, text: str = None, lines: list[str] = None):
        """
        text 和 lines 传一个
        """
        if text is not None:
            self._text = text
            self._lines = text.split("\n")
        elif lines is not None:
            self._text = "\n".join(lines)
            self._lines = lines
        else:
            raise ValueError("text 和 lines 传一个")

    @property
    def text(self) -> str:
        return self._text

    @property
    def lines(self) -> list[str]:
        return self._lines


class Format:
    """格式化操作类"""

    def format(self, origin_content: Content) -> Content:
        return origin_content


class FormatTitle(Format):
    """格式化标题（# 开头的标题）"""

    TITLE_RE = re.compile("^#+ .*")

    def format(self, origin_content: Content) -> Content:
        origin_lines = origin_content.lines
        lines = []

        for line_index, line in enumerate(origin_lines):
            if self.TITLE_RE.match(line):
                lines.append("#" + line)
                if previous := line_index - 1:
                    if origin_lines[previous].strip():
                        lines.insert(-1, "")
                if (next_index := line_index + 1) < len(origin_lines):
                    if origin_lines[next_index].strip():
                        lines.append("")
            else:
                lines.append(line)

        return Content(lines=lines)


class FormatManager:
    """格式化管理器"""

    @classmethod
    def get_all_format(cls) -> list[Format]:
        """所有格式化工具"""
        format_list = []
        for fmt_cls in filter_class_family(globals().values(), Format):
            format_list.append(fmt_cls())

        return format_list

    def format(self, origin_content: Content):
        content = origin_content

        for fmt in self.get_all_format():
            content = fmt.format(content)

        return content


def test():
    # 测试用例：内容、命令、结果
    test_case: list[tuple[str, str]] = [
        ("", ""),
        (
            """
# 一级标题
一些内容
## 二级标题
###非标题
""",
            """
## 一级标题

一些内容

### 二级标题

###非标题
""",
        ),
    ]
    fmt_manager = FormatManager()
    for input_text, correct_result in test_case:
        content = fmt_manager.format(Content(text=input_text))
        funcrun_result = content.text
        if funcrun_result == correct_result:
            print(".", end="")
        else:
            print("测试失败")
            print(f"{input_text=}")
            print(f"{correct_result=}")
            print(f"{funcrun_result=}")

    print()


def main():
    fmt_manager = FormatManager()
    input_content = Content(text="""{{ClipText}}""")
    output_content = fmt_manager.format(input_content)
    print(output_content.text)


if __name__ == "__main__":
    test()
    # main()
