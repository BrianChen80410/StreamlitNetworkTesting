import matplotlib.pyplot as plt
import re
import streamlit as st
import subprocess
import time

def ping_ip(ip_address, ping_boundary):
    try:
        output = subprocess.check_output(['ping', ip_address, '-n', '1', '-w', str(ping_boundary)], 
                                         stderr=subprocess.STDOUT, 
                                         universal_newlines=True)
        ping_time_match = re.search('<1ms', output)
        if ping_time_match:
            return 0
        else:
            ping_time_match = re.search(r'=(\d+)ms', output)
            if ping_time_match:
                return ping_time_match.group(1)
            else:
                return None
    except subprocess.CalledProcessError as e:
        print(f'cmd ping error: {e.output}')
        return None

def plot_ping_times(ping_results):
    plt.figure(figsize=(8, 4), dpi=300)
    plt.title('Ping result')
    if len(ping_results) <= 30:
        plt.plot(range(1, len(ping_results)+1), ping_results, label='Ping', marker='o')
    else:
        plt.plot(range(1, len(ping_results)+1), ping_results, label='Ping')
    average = sum(ping_results) / len(ping_results)
    plt.axhline(average, label=f'average={average:.2f}', color='red', linestyle='--')
    plt.xlabel('Test times')
    plt.ylabel('Ping (ms)')
    plt.ylim(min(ping_results)-max(ping_results)*0.05, max(ping_results)*1.05)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    return plt

# Streamlit界面
st.set_page_config(
    page_title='網路穩定性測試',
    layout='centered',
)
st.title('網路穩定性測試')
# 設定測試目標
target_ip = st.selectbox('請選擇測試目標', 
                        ('chat.openai.com', 'one.one.one.one', 'www.google.com', '8.8.8.8', '8.8.4.4', '4.4.4.2'))
# 設定測試次數
test_count = st.number_input('請輸入測試次數', min_value=1, value=4)
# 設定測試時間上限
ping_boundary = st.number_input('請輸入測試時間上限（豪秒）', min_value=0, max_value=1000, value=500)
# 設定測試間隔時間
sleep_seconds = st.number_input('請輸入測試間隔時間（秒）', min_value=0, value=1)

# 開始監測按鈕
if st.button('開始測試'):
    # 初始化一個空列表來儲存ping的結果
    ping_results = []
    with st.empty():
        with st.status('正在測試') as status: # 用來在測試期間保持輸出的動態更新
            for i in range(test_count):
                result = ping_ip(target_ip, ping_boundary)
                if result is not None:
                    txt = f'回覆自 {target_ip}: 時間={result}ms'
                    st.write(txt)
                    status.update(label=f'正在測試... {txt}', state='running')
                    # 將結果新增至列表中
                    ping_results.append(int(result))
                else:
                    txt = '要求等候逾時'
                    st.write(txt)
                    status.update(label=f'正在測試... {txt}', state='running')
                    # 如果逾時，可以增加一個None或特殊值，例如9999或-1，來表示逾時
                    ping_results.append(ping_boundary)
                # 如果不是最後一次測試，則休息測試間隔時間
                if i < test_count - 1:
                    time.sleep(sleep_seconds)
                else:
                    st.write(f'結束測試')
                    status.update(label='測試完畢', state='complete', expanded=False)
                    st.toast('測試完畢', icon='🎉')
    with st.empty():
        with st.container(border=True):
            st.write('測試結果圖表')
            # 監測結束後繪製圖表
            plt = plot_ping_times(ping_results)
            st.pyplot(plt)
            st.toast('測試結果圖表繪製完畢', icon='🎉')