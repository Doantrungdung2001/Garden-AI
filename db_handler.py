import pymongo
import threading
import time
from bson.objectid import ObjectId
from datetime import datetime, timedelta

class MongoDBHandler:
    def __init__(self, mongo_uri, db_name):
        self.client = pymongo.MongoClient(mongo_uri)
        self.db = self.client[db_name]
        self.load_rtsp_links()

    def insert_detection_log(self, camera_id, start_time, end_time, video_url):
        # Chuyển đổi chuỗi thành datetime
        start_time_date = datetime.strptime(start_time, "%Y-%m-%d_%H-%M-%S")
        end_time_date = datetime.strptime(end_time, "%Y-%m-%d_%H-%M-%S")
        log_data = {
            "camera_id": camera_id,
            "start_time": start_time_date,
            "end_time": end_time_date,
            "video_url": video_url
        }
        self.db.ObjectDetections.insert_one(log_data)
    
    def insert_connection_log(self, camera_id, start_time, end_time):
        start_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))
        end_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end_time))
        log_data = {
            "camera_id": camera_id,
            "start_time": start_time,
            "end_time": end_time
        }
        self.db.ConnectionLosses.insert_one(log_data)

    def get_rtsp_links(self):
        links = []
        cursor = self.db.Cameras.find({}, {"_id": 0, "rtsp_link": 1})
        for document in cursor:
            links.append(document["rtsp_link"])
        return links

    def start_rtsp_links_watcher(self):
        def watch_rtsp_links():
            while True:
                # Lặp vô hạn để theo dõi thay đổi trong collection "Cameras"
                try:
                    # Kiểm tra thay đổi trong collection "Cameras"
                    camera_collection = self.db["Cameras"]
                    latest_change = camera_collection.find_one({}, sort=[('$natural', -1)])
                    if latest_change:
                        latest_change_time = latest_change['_id'].generation_time

                        if latest_change_time and (not self.last_change_time or latest_change_time > self.last_change_time):
                            print("Cập nhật danh sách RTSP URLs từ MongoDB...")
                            self.load_rtsp_links()
                            self.last_change_time = latest_change_time
                except Exception as e:
                    print(f"Lỗi khi kiểm tra thay đổi trong collection 'Cameras': {e}")
                
                # Chờ một khoảng thời gian trước khi kiểm tra lại
                time.sleep(10)

        self.last_change_time = None

        thread = threading.Thread(target=watch_rtsp_links)
        thread.start()
    def load_rtsp_links(self):
        self.rtsp_links = self.get_rtsp_links()