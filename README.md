# 密码管理程序跨平台打包指南

本项目是一个基于Python和tkinter的密码管理程序，目前支持在Windows、Linux和Android平台上使用。以下是将程序打包为不同平台安装包的详细指南。

## 项目概述
- 基于Python标准库中的tkinter构建GUI界面
- 无需安装额外依赖包
- 支持密码保护的内容管理
- 支持DEB和APK文件的安装辅助功能

## 已实现的打包

### Windows平台 (.exe)
程序已经可以在Windows上使用PyInstaller打包为可执行文件：

```bash
pyinstaller --onefile --windowed --name=密码管理器 password_manager.py
```

生成的可执行文件位于`dist`目录下。

## Linux平台打包为DEB文件

要在Linux系统上将程序打包为DEB格式安装包，需要以下步骤：

### 前提条件
- 在Linux系统（如Ubuntu、Debian）上操作
- 安装必要的打包工具

```bash
sudo apt-get update
sudo apt-get install python3 python3-tk python3-pip build-essential debhelper dh-python
```

### 步骤1：创建DEB打包目录结构

```bash
mkdir -p password-manager-deb/DEBIAN
mkdir -p password-manager-deb/usr/bin
mkdir -p password-manager-deb/usr/share/password-manager
mkdir -p password-manager-deb/usr/share/applications
```

### 步骤2：创建控制文件

创建`password-manager-deb/DEBIAN/control`文件，内容如下：

```
Package: password-manager
Version: 1.0
Section: utils
Priority: optional
Architecture: all
Depends: python3, python3-tk
Maintainer: Your Name <your.email@example.com>
Description: 简单的密码管理工具
  一款基于Python的密码管理程序，支持安全存储和管理密码信息。
```

### 步骤3：复制程序文件

```bash
# 复制主程序文件
cp password_manager.py password-manager-deb/usr/share/password-manager/

# 创建启动脚本
cat > password-manager-deb/usr/bin/password-manager << 'EOF'
#!/bin/bash
python3 /usr/share/password-manager/password_manager.py
EOF

# 设置脚本可执行权限
chmod +x password-manager-deb/usr/bin/password-manager
```

### 步骤4：创建桌面快捷方式

创建`password-manager-deb/usr/share/applications/password-manager.desktop`文件：

```
[Desktop Entry]
Name=密码管理程序
Comment=简单的密码管理工具
Exec=password-manager
Icon=utilities-terminal
Terminal=false
Type=Application
Categories=Utility;
```

### 步骤5：构建DEB包

```bash
sudo chown -R root:root password-manager-deb
dpkg-deb --build password-manager-deb
```

生成的DEB包文件为`password-manager-deb.deb`，可以使用以下命令安装：

```bash
sudo dpkg -i password-manager-deb.deb
sudo apt-get install -f  # 修复可能的依赖问题
```

## Android平台打包为APK文件

将Python程序转换为Android应用(APK)需要使用Kivy或BeeWare等工具。这里我们使用Kivy作为示例：

### 前提条件
- 安装Python 3.8或更高版本
- 安装Kivy和Buildozer

```bash
pip install kivy buildozer
```

### 步骤1：初始化Buildozer配置

```bash
# 在项目目录中初始化
buildozer init
```

### 步骤2：修改buildozer.spec配置文件

编辑生成的`buildozer.spec`文件，设置以下关键配置：

```ini
# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = python3,kivy

# (str) Title of your application
title = 密码管理程序

# (str) Package name
package.name = passwordmanager

# (str) Package domain (needed for android/ios packaging)
package.domain = org.example

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas

# (str) Application versioning (method 1)
version = 1.0

# (list) Permissions
sandroid.permissions = INTERNET
```

### 步骤3：创建Kivy适配层

由于原程序使用tkinter，需要创建一个Kivy适配层文件`main.py`：

