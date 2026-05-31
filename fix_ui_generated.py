from pathlib import Path
import re


FILES = [
    Path("app/view/main_windown.py"),
    Path("app/view/login_view.py"),
    Path("app/view/register_view.py"),
]


def fix_file(path: Path):
    if not path.exists():
        print(f"Bỏ qua, không thấy file: {path}")
        return

    text = path.read_text(encoding="utf-8")

    text = text.replace(
        "QtWidgets.QSpacerItem(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)",
        "QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)"
    )

    text = text.replace(
        "QtWidgets.QSpacerItem(QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)",
        "QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)"
    )

    text = re.sub(
        r"self\.(\w+)\.setClass\(_translate\([^)]+,\s*\"([^\"]+)\"\)\)",
        r'self.\1.setProperty("class", "\2")',
        text
    )

    text = re.sub(
        r"self\.(\w+)\.setClass\(\"([^\"]+)\"\)",
        r'self.\1.setProperty("class", "\2")',
        text
    )

    path.write_text(text, encoding="utf-8")
    print(f"Đã fix: {path}")


def main():
    for file in FILES:
        fix_file(file)

    print("Hoàn tất fix file py generate từ ui.")


if __name__ == "__main__":
    main()