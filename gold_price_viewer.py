# gold_price_viewer.py
import requests
import json
import logging
import pystray
from PIL import Image, ImageDraw
import threading

# 配置日志
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def fetch_gold_price():
    url = 'https://free.xwteam.cn/api/gold/trade'

    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data['code'] == 200:
                return data['data']
            else:
                raise Exception(f"API returned an unexpected response: {data}")
        else:
            raise Exception(f"HTTP error occurred: {response.status_code}")
    except requests.RequestException as e:
        logging.error(f"Request error occurred: {e}")
    except json.JSONDecodeError as e:
        logging.error(f"JSON decode error: {e}")
    except Exception as e:
        logging.error(f"Failed to fetch gold price: {e}")
        return None

def create_icon():
    # 创建一个简单的图标
    width = 64
    height = 64
    color1 = "yellow"
    color2 = "blue"
    image = Image.new('RGB', (width, height), color1)
    dc = ImageDraw.Draw(image)
    dc.rectangle(
        (width // 2, 0, width, height // 2),
        fill=color2)
    dc.rectangle(
        (0, height // 2, width // 2, height),
        fill=color2)
    return image

def update_tray_icon(data):
    if data is not None and 'LF' in data:
        for item in data['LF']:
            if item['Symbol'] == 'Au':
                tray_icon.title = f"黄金 - BP: {item['BP']} - SP: {item['SP']} - High: {item['High']} - Low: {item['Low']} - 更新时间: {data['UpTime']}"
                break
        else:
            tray_icon.title = "无法获取黄金信息"
    else:
        tray_icon.title = "无法获取金价信息"

def update_price_listbox():
    global tray_icon
    data = fetch_gold_price()
    if 'tray_icon' in globals() and tray_icon is not None:
        if data is not None:
            update_tray_icon(data)
        else:
            update_tray_icon(None)

def start_tray_icon():
    global tray_icon, tray_menu  # 将 tray_menu 定义为全局变量
    image = create_icon()
    tray_icon = pystray.Icon("gold_price_viewer", image, "Gold Price Viewer", menu=tray_menu)

    tray_icon.run()

def stop_tray_icon():
    tray_icon.stop()

def on_exit():
    stop_tray_icon()

def main():
    global tray_icon, tray_menu  # 将 tray_menu 定义为全局变量
    tray_menu = pystray.Menu(
        pystray.MenuItem('Update Now', update_price_listbox),
        pystray.MenuItem('退出', on_exit)
    )

    # 启动自动更新
    update_price_listbox()
    threading.Timer(10.0, update_price_listbox).start()  # 每 10 秒更新一次

    # 启动系统托盘图标
    start_tray_icon()

if __name__ == "__main__":
    main()