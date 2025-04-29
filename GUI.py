import sys
import tkinter as tk
from pathlib import Path
from tkinter import ttk, filedialog, messagebox

from main import generate_pronunciation


class CantoneseApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("粤语歌词注音工具")
        self.geometry("600x400")
        self.create_widgets()
        exe_dir = Path(sys.argv[0]).parent
        default_input = exe_dir / 'lyrics.txt'
        if default_input.exists():
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, str(default_input))
            self.auto_generate_output(str(default_input))

    def drag_start(self, event):
        self._drag_start_x = event.x
        self._drag_start_y = event.y

    def drag_motion(self, event):
        x = self.winfo_x() + (event.x - self._drag_start_x)
        y = self.winfo_y() + (event.y - self._drag_start_y)
        self.geometry(f"+{x}+{y}")

    def create_widgets(self):
        # 创建自定义标题栏
        title_bar = ttk.Frame(self)
        title_bar.pack(side='top', fill='x')

        # 添加标题栏内的内容，例如标题和关闭按钮
        title_label = ttk.Label(title_bar, text="粤语歌词注音工具")
        title_label.pack(side='left', padx=5)

        # 绑定拖动事件到title_bar
        title_bar.bind('<ButtonPress-1>', self.drag_start)
        title_bar.bind('<B1-Motion>', self.drag_motion)

        # 文件选择部分
        file_frame = ttk.LabelFrame(self, text="歌词文件")
        file_frame.pack(pady=10, padx=10, fill="x")

        self.file_entry = ttk.Entry(file_frame)
        self.file_entry.pack(side="left", fill="x", expand=True, padx=5)
        ttk.Button(file_frame, text="浏览...", command=self.select_file).pack(side="left")

        # 输出设置
        output_frame = ttk.LabelFrame(self, text="输出设置")
        output_frame.pack(pady=10, padx=10, fill="x")

        self.output_var = tk.StringVar()
        ttk.Entry(output_frame, textvariable=self.output_var).pack(side="left", fill="x", expand=True, padx=5)
        ttk.Button(output_frame, text="选择...", command=self.select_output).pack(side="left")

        # 简繁体选择
        options_frame = ttk.Frame(self)
        options_frame.pack(pady=10, fill="x")

        self.conversion_var = tk.BooleanVar(value=False)
        ttk.Radiobutton(options_frame, text="简体", variable=self.conversion_var,
                        value=False).pack(side="left")
        ttk.Radiobutton(options_frame, text="繁体", variable=self.conversion_var,
                        value=True).pack(side="left")
        # 生成按钮
        ttk.Button(self, text="生成粤语注音", command=self.generate).pack(pady=20)

    def select_file(self):
        """文件选择对话框"""
        filetypes = [
            ("文本文件", "*.txt"),
            ("所有文件", "*.*")
        ]
        filepath = filedialog.askopenfilename(
            title="选择歌词文件",
            initialdir=Path.home(),
            filetypes=filetypes
        )
        if filepath:
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, filepath)
            self.auto_generate_output(filepath)

    def select_output(self):
        """输出路径选择"""
        initial_file = self.output_var.get() or "output_Cantonese.txt"
        filepath = filedialog.asksaveasfilename(
            title="保存注音文件",
            defaultextension=".txt",
            initialfile=initial_file,
            filetypes=[("文本文件", "*.txt")]
        )
        if filepath:
            self.output_var.set(filepath)

    def auto_generate_output(self, input_path):
        """自动生成默认输出路径"""
        if not self.output_var.get():
            try:
                input_path = Path(input_path)
                output_path = input_path.with_name(
                    f"{input_path.stem}_Cantonese.txt")
                self.output_var.set(str(output_path))
            except:
                pass

    def validate_inputs(self):
        """输入验证"""
        errors = []
        if not self.file_entry.get():
            errors.append("必须选择输入文件")
        elif not Path(self.file_entry.get()).exists():
            errors.append("输入文件不存在")

        if errors:
            messagebox.showerror("输入错误", "\n".join(errors))
            return False
        return True

    def generate(self):
        """生成按钮点击事件"""
        if not self.validate_inputs():
            return

        try:
            # 显示进度提示
            self.progress = ttk.Progressbar(
                self, mode="indeterminate", length=280)
            self.progress.pack(pady=10)
            self.progress.start()
            self.update_idletasks()

            # 调用核心功能
            generate_pronunciation(
                input_file=Path(self.file_entry.get()),
                output_file=Path(self.output_var.get()),
                conversion=self.conversion_var.get()
            )

            # 完成提示
            messagebox.showinfo(
                "完成",
                f"成功生成注音文件：\n{self.output_var.get()}"
            )
        except Exception as e:
            messagebox.showerror(
                "生成错误",
                f"生成失败：{str(e)}",
                detail="请检查：\n1. 输入文件编码是否为UTF-8\n2. 网络连接是否正常"
            )
        finally:
            if hasattr(self, 'progress'):
                self.progress.stop()
                self.progress.destroy()


def gui_main():
    """GUI入口"""
    app = CantoneseApp()
    # Windows平台优化
    if sys.platform == "win32":
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)  # 高DPI支持
    app.mainloop()


if __name__ == "__main__":  # 打包时专用入口
    gui_main()
