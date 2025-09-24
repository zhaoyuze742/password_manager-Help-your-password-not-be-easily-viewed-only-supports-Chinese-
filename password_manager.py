import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
import json
import os
import platform
import getpass
import webbrowser

class PasswordManager:
    def __init__(self, root):
        self.root = root
        self.root.title("密码管理程序")
        self.root.geometry("800x500")  # 增加默认窗口大小
        self.root.minsize(600, 400)  # 设置最小窗口尺寸
        
        # 设置字体和颜色
        self.font = ("SimHei", 10)
        self.bg_color = "#f0f0f0"
        self.fg_color = "#000000"
        self.entry_bg = "#ffffff"
        
        # 获取应用数据目录（隐藏位置）
        self.app_data_dir = self._get_app_data_dir()
        
        # 初始化数据
        self.settings_file = os.path.join(self.app_data_dir, "settings.json")
        self.content_file = os.path.join(self.app_data_dir, "password_content.dat")
        self.master_password = self.load_settings()
        self.is_locked = True
        self.content = self.load_content()
        
        # 创建菜单
        self.create_menu()
        
        # 创建主界面
        self.create_main_frame()
        
        # 添加窗口关闭事件处理
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # 初始锁定状态
        self.lock_content()
    
    def _get_app_data_dir(self):
        """获取适合存储应用数据的隐藏目录"""
        username = getpass.getuser()
        system = platform.system()
        
        if system == "Windows":
            # Windows系统使用AppData\Roaming
            app_data = os.path.expandvars(r"%APPDATA%\PasswordManager")
        elif system == "Darwin":  # macOS
            app_data = os.path.expanduser(f"~/Library/Application Support/PasswordManager")
        else:  # Linux和其他系统
            app_data = os.path.expanduser(f"~/.password_manager")
        
        # 确保目录存在
        if not os.path.exists(app_data):
            os.makedirs(app_data, exist_ok=True)
        
        return app_data
        
    def create_menu(self):
        # 创建菜单栏
        menubar = tk.Menu(self.root)
        
        # 创建设置菜单
        setting_menu = tk.Menu(menubar, tearoff=0)
        setting_menu.add_command(label="更改主密码", command=self.change_master_password)
        menubar.add_cascade(label="设置", menu=setting_menu)
        
        # 创建帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="关于", command=self.show_about)
        help_menu.add_command(label="打开作者B站主页", command=self.open_bilibili)
        menubar.add_cascade(label="帮助", menu=help_menu)
        
        # 创建文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="打开DEB文件", command=self.open_deb_file)
        file_menu.add_command(label="打开APK文件", command=self.open_apk_file)
        menubar.add_cascade(label="文件", menu=file_menu)
        
        # 设置菜单栏
        self.root.config(menu=menubar)
    
    def create_main_frame(self):
        # 创建主框架
        main_frame = tk.Frame(self.root, bg=self.bg_color, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建标题标签
        title_label = tk.Label(main_frame, text="密码管理区域", font=(self.font[0], 12, "bold"), bg=self.bg_color)
        title_label.pack(pady=(0, 10))
        
        # 创建文本区域
        self.text_frame = tk.Frame(main_frame, bg=self.entry_bg, bd=1, relief=tk.SUNKEN)
        self.text_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 创建滚动条
        scrollbar = tk.Scrollbar(self.text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 创建文本区域
        self.text_area = tk.Text(self.text_frame, wrap=tk.WORD, font=self.font, yscrollcommand=scrollbar.set)
        self.text_area.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.text_area.yview)
        
        # 创建按钮框架
        button_frame = tk.Frame(main_frame, bg=self.bg_color, height=60)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        button_frame.pack_propagate(False)  # 防止框架自动调整大小
        
        # 创建锁定/解锁按钮
        self.lock_button = tk.Button(button_frame, text="解锁", command=self.toggle_lock, font=('SimHei', 12, 'bold'), width=15, height=2, bg="#4CAF50", fg="white", relief=tk.RAISED)
        # 使用grid布局确保按钮位置更稳定
        button_frame.grid_columnconfigure(0, weight=1)
        self.lock_button.grid(row=0, column=1, padx=20, pady=10, sticky="e")
    
    def load_settings(self):
        # 加载设置
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    return settings.get("master_password", "123456")  # 默认密码为123456
            except:
                return "123456"
        else:
            # 第一次运行，创建设置文件
            self.save_settings("123456")
            return "123456"
    
    def save_settings(self, password):
        # 保存设置
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump({"master_password": password}, f)
            return True
        except:
            return False
    
    def change_master_password(self):
        # 更改主密码
        current_password = simpledialog.askstring("输入当前密码", "请输入当前密码:", show='*')
        
        if current_password != self.master_password:
            messagebox.showerror("错误", "当前密码错误！")
            return
        
        new_password = simpledialog.askstring("输入新密码", "请输入新密码:", show='*')
        if not new_password:
            return
        
        confirm_password = simpledialog.askstring("确认新密码", "请再次输入新密码:", show='*')
        if new_password != confirm_password:
            messagebox.showerror("错误", "两次输入的密码不一致！")
            return
        
        if self.save_settings(new_password):
            self.master_password = new_password
            messagebox.showinfo("成功", "主密码已更改成功！")
        else:
            messagebox.showerror("错误", "保存密码失败！")
    
    def toggle_lock(self):
        # 切换锁定/解锁状态
        if self.is_locked:
            password = simpledialog.askstring("输入密码", "请输入密码解锁:", show='*')
            if password == self.master_password:
                self.unlock_content()
            elif password is not None:  # 用户没有点击取消
                messagebox.showerror("错误", "密码错误！")
        else:
            # 锁定前先保存最新内容
            self.content = self.text_area.get("1.0", "end-1c")
            if self.save_content():
                self.lock_content()
            else:
                messagebox.showerror("错误", "保存内容失败！")
    
    def lock_content(self):
        # 锁定内容
        # 清空并禁用文本区域
        self.text_area.delete("1.0", tk.END)
        self.text_area.insert("1.0", "内容已锁定，请输入密码解锁")
        self.text_area.config(state=tk.DISABLED, bg="#e0e0e0", fg="#808080")
        # 更改按钮文本
        self.lock_button.config(text="解锁")
        # 更新状态
        self.is_locked = True
    
    def unlock_content(self):
        # 解锁内容
        # 启用并恢复文本区域
        self.text_area.config(state=tk.NORMAL, bg=self.entry_bg, fg=self.fg_color)
        self.text_area.delete("1.0", tk.END)
        # 确保加载最新保存的内容
        self.content = self.load_content()
        self.text_area.insert("1.0", self.content)
        # 更改按钮文本
        self.lock_button.config(text="锁定")
        # 更新状态
        self.is_locked = False
    
    def show_about(self):
        # 显示关于信息
        messagebox.showinfo("关于", "密码管理程序 v1.0\n\n一款简单的密码管理工具，可以帮助您安全地存储和管理密码信息。")
    
    def open_bilibili(self):
        # 打开作者B站主页
        try:
            webbrowser.open("https://space.bilibili.com/123456789")  # 这里可以替换为实际的B站ID
            messagebox.showinfo("提示", "正在打开作者B站主页...")
        except Exception as e:
            messagebox.showerror("错误", f"打开B站主页失败: {str(e)}")
    
    def open_deb_file(self):
        # 打开并支持安装DEB文件
        if self.is_locked:
            messagebox.showinfo("提示", "请先解锁程序后再操作")
            return
        
        try:
            file_path = filedialog.askopenfilename(
                title="选择DEB文件",
                filetypes=[("DEB文件", "*.deb"), ("所有文件", "*.*")]
            )
            
            if file_path:
                # 显示文件路径到文本区域
                self.text_area.insert(tk.END, f"\n\n打开的DEB文件: {file_path}")
                
                # 获取当前系统类型
                current_system = platform.system()
                
                if current_system == "Linux":
                    # 在Linux系统上提供安装选项
                    self.text_area.insert(tk.END, "\n\nLinux系统下安装命令:\n")
                    self.text_area.insert(tk.END, f"sudo dpkg -i '{file_path}'")
                    self.text_area.insert(tk.END, "\n\nsudo apt-get install -f  # 修复依赖关系")
                    
                    # 询问是否直接运行安装命令
                    if messagebox.askyesno("安装DEB文件", "检测到您正在Linux系统上运行，是否直接打开终端执行安装命令？"):
                        # 尝试使用默认终端执行命令
                        try:
                            # 根据不同的Linux发行版尝试不同的终端
                            terminals = ["x-terminal-emulator", "gnome-terminal", "konsole", "xfce4-terminal", "lxterminal"]
                            terminal_found = False
                            
                            for terminal in terminals:
                                if os.system(f"which {terminal} > /dev/null") == 0:
                                    os.system(f'{terminal} -e "sudo dpkg -i {file_path}; echo 安装完成，按任意键退出; read"')
                                    terminal_found = True
                                    break
                            
                            if not terminal_found:
                                messagebox.showinfo("提示", "未找到支持的终端程序，请手动使用终端执行安装命令。")
                        except Exception as e_inner:
                            messagebox.showerror("错误", f"执行安装命令失败: {str(e_inner)}")
                else:
                    # 非Linux系统提供提示
                    self.text_area.insert(tk.END, "\n\n提示: 此文件为Linux系统的DEB安装包，在当前系统下无法直接安装。")
                    self.text_area.insert(tk.END, "\n如需安装，请将文件复制到Linux系统后使用 dpkg -i 命令安装。")
                
                # 滚动到末尾
                self.text_area.see(tk.END)
                messagebox.showinfo("成功", f"已选择DEB文件: {os.path.basename(file_path)}")
        except Exception as e:
            messagebox.showerror("错误", f"处理DEB文件失败: {str(e)}")
    
    def open_apk_file(self):
        # 打开并支持安装APK文件到Android设备
        if self.is_locked:
            messagebox.showinfo("提示", "请先解锁程序后再操作")
            return
        
        try:
            file_path = filedialog.askopenfilename(
                title="选择APK文件",
                filetypes=[("APK文件", "*.apk"), ("所有文件", "*.*")]
            )
            
            if file_path:
                # 显示文件路径到文本区域
                self.text_area.insert(tk.END, f"\n\n打开的APK文件: {file_path}")
                
                # 检查是否安装了ADB工具（Android Debug Bridge）
                has_adb = False
                try:
                    # 检查ADB是否可用
                    result = os.system("adb version >nul 2>&1" if platform.system() == "Windows" else "adb version >/dev/null 2>&1")
                    has_adb = (result == 0)
                except:
                    pass
                
                if has_adb:
                    # 检查是否有连接的Android设备
                    try:
                        # 执行adb devices命令查看连接的设备
                        temp_file = "temp_adb_devices.txt"
                        os.system(f"adb devices > {temp_file}" if platform.system() == "Windows" else f"adb devices > {temp_file}")
                        
                        with open(temp_file, 'r') as f:
                            devices_output = f.read()
                        
                        os.remove(temp_file)
                        
                        # 检查是否有设备连接
                        if "device" in devices_output and len(devices_output.splitlines()) > 2:
                            self.text_area.insert(tk.END, "\n\n检测到已连接的Android设备，可通过ADB安装此APK文件。")
                            
                            # 询问是否通过ADB安装
                            if messagebox.askyesno("安装APK文件", "检测到已连接的Android设备，是否通过ADB安装此APK文件？"):
                                try:
                                    # 执行安装命令
                                    install_command = f"adb install -r '{file_path}'"
                                    self.text_area.insert(tk.END, f"\n\n执行安装命令: {install_command}")
                                    
                                    # 在终端中执行安装命令并显示结果
                                    if platform.system() == "Windows":
                                        os.system(f"start cmd /k '{install_command} && echo 安装完成，按任意键退出 && pause'")
                                    else:
                                        # 尝试使用默认终端执行命令
                                        terminals = ["x-terminal-emulator", "gnome-terminal", "konsole", "xfce4-terminal", "lxterminal"]
                                        terminal_found = False
                                        
                                        for terminal in terminals:
                                            if os.system(f"which {terminal} > /dev/null") == 0:
                                                os.system(f"{terminal} -e '{install_command}; echo 安装完成，按任意键退出; read'")
                                                terminal_found = True
                                                break
                                        
                                        if not terminal_found:
                                            messagebox.showinfo("提示", "未找到支持的终端程序，请手动使用终端执行安装命令。")
                                except Exception as e_inner:
                                    messagebox.showerror("错误", f"执行安装命令失败: {str(e_inner)}")
                        else:
                            self.text_area.insert(tk.END, "\n\n未检测到已连接的Android设备。")
                            self.text_area.insert(tk.END, "\n请确保Android设备已开启USB调试并连接到计算机。")
                            
                            # 提供安装命令参考
                            self.text_area.insert(tk.END, f"\n\n安装命令参考: adb install -r '{file_path}'")
                    except Exception as e_inner:
                        self.text_area.insert(tk.END, f"\n\n检测Android设备时出错: {str(e_inner)}")
                else:
                    self.text_area.insert(tk.END, "\n\n提示: 未检测到ADB工具，无法直接安装APK到Android设备。")
                    self.text_area.insert(tk.END, "\n请安装Android SDK Platform Tools以启用APK安装功能。")
                    
                    # 针对Android系统的特殊提示
                    if platform.system() == "Linux":
                        self.text_area.insert(tk.END, "\n\nLinux系统下安装ADB命令参考:\n")
                        self.text_area.insert(tk.END, "sudo apt-get install android-tools-adb  # Ubuntu/Debian\n")
                        self.text_area.insert(tk.END, "sudo dnf install android-tools  # Fedora/RHEL\n")
                        self.text_area.insert(tk.END, "sudo pacman -S android-tools  # Arch Linux")
                
                # 滚动到末尾
                self.text_area.see(tk.END)
                messagebox.showinfo("成功", f"已选择APK文件: {os.path.basename(file_path)}")
        except Exception as e:
            messagebox.showerror("错误", f"处理APK文件失败: {str(e)}")
    
    def load_content(self):
        # 加载保存的内容
        if os.path.exists(self.content_file):
            try:
                with open(self.content_file, 'r', encoding='utf-8') as f:
                    return f.read()
            except:
                return ""
        else:
            return ""
    
    def save_content(self):
        # 保存内容到文件
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.content_file), exist_ok=True)
            # 获取当前文本区域的最新内容（不包含末尾的换行符）
            if not self.is_locked:
                current_content = self.text_area.get("1.0", "end-1c")
                with open(self.content_file, 'w', encoding='utf-8') as f:
                    f.write(current_content)
            else:
                with open(self.content_file, 'w', encoding='utf-8') as f:
                    f.write(self.content)
            return True
        except Exception as e:
            print(f"保存内容失败: {str(e)}")  # 实际应用中可以添加日志
            return False
    
    def on_closing(self):
        # 窗口关闭事件处理
        if not self.is_locked:
            # 如果内容未锁定，询问是否保存
            result = messagebox.askyesnocancel("保存", "是否保存当前内容？")
            if result is None:  # 用户点击了取消
                return
            if result:  # 用户点击了是
                # 确保获取最新内容
                self.content = self.text_area.get("1.0", "end-1c")
                success = self.save_content()
                if not success:
                    messagebox.showerror("错误", "保存内容失败！")
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordManager(root)
    root.mainloop()

#                            _ooOoo_
#                           o8888888o
#                           88" . "88
#                           (| -_- |)
#                            O\ = /O
#                        ____/`---'\____
#                      .   ' \\| |// `.
#                       / \\||| : |||// \
#                     / _||||| -:- |||||- \
#                       | | \\\ - /// | |
#                     | \_| ''\---/'' | |
#                      \ .-\__ `-` ___/-. /
#                   ___`. .' /--.--\ `. . __
#                ."" '< `.___\_<|>_/___.' >'"".
#               | | : `- \`.;`\ _ /`;.`/ - ` : | |
#                 \ \ `-. \_ __\ /__ _/ .-` / /
#         ======`-.____`-.___\_____/___.-`____.-'======
#                            `=---='
#
#         .............................................
#                  佛祖保佑             永无BUG