```python
# main.py - Kivy适配层
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.modalview import ModalView
import subprocess
import sys
import os

# 导入原始的密码管理器功能
import password_manager as pm

class PasswordManagerApp(App):
    def build(self):
        # 这里需要根据原始程序的功能创建Kivy界面
        # 由于原程序使用tkinter，需要重新实现UI部分
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        title = Label(text='密码管理程序 (Android版)', font_size=20, size_hint=(1, 0.1))
        layout.add_widget(title)
        
        # 创建滚动文本区域
        scroll = ScrollView(size_hint=(1, 0.7))
        self.text_area = TextInput(text='内容已锁定，请输入密码解锁', readonly=True,
                                  background_color=(0.9, 0.9, 0.9, 1))
        scroll.add_widget(self.text_area)
        layout.add_widget(scroll)
        
        # 创建解锁按钮
        self.lock_button = Button(text='解锁', size_hint=(1, 0.15),
                                 background_color=(0.2, 0.8, 0.2, 1))
        self.lock_button.bind(on_press=self.toggle_lock)
        layout.add_widget(self.lock_button)
        
        # 初始化状态
        self.is_locked = True
        
        return layout
    
    def toggle_lock(self, instance):
        if self.is_locked:
            # 创建密码输入弹窗
            self.pw_popup = ModalView(size_hint=(0.8, 0.5))
            popup_layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
            
            label = Label(text='请输入密码解锁:')
            self.pw_input = TextInput(password=True, multiline=False)
            
            btn_layout = BoxLayout(spacing=10)
            cancel_btn = Button(text='取消')
            cancel_btn.bind(on_press=self.pw_popup.dismiss)
            
            ok_btn = Button(text='确定')
            ok_btn.bind(on_press=self.check_password)
            
            btn_layout.add_widget(cancel_btn)
            btn_layout.add_widget(ok_btn)
            
            popup_layout.add_widget(label)
            popup_layout.add_widget(self.pw_input)
            popup_layout.add_widget(btn_layout)
            
            self.pw_popup.add_widget(popup_layout)
            self.pw_popup.open()
        else:
            # 锁定逻辑
            self.text_area.text = '内容已锁定，请输入密码解锁'
            self.text_area.readonly = True
            self.lock_button.text = '解锁'
            self.is_locked = True
    
    def check_password(self, instance):
        # 这里简化处理，实际应用中应与原程序的密码验证逻辑保持一致
        password = self.pw_input.text
        self.pw_popup.dismiss()
        
        # 假设默认密码为'123456'
        if password == '123456':
            self.unlock_content()
        else:
            error_popup = Popup(title='错误', content=Label(text='密码错误！'),
                               size_hint=(0.6, 0.4))
            error_popup.open()
    
    def unlock_content(self):
        # 解锁内容
        self.text_area.text = '这里是解锁后的密码管理区域\n您可以在此输入和管理您的密码信息'
        self.text_area.readonly = False
        self.lock_button.text = '锁定'
        self.is_locked = False

if __name__ == '__main__':
    PasswordManagerApp().run()
```

### 步骤4：构建APK文件

```bash
# 首次运行会下载Android SDK、NDK等依赖，可能需要较长时间
# 确保有稳定的网络连接和足够的磁盘空间
buildozer android debug
```

生成的APK文件位于`bin`目录下，可以通过USB连接Android设备后安装：

```bash
# 安装到连接的设备
buildozer android deploy run
```

## 注意事项

1. **平台兼容性**：
   - DEB包主要适用于Debian系Linux发行版（如Ubuntu）
   - APK包需要Android设备或模拟器才能运行

2. **功能差异**：
   - Android版本由于平台限制，可能无法完全实现原程序的所有功能
   - 特别是文件操作和系统命令执行等功能在Android上受到严格限制

3. **依赖管理**：
   - Linux版本依赖Python 3和tkinter库
   - Android版本依赖Kivy框架

4. **安全性**：
   - 本程序提供基本的密码保护功能，适用于个人使用
   - 企业级应用建议使用更专业的加密和安全机制

## 常见问题解决

### Linux打包问题
- **依赖缺失**：使用`apt-get install -f`修复依赖问题
- **权限错误**：确保DEBIAN目录下的控制文件格式正确

### Android打包问题
- **内存不足**：Buildozer构建过程需要较大内存，建议至少4GB RAM
- **网络问题**：如遇SDK下载失败，可手动下载并配置环境变量
- **版本不兼容**：确保使用兼容的Python、Kivy和Buildozer版本

## 更新日志

- v1.0: 初始版本，支持Windows、Linux和Android平台
