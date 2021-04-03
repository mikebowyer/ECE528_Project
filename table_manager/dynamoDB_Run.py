import logging
import time
from dashcam_table_manager import DashcamTableManager

# logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(name)s %(levelname)s:%(message)s')
# logger = logging.getLogger(__name__)


if __name__ == '__main__':

    tableManager = DashcamTableManager("dashcam_images")

    try:
        while True:
            val = input(
                "Options: \n\t0) Check if table exists\n\t1) Delete table\n\t2) List tables\n\t3) Put new item\n\t4) Scan table\n\t5) get image\n\t6) update image\n\t7) delete image\n\t8) get_imgs_in_GPS_bounds")
            if int(val) == 0:
                tableManager.check_if_table_exists()
            elif int(val) == 1:
                tableManager.delete_table()
            elif int(val) == 2:
                tableManager.list_tables()
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
                human_readable_time = time.strftime("%Y-%m-%d %H:%M:%S",
                                                    time.gmtime(epochTime))
                detectedLabels = ['Cat', 'Car']
                put_success = tableManager.put_new_img(epochTime, lat, long, 'ImageURL', 'LabelledImageURL',
                                                       detectedLabels, human_readable_time)
            elif int(val) == 4:
                tableManager.scan_table()
            elif int(val) == 5:
                foundItem = tableManager.get_img(1616718877, '122e0e31-30d9-4563-b489-8a105ec846f0')
                print(foundItem)
            elif int(val) == 6:
                result = tableManager.update_img(1616718877, '122e0e31-30d9-4563-b489-8a105ec846f0',
                                                 lat=32.389459)  # detectedLabel='Sloth')
                print(result)
            elif int(val) == 7:
                response = tableManager.delete_img(1616718956, '189e363c-7a50-4ed1-ad9d-1bb96409733f')
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
                results = tableManager.get_imgs_in_GPS_bounds(top_left_lat, top_left_long, bottom_right_lat,
                                                              bottom_right_long)

    except KeyboardInterrupt:
        print('interrupted!')
