"""一键启动 SQL 随身教练（无需 Electron 时使用）"""
import os
import sys
import subprocess


def main():
    print("=" * 50)
    print("  🏠 SQL随身教练")
    print("  基于 DeepSeek-V4-Pro 的 SQL 辅助学习系统")
    print("=" * 50)

    if not os.path.exists("venv"):
        print("\n⚠️ 未找到虚拟环境，正在创建...")
        subprocess.run([sys.executable, "-m", "venv", "venv"])
        print("✅ 虚拟环境已创建")

    print("\n🚀 正在启动应用...")
    print("📱 浏览器将自动打开 http://localhost:8501")
    print("   如果未自动打开，请手动访问该地址")
    print("\n按 Ctrl+C 退出\n")

    subprocess.run([
        sys.executable, "-m", "streamlit", "run", "app.py",
        "--server.port", "8501"
    ])


if __name__ == "__main__":
    main()
