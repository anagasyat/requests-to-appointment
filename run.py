import requests
import time
import threading

# 配置信息
url = "https://api2.lptiyu.com/bdlp_h5_fitness_test/public/index.php/index/Appoint/checkAppoint"
headers = {
    "Host": "api2.lptiyu.com",
    "Connection": "keep-alive",
    "Content-Length": "51",
    "Pragma": "no-cache",
    "Cache-Control": "no-cache",
    "sec-ch-ua-platform": '"Android"',
    "X-Requested-With": "XMLHttpRequest",
    "User-Agent": "",
    "Accept": "*/*",
    "sec-ch-ua": '"Not A(Brand";v="8", "Chromium";v="132", "Android WebView";v="132"',
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "sec-ch-ua-mobile": "?1",
    "Origin": "https://api2.lptiyu.com",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
    "Referer": "https://api2.lptiyu.com/bdlp_h5_fitness_test/view/fitness/homepage/appo-detail.html",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
    "Cookie": "这里填写你的cookie"
}

#以下参数根据你的抓包内容修改
# 预约信息
class_ids = {
    "08:30 - 10:00": "4359",
    "10:00 - 11:30": "4360",
    "14:30 - 16:00": "4361",
    "16:00 - 17:30": "4362"
}
dates = ["2025-03-16", "2025-03-22", "2025-03-23"]
location_id = "204"

#以下的预约逻辑谨慎修改，一般直接用就行
# 全局标志，用于指示是否已经预约成功
success_flag = False

def update_cookie(headers, class_id, class_time, test_time):
    """更新Cookie中的时间信息"""
    cookie_parts = headers["Cookie"].split("; ")
    cookie_dict = {}
    for part in cookie_parts:
        key, value = part.split("=", 1)
        cookie_dict[key] = value
    
    cookie_dict["COOKIE_APPO_CLASS_ID"] = class_id
    cookie_dict["COOKIE_APPO_CLASS_TIME"] = class_time
    cookie_dict["COOKIE_APPO_TEST_TIME"] = test_time
    
    updated_cookie = "; ".join([f"{k}={v}" for k, v in cookie_dict.items()])
    headers["Cookie"] = updated_cookie
    return headers

def send_request(date, time_slot, class_id):
    """发送单个预约请求"""
    global success_flag
    if success_flag:
        return  # 如果已经成功预约，直接返回
    
    test_time = time_slot.replace(" ", "%20")
    updated_headers = update_cookie(headers, class_id, date, test_time)
    
    data = {
        "class_id": class_id,
        "class_time": date,
        "location_id": location_id
    }
    try:
        response = requests.post(url, headers=updated_headers, data=data)
        response.raise_for_status()  # 检查请求是否成功
        result = response.json()
        print(result)
        if result.get("status") == 1:
            print(f"预约成功: 日期 {date}, 时间段 {time_slot}")
            success_flag = True  # 设置成功标志
            return True  # 预约成功，返回 True
        else:
            print(f"预约失败: 日期 {date}, 时间段 {time_slot}, 原因: {result.get('info')}")
            return False  # 预约失败，返回 False
    except Exception as e:
        print(f"预约检查失败: {e}")
        return False  # 请求失败，返回 False

def check_appoint():
    """检查预约"""
    global success_flag
    success_flag = False  # 每次检查前重置成功标志
    threads = []
    for date in dates:
        for time_slot, class_id in class_ids.items():
            thread = threading.Thread(target=send_request, args=(date, time_slot, class_id))
            threads.append(thread)
            thread.start()
    
    for thread in threads:
        thread.join()

if __name__ == "__main__":
    while True:
        check_appoint()
        if success_flag:
            break  # 预约成功，退出循环
        time.sleep(3)  # 预约失败，等待3秒后重试
