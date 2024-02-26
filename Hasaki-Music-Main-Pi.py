import requests
import time
import json
import public_ip as ip
import pygame
import os
import threading  
import datetime
import vlc
import sys



#location = ip.get()
location = '14.241.238.138'

def hasaki_ringtone():
    os.environ["OMP_NUM_THREADS"]= '1'
    os.environ["OMP_THREAD_LIMIT"] = '1'
    import cv2
    from yolov8 import YOLOv8
    import numpy as np

    def download_file(mp3_url, path_file):
        response = requests.get(mp3_url)
        with open(path_file, 'wb') as file:
            file.write(response.content)
        
        return path_file
    

    def play_mp3(file):
        pygame.mixer.init()
        pygame.mixer.music.load(file)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            time.sleep(1)

        pygame.mixer.quit()

        
    def is_point_inside_polygon(point, polygon):
        x, y = point
        result = cv2.pointPolygonTest(polygon, (x, y), False)
        return result > 0
    

    def detect(frame, polygon):
        boxes, scores, class_ids = yolov8_detector(frame)
        filtered_boxes = [box for box in boxes if is_point_inside_polygon(((box[0] + box[2]) // 2, (box[1] + box[3]) // 2), polygon)]
        return filtered_boxes, scores, class_ids
    


    try:
        model_url = "https://tenant03-io-api.app.rdhasaki.com/hasaki-voice/model.onnx"
        download_file(model_url, "model.onnx")
        yolov8_detector = YOLOv8("model.onnx", conf_thres=0.2, iou_thres=0.3) 
        mp3_url = "https://tenant03-io-api.app.rdhasaki.com/hasaki-voice/hasakixinchao1.mp3"
        download_file(mp3_url, "hasakixinchao1.mp3")
        
        url_channel = f'https://getchannel.app.rdhasaki.com/{location}'
        req = requests.get(url_channel).content.decode('utf-8')
        data_location = json.loads(req)[0]
        if location == data_location.get('locate'):
            port = data_location.get('port')
            channel = data_location.get('channel')
            
            i = 0
            cap = cv2.VideoCapture(f"rtsp://viennh:viennh11@{location}:{port}/cam/realmonitor?channel={channel}&subtype=0")
            r_box = requests.post(f"https://ai.hasaki.vn/control/check_light_is_on/getTask?IP={location}&port={port}&C={channel}").content.decode('utf-8')
            data_box_load = json.loads(r_box)
            data_box = data_box_load['json_list'][0]['PARAMS']['points']
            polygon = cv2.convexHull(np.array(data_box))

            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                i = i + 1
                if i % 5 == 0:
                    boxes, scores, class_ids = detect(frame, polygon)
                    if boxes:
                        for score in scores:
                            if score >= 0.83:
                                play_mp3("hasakixinchao1.mp3")
                                time.sleep(10)     

        elif location == '123.30.249.178':
            print('Không thể phát Hasaki Ringtone', 'Đang sử dụng VPN. Hãy tắt VPN và thử lại.')
            os._exit(0)
            
    
        
    except Exception as e:
        print('Không thể phát Hasaki Ringtone', 'Kiểm tra lại Internet.')
        print(str(e))
        os._exit(0)
        
   
def music_hasaki():
    api_url = f"https://wshr.hasaki.vn/api/hr/music/songs/current-file?category_id=1&ip={location}"
    r = requests.get(api_url)
    data = r.json()
    a = []
    data = data["data"]["advertisement"]
    for time_ads in data:
        a.append(time_ads["begin_time"])

    run_time = datetime.datetime.now().hour
    range_time = (22 <= run_time < 24) or (0 <= run_time < 8)
    running = True

    def music_stream():
        try:
            response = requests.get(api_url)
            if response.status_code == 200:
                data = response.json()
                file_path = data["data"]["current"]["file"]
                # Xây dựng URL đầy đủ cho file mp3
                base_url_music = f"https://wshr.hasaki.vn/production/music/{file_path}"
                response_file = requests.get(base_url_music, stream=True)
                if response_file.status_code == 200:
                    vlc_instance = vlc.Instance("--no-xlib --no-video --intf dummy --no-osd")
                    player = vlc_instance.media_player_new()
                    media = vlc_instance.media_new(base_url_music)
                    player.set_media(media)
                    player.play()

                    while player.get_state() != vlc.State.Ended:
                        if player.get_state() == vlc.State.Error:
                            restart_app()
                            time.sleep(1)
                        current_time = datetime.datetime.now().time().strftime("%H:%M:%S")
                        if current_time in a:
                            break
                        time.sleep(1)

                    player.stop()
                    player.release()
                    vlc_instance.release()
                else:
                    print('Không thể phát Hasaki Music', 'Kiểm tra lại Internet')
                    os._exit(0)
            else:
                print('Không thể phát Hasaki Music', 'Kiểm tra lại Internet.')
                os._exit(0)
        except:
            restart_app()

    def advertisement():
        response = requests.get(api_url)
        if response.status_code == 200:
            data_ads = response.json()
            data_ads = data_ads["data"]["advertisement"]
            
            current_time = datetime.datetime.now().time().strftime("%H:%M:%S")
            for ads in data_ads:
                if current_time == ads["begin_time"]:
                    ads_mkt = ads["file"]
                    base_url = f"https://wshr.hasaki.vn/production/music/{ads_mkt}"
                    
                    response_file = requests.get(base_url, stream=True)
                    if response_file.status_code == 200:
                        # Phát file mp3 bằng VLC Python
                        vlc_instance = vlc.Instance()
                        player = vlc_instance.media_player_new()
                        media = vlc_instance.media_new(base_url)
                        player.set_media(media)
                        player.play()

                        while player.get_state() != vlc.State.Ended:
                            time.sleep(1)

                        player.stop()
                        break
            else:
                pass
        else:
            pass


    def restart_app():
        global running
        running = False
        python = sys.executable
        os.execl(python, python, *sys.argv)

    while not range_time:
        current_time = datetime.datetime.now().time().strftime("%H:%M:%S")
        if str(current_time) in a:
            advertisement()
        else:
            try:        
                music_stream()
            except:
                time.sleep(5)
                restart_app()
                continue

if __name__ == "__main__":
    
    threading.Thread(target=hasaki_ringtone).start()
    threading.Thread(target=music_hasaki).start()
