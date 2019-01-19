MicroChat

微信辅助工具，用来将指定微信联系人的多段语音合并成一个 mp3

仅在 Linux 下测试通过

# Clone #
* git clone https://github.com/linzhanyu/MicroChat.git
* git submodule init
* git submodule update

# 安装依赖环境 #

Python 3.6

1. wxPython [安装教程](https://linzhanyu.github.io/python3/pip/wxpython/phoenix/2017/12/19/wxpython.html)

2. silk-v3-decoder

2.1. libmp3lame

2.2. libopencore-amrnb

2.3. libopencore-amrwb

2.4 ffmpeg
./configure --enable-libmp3lame --enable-libopencore-amrnb --enable-libopencore-amrwb --enable-version3 --enable-shared

3. Android SDK platform-tool

adb


# 运行 #

python3 Main.py


![image](https://raw.githubusercontent.com/linzhanyu/MicroChat/master/res/instruction.png)
		      


# 输出数据 #

在 data 目录中

# 未来发展规划 #

1. 自动区分多开微信
2. 将数据保存到不同的用户文件夹中 保存IMEI等数据存到对应配置文件
3. 多线程数据处理
4. 音频播放
