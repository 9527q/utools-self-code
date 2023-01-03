"""
处理批量文本
    - 比如输入是从表格处复制的多行文本，可以对其进行处理
    - 如何区分输入的文本元素？根据换行符
    - 空行会被跳过

怎么增加新的命令功能？
    1. 新写命令类继承 `Command`
    2. 实现 `load_from_input_cmd` 和 `handle_content`
    3. 在 `test` 中增加测试用例
    4. 测试通过后，将代码整体复制到 uTools 快捷命令中

现有功能与对应命令
    - 引号
        - 【'】【‘】【’】：添加单引号
        - 【-'】【-‘】【-’】：删除单引号
        - 【"】【“】【”】：添加双引号
        - 【-"】【-“】【-”】：删除双引号
    - 逗号
        - 【,】【，】：添加逗号
        - 【-,】【-，】：删除逗号
    - 输出时换行连接
        - 默认以换行连接多行内容
        - 【-n】【-N】：输出不换行
"""
from typing import Callable, Optional, Type


class Content:
    """内容"""

    def __init__(self, items: list[str]):
        self.items = items  # 元素列表
        self.join = ""  # 输出连接符

    @classmethod
    def load_input(cls, input_content: str) -> "Content":
        """加载内容"""
        items = input_content.strip().split("\n")
        items = [i for item in items if (i := item.strip())]
        return cls(items=items)

    def output(self) -> str:
        """输出"""
        return self.join.join(self.items)

    def set_item(self, index: int, new_item: str):
        """设置内容"""
        self.items[index] = new_item


class Command:
    """命令"""

    ORDER = 99

    @classmethod
    def load_from_input_cmd(cls, input_cmd: str) -> Optional["Command"]:
        """根据命令判断是否加载自身"""
        return cls()

    def handle_content(self, content: Content):
        """处理函数"""


class CommandManager:
    """命令管理器"""

    def __init__(self):
        self.cmd_cls_list: list[Type[Command]] = []  # 所有的命令类
        self.load_local_command_cls()
        self.cmds: list[Command] = []  # 所有的命令实例

    def load_local_command_cls(self):
        """加载本地的命令类"""
        for o in globals().values():
            if o is Command:
                continue
            if isinstance(o, type) and issubclass(o, Command):
                self.cmd_cls_list.append(o)

    def add_command(self, command: Command):
        """添加命令"""
        self.cmds.append(command)

    @classmethod
    def load_from_input(cls, input_cmd: str) -> "CommandManager":
        """加载命令管理器"""
        manager = cls()

        for cmd_cls in manager.cmd_cls_list:
            if cmd := cmd_cls.load_from_input_cmd(input_cmd):
                manager.add_command(cmd)
        manager.cmds.sort(key=lambda c: c.ORDER)

        return manager

    def handle_content(self, content: Content):
        """处理内容"""
        for cmd in self.cmds:
            cmd.handle_content(content)


class CommandComma(Command):
    """逗号"""

    ORDER = 2

    def __init__(self):
        self.is_add = True  # 添加逗号还是删除逗号

    @classmethod
    def load_from_input_cmd(cls, input_cmd: str) -> Optional["Command"]:
        cmd = None
        if "-," in input_cmd or "-，" in input_cmd:
            cmd = cls()
            cmd.is_add = False
        elif "," in input_cmd or "，" in input_cmd:
            cmd = cls()
        return cmd

    def handle_content(self, content: Content):
        handle = self.get_handle()
        for i, item in enumerate(content.items):
            content.set_item(i, handle(item))

    def get_handle(self) -> Callable:
        """获取处理函数"""
        if self.is_add:
            return self.add_comma
        else:
            return self.remove_comma

    @staticmethod
    def add_comma(item: str):
        """添加逗号"""
        return f"{item.rstrip(',，')},"

    @staticmethod
    def remove_comma(item: str):
        """去除逗号"""
        return item.rstrip(",，")


class CommandWrap(Command):
    """换行"""

    def __init__(self):
        self.is_add_wrap = True  # 是否添加换行

    @classmethod
    def load_from_input_cmd(cls, input_cmd: str) -> Optional["Command"]:
        cmd = cls()
        if "-n" in input_cmd or "-N" in input_cmd:
            cmd.is_add_wrap = False
        return cmd

    def handle_content(self, content: Content):
        if self.is_add_wrap:
            content.join = "\n"
        else:
            content.join = ""


class CommandQuote(Command):
    """引号"""

    ORDER = 1

    def __init__(self):
        self.is_add_quote1: Optional[bool] = None  # 单引号
        self.is_add_quote2: Optional[bool] = None  # 双引号

    @classmethod
    def load_from_input_cmd(cls, input_cmd: str) -> Optional["Command"]:
        cmd = cls()
        if "-'" in input_cmd or "-‘" in input_cmd or "-’" in input_cmd:
            cmd.is_add_quote1 = False
        elif "'" in input_cmd or "‘" in input_cmd or "’" in input_cmd:
            cmd.is_add_quote1 = True
        elif '-"' in input_cmd or "-“" in input_cmd or "-”" in input_cmd:
            cmd.is_add_quote2 = False
        elif '"' in input_cmd or "“" in input_cmd or "”" in input_cmd:
            cmd.is_add_quote2 = True
        else:
            return None

        return cmd

    def handle_content(self, content: Content):
        handle = self.get_handle()
        for i, item in enumerate(content.items):
            content.set_item(i, handle(item))

    def get_handle(self) -> Callable:
        """获取处理函数"""
        if self.is_add_quote1 is not None:
            if self.is_add_quote1:
                return self.add_quote1
            else:
                return self.remove_quote1
        else:
            if self.is_add_quote2:
                return self.add_quote2
            else:
                return self.remove_quote2

    @staticmethod
    def add_quote1(item: str):
        """添加单引号"""
        return f"""'{item.strip("'‘’")}'"""

    @staticmethod
    def remove_quote1(item: str):
        """去除单引号"""
        return item.strip("'‘’")

    @staticmethod
    def add_quote2(item: str):
        """添加双引号"""
        return f'''"{item.strip('"“”')}"'''

    @staticmethod
    def remove_quote2(item: str):
        """去除双引号"""
        return item.strip('"“”')


def test():
    # 测试用例：内容、命令、结果
    test_case: list[tuple[str, str, str]] = [
        ("", "", ""),
        ("1\n2\n3", ",-n", "1,2,3,"),
        ("1,，\n2，,\n3,", "-，", "1\n2\n3"),
        ("1'\n2'\n3'", "-'", "1\n2\n3"),
        ("1\n2\n3", "'，", "'1',\n'2',\n'3',"),
        ("1\n2\n3", '"，', '"1",\n"2",\n"3",'),
    ]
    for input_content, input_command, result in test_case:
        content = Content.load_input(input_content)
        cmd_manager = CommandManager.load_from_input(input_command)
        cmd_manager.handle_content(content)
        now_result = content.output()
        if now_result == result:
            print(".", end="")
        else:
            print("测试失败")
            print(f"{input_content=}")
            print(f"{input_command=}")
            print(f"{now_result=}")
            print(f"{result=}")
            print(f"{cmd_manager.cmd_cls_list=}")
            print(f"{cmd_manager.cmds=}")
    print()


def main():
    # 加载内容
    content = Content.load_input("""{{ClipText}}""")
    # 加载命令管理器
    cmd_manager = CommandManager.load_from_input("""{{subinput:命令}}""")
    # 处理内容
    cmd_manager.handle_content(content)
    # 输出
    print(content.output())


if __name__ == "__main__":
    test()
    # main()
