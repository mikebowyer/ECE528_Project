import logging
from dashcam_table_manager import DashcamTableManager

# logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(name)s %(levelname)s:%(message)s')
# logger = logging.getLogger(__name__)


if __name__ == '__main__':

    tableManager = DashcamTableManager("dashcam_images")

    try:
        while True:
            val = input("Enter your value: ")
            if int(val) == 0:
                tableManager.check_if_table_exists()
            elif int(val)==1:
                tableManager.delete_table()
            elif int(val)==2:
                tableManager.list_tables()
            elif int(val)==3:
                put_sucess = tableManager.put_new_img(42.389459,-83.386596,"http://imgSource.com", "caterpillar")
            elif int(val)==4:
                tableManager.scan_table()
            elif int(val)==5:
                foundItem = tableManager.get_img(1616718877, '122e0e31-30d9-4563-b489-8a105ec846f0')
                print(foundItem)
            elif int(val)==6:
                result = tableManager.update_img(1616718877, '122e0e31-30d9-4563-b489-8a105ec846f0', lat=32.389459)#detectedLabel='Sloth')
                print (result)
            elif int(val)==7:
                response = tableManager.delete_img(1616718956, '189e363c-7a50-4ed1-ad9d-1bb96409733f')
                print(response)



    except KeyboardInterrupt:
        print('interrupted!')
    # list_tables()


    # if not check_if_table_exists():
    #     table = create_dashcam_img_table()

    # #Put new Item
    # put_response = put_new_img(0,int(time.time()), 42.390949, -83.393720,"www.google.com")
    # logger.info("Put image response: ")
    # pprint(put_response, sort_dicts=False)
