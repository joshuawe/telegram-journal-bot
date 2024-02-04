import unittest
from datetime import datetime

import verbal_diary_bot as vdb
import verbal_diary_bot.database_operations as dbops


import utils_sys_path



USER1 = {'user_id': 999, 'name': 'test_name', 'notion_token': 'test_notion_token'}
USER2 = {'user_id': 998, 'name': 'test_name2', 'notion_token': 'test_notion_token2'}

MESSAGE1 = {'message': 'test message', 'word_count': 2, 'message_type': 'audio', 'audio_length': 23}
MESSAGE2 = {'message': 'Here we are talking many more words.', 'word_count': 32, 'message_type': 'audio', 'audio_length': 36}

class TestUserClass(unittest.TestCase):
    def setUp(self) -> None:
        dbops.delete_user(USER1['user_id'])
    
    def test_new_user(self):
        """Test creating a new user."""
        user = vdb.user.User(USER1['user_id'], USER1['name'], USER1['notion_token'])
        assert user.user_id == USER1['user_id']
        assert dbops.user_exists(USER1['user_id'])
    
        
    def test_add_message(self):
        """Test adding a message."""
        # delete user first
        dbops.delete_user(USER1['user_id'])
        
        date = datetime.now()
        date_str = date.strftime('%Y-%m-%d %H:%M:%S')
        user = vdb.user.User(USER1['user_id'])
        user.add_message(MESSAGE1['message'], MESSAGE1['word_count'], MESSAGE1['message_type'], MESSAGE1['audio_length'], date)
        
        # get message and check if date is correct
        message = dbops.get_messages_by_user(USER1['user_id'])[-1]
        assert message[1] == USER1['user_id']
        assert message[2] == date_str
        assert message[3] == MESSAGE1['message']
        assert message[4] == MESSAGE1['word_count']
        assert message[5] == MESSAGE1['message_type']
        assert message[6] == MESSAGE1['audio_length']
        
        # add further messages
        user.add_message(MESSAGE2['message'], MESSAGE2['word_count'], MESSAGE2['message_type'], MESSAGE2['audio_length'])
        
        # check length of all messages. Should be two
        assert len(user.get_messages()) == 2
        
        
        
    
        
    def tearDown(self) -> None:
        dbops.delete_user(USER1['user_id'])
        return super().tearDown()
    