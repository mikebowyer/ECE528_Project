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
                "\n### Options: ###\n\t0) Check if table exists\n\t1) Delete table\n\t2) List tables\n\t3) Put new event\n\t4) Scan table\n\t5) Get Event\n\t6) Update Event\n\t7) Check if image should be associated with an event\n\t8) get_imgs_in_GPS_bounds\n")
            if int(val) == 0:  # Check if table exists
                event_table_manager.check_if_table_exists()
            elif int(val) == 1:  # Delete table
                event_table_manager.delete_table()
            elif int(val) == 2:  # List tables
                event_table_manager.list_tables()
            elif int(val) == 3:  # put new event
                # lat = input("Enter your latitude value: ")
                # long = input("Enter your longitude value: ")
                # source = input("Enter your image source URL: ")
                # label = input("Enter your the detected label: ")
                foundImage = dashcam_img_table_manager.get_img(1618442473, '296967a4-a2d3-47a7-9faf-3983800bc962')
                event_type = 'Construction'
                put_success = event_table_manager.put_new_event(event_type, foundImage)
            elif int(val) == 4:  # Scan table
                results = event_table_manager.scan_table()
                print(results)
            elif int(val) == 5:  # Get event
                foundItem = event_table_manager.get_event(1618264729, '67e326ed-3bed-4158-93cf-a6edd65a4b9c')
                print(foundItem)
            elif int(val) == 6:
                newImgToAssociate = dashcam_img_table_manager.get_img(1618267610,
                                                                      'ca6aab8a-aa22-4859-8bdc-0b31a0e51eed')
                result = event_table_manager.update_event_using_new_img(1618267621,
                                                                        '01cf0349-5cf3-4f78-b290-5bdbec36d869',
                                                                        new_image_to_associate=newImgToAssociate)
                print(result)
            elif int(val) == 7:
                imgToAssociate = dashcam_img_table_manager.get_img(1618444236,
                                                                      '2568612a-3cde-413e-aa43-f45be947d210')
                detected_label_associations = event_table_manager.check_if_img_matches_any_events(imgToAssociate)
                print("Events this image should be associated with: \n {}".format(detected_label_associations))

                if not detected_label_associations:
                    print("No events could be associated with this image, so creating new event.")
                    event_type = 'Construction'
                    put_success = event_table_manager.put_new_event(event_type, imgToAssociate)
                else:
                    print("At least one event found associated to this image, making associations.")
                    for detected_label_association in detected_label_associations:
                        for event_to_associate in detected_label_association:
                            event_time = event_to_associate['start_time']
                            event_uid = event_to_associate['event_uid']
                            result = event_table_manager.update_event_using_new_img(event_time,
                                                                                    event_uid,
                                                                                    new_image_to_associate=imgToAssociate)
                            if not result:
                                raise Exception("Sorry, had problems associating image to event")
            elif int(val) == 8:
                # top_left_lat = input("Enter the top left bounding box corner latitude value: ")
                # top_left_long = input("Enter the top left bounding box corner longitude value: ")
                # bottom_right_lat = input("Enter the bottom right bounding box corner latitude value: ")
                # bottom_right_long = input("Enter the bottom right bounding box corner longitude value: ")
                # bottom_right_long = input("Enter the bottom right bounding box corner longitude value: ")
                top_left_lat = 30
                top_left_long = -70
                bottom_right_lat = 50
                bottom_right_long = -80
                results = event_table_manager.get_events_in_GPS_bounds(top_left_lat, top_left_long, bottom_right_lat,
                                                                       bottom_right_long, 1200000, "Construction")
                print(results)

    except KeyboardInterrupt:
        print('interrupted!')
