import unittest
from datetime import datetime, timedelta

# import utils_sys_path
from verbal_diary_bot import database_operations as dbops


USER1 = {'user_id': 999, 'name': 'test_name', 'notion_token': 'test_notion_token'}
USER2 = {'user_id': 998, 'name': 'test_name2', 'notion_token': 'test_notion_token2'}

class TestDatabaseOperations(unittest.TestCase):
    def test_connect_db(self):
        conn = dbops.connect_db()
        assert conn is not None
        conn.close()
        
    def test_insert_delete_user(self):

        # insert the user
        dbops.insert_user(USER1['user_id'], USER1['name'], USER1['notion_token'])
        # check if user exists
        assert dbops.user_exists(USER1['user_id'])
        # check if user details are correct    
        user_data = dbops.get_user(USER1['user_id'])
        assert user_data[0] == USER1['user_id']
        assert user_data[1] == USER1['name']
        assert user_data[2] == USER1['notion_token']
        # update the user
        dbops.update_user(USER1['user_id'], USER2['name'], USER2['notion_token'])
        # check if user details are correct
        user_data = dbops.get_user(USER1['user_id'])
        assert user_data[0] == USER1['user_id']
        assert user_data[1] == USER2['name']
        assert user_data[2] == USER2['notion_token']
        # delete the user
        dbops.delete_user(USER1['user_id'])
        # check if user exists
        assert not dbops.user_exists(USER1['user_id'])
        
    def test_user_messages(self):
        # insert the users
        dbops.insert_user(USER1['user_id'], USER1['name'], USER1['notion_token'])
        dbops.insert_user(USER2['user_id'], USER2['name'], USER2['notion_token'])
        message_date = datetime.now()
        message_date2 = message_date + timedelta(minutes=2)
        # insert messages
        dbops.insert_message(USER1['user_id'], message_date, 'test_message', 10, 'audio', 0)
        dbops.insert_message(USER1['user_id'], message_date2, 'test_message2', 10, 'audio', 0)
        
        
        
        
        # delete the users
        dbops.delete_user(USER1['user_id'])
        dbops.delete_user(USER2['user_id'])
        # make sure it worked
        assert not dbops.user_exists(USER1['user_id'])
        assert not dbops.user_exists(USER2['user_id'])
        
    def tearDown(self) -> None:
        # check if any of the users exist
        if dbops.user_exists(USER1['user_id']):
            dbops.delete_user(USER1['user_id'])
        if dbops.user_exists(USER2['user_id']):
            dbops.delete_user(USER2['user_id'])
        # assure they do not exist
        assert not dbops.user_exists(USER1['user_id'])
        assert not dbops.user_exists(USER2['user_id'])
        return super().tearDown()
    