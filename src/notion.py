from datetime import datetime
from typing import Union, List, Literal
from pprint import pprint

from notion_client import Client

import utils


class Notion:
    NOTION_TOKEN: str
    DATABASE_ID: str
    PAGE_PROPERTIES: list
    client: Client
    
    def __init__(self, NOTION_TOKEN: str, DATABASE_ID: str, PAGE_PROPERTIES: list) -> None:
        self.NOTION_TOKEN = NOTION_TOKEN
        self.DATABASE_ID = DATABASE_ID
        self.PAGE_PROPERTIES = PAGE_PROPERTIES
        self.client = Client(auth=NOTION_TOKEN)
        
    def create_page_in_database(self, database_id: str, title: str):
        
        # New page's properties and content
        new_page_properties = {
            "Title": {
                "title": [
                    {
                        "type": "text",
                        "text": {
                            "content": title
                        }
                    }
                ]
            },
            "Description": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": "Your page description"
                        }
                    }
                ]
            }
            # Add other properties as needed
        }

        # create new page
        new_page = self.client.pages.create(parent={"database_id": database_id}, properties=new_page_properties)
        
        return new_page
    
    def get_pages_from_database(self, database_id: str):
        """
        Get all pages from a given database and return the existing page IDs and page names.

        Parameters
        ----------
        database_id : str
            The ID of the database to get pages from.

        Returns
        -------
        list[dict]
            A list of dictionaries containing the page ID and page name. (keys: "id", "name")
        """
        # get all pages from database
        response = self.client.databases.query(database_id=database_id)
        
        # extract page names and IDs
        page_title = self.PAGE_PROPERTIES[0]
        pages_info = []
        for page in response["results"]:
            page_id = page["id"]
            if page["properties"][page_title]["title"] == []:
                page_name = ""
            else:
                page_name = page["properties"][page_title]["title"][0]["text"]["content"]  # Adjust this based on your database's structure
            pages_info.append({"id": page_id, "name": page_name})
                
        return pages_info
    
    def create_block_paragraph(self, text_to_add: str):
        # Corrected content structure with rich_text field
        paragraph_block = {
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{
                    "type": "text",
                    "text": {
                        "content": text_to_add
                    }
                }]
            }
        }
        return paragraph_block
    
    def create_block_header(self, text_to_add: str, heading: Literal['#', '##', '###']='#'):
        # get the correct heading type
        mapped_headings = dict(zip(['#', '##', '###'], ['heading_1', 'heading_2', 'heading_3']))
        heading = mapped_headings[heading]
        # Create the block with the correct heading
        heading_block = {
            "object": "block",
            "type": heading,
            heading: {
                "rich_text": [{
                    "type": "text",
                    "text": {
                        "content": text_to_add
                    }
                }]
            }
        }
        return heading_block
    
    def add_blocks_to_page(self, page_id: str, blocks: Union[List[dict],dict]):
        # blocks must always be a list of dicts
        if isinstance(blocks, dict):
            blocks = [blocks]
        response = self.client.blocks.children.append(block_id=page_id, children=blocks)
        return response
    
    def create_transcription_block(self, header:str, text:str):
        # create the header block
        header_block = self.create_block_header(header, heading='###')
        # create the paragraph block
        paragraph_block = self.create_block_paragraph(text)
        # append the two blocks
        blocks = [header_block, paragraph_block]
        return blocks


def append_transcription(token: str, database_id: str, page_properties: str, transcription: dict):
    notion = Notion(token, database_id, page_properties)
    
    # create new page
    # current week number in the form of YYYY-WW
    week_number = datetime.now().strftime("%Y Week %V")
    date_time = datetime.now().strftime("%d.%m.%Y %H:%M")  # DD.MM.YYYY HH:MM
    timezone = datetime.now().strftime("%Z")  # Timezone
    new_page = notion.create_page_in_database(notion.DATABASE_ID, week_number)
    new_page_id = new_page['id']
    # append the transcription to the new page
    heading = f"Transcription from {date_time} {timezone} - {utils.get_speech2text_model_name()}"
    text = transcription['text']
    block = notion.create_transcription_block(heading, text)
    # append the block to the new page
    response = notion.add_blocks_to_page(new_page_id, block)
    return response

        

if __name__ == "__main__":
    NOTION_TOKEN  = "secret_akufRDBcruwCW8E62hTVvrefbJtpEskd9hOdoDJZpAC"
    DATABASE_ID = "3d23e0e454e04767bb4d4b856b613e0c"
    PAGE_PROPERTIES = ["Title", "Description"]


    notion = Notion(NOTION_TOKEN, DATABASE_ID, PAGE_PROPERTIES)
    # new_page = notion.create_page_in_database(DATABASE_ID, "new new *new*")
    
    append_transcription(NOTION_TOKEN, DATABASE_ID, PAGE_PROPERTIES, {'text': 'test text'})

