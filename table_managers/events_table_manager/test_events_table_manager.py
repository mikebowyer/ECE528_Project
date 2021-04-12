import logging
import time
from events_table_manager import EventTableManager
from table_managers.dashcam_images_table_manager.dashcam_table_manager import DashcamTableManager
# logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(name)s %(levelname)s:%(message)s')
# logger = logging.getLogger(__name__)


if __name__ == '__main__':

    event_table_manager = EventTableManager("events", True)
    dashcam_img_table_manager = DashcamTableManager("dashcam_images", True)

    try:
        while True:
            val = input(
                "\n### Options: ###\n\t0) Check if table exists\n\t1) Delete table\n\t2) List tables\n\t3) Put new item\n\t4) Scan table\n\t5) get image\n\t6) update image\n\t7) delete image\n\t8) get_imgs_in_GPS_bounds\n")
            if int(val) == 0:
                event_table_manager.check_if_table_exists()
            elif int(val) == 1:
                event_table_manager.delete_table()
            elif int(val) == 2:
                event_table_manager.list_tables()
            elif int(val) == 3:
                # lat = input("Enter your latitude value: ")
                # long = input("Enter your longitude value: ")
                # source = input("Enter your image source URL: ")
                # label = input("Enter your the detected label: ")
                lat = 42.388540
                long = -83.38822
                source = "Test"
                label = "Test"
                epochTime = int(time.time())
                foundImage = dashcam_img_table_manager.get_img(1618189103, '0110d98a-9951-4136-9782-44e4c8dfcfac')
                event_type = 'Construction'
                put_success = event_table_manager.put_new_event(epochTime, lat, long, event_type, foundImage)
            elif int(val) == 4:
                event_table_manager.scan_table()
            elif int(val) == 5:
                foundItem = event_table_manager.get_img(1616718877, '122e0e31-30d9-4563-b489-8a105ec846f0')
                print(foundItem)
            elif int(val) == 6:
                result = event_table_manager.update_img(1616718877, '122e0e31-30d9-4563-b489-8a105ec846f0',
                                                        lat=32.389459)  # detectedLabel='Sloth')
                print(result)
            elif int(val) == 7:
                response = event_table_manager.delete_img(1616718956, '189e363c-7a50-4ed1-ad9d-1bb96409733f')
                print(response)
            elif int(val) == 8:
                # top_left_lat = input("Enter the top left bounding box corner latitude value: ")
                # top_left_long = input("Enter the top left bounding box corner longitude value: ")
                # bottom_right_lat = input("Enter the bottom right bounding box corner latitude value: ")
                # bottom_right_long = input("Enter the bottom right bounding box corner longitude value: ")
                top_left_lat = 42.410831
                top_left_long = -83.413774
                bottom_right_lat = 42.396622
                bottom_right_long = -83.402775
                results = event_table_manager.get_imgs_in_GPS_bounds(top_left_lat, top_left_long, bottom_right_lat,
                                                                     bottom_right_long)

    except KeyboardInterrupt:
        print('interrupted!')
