from pprint import pprint

from notion_client import Client


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
        
    def create_page_in_database(self, database_id: str):
        
        # New page's properties and content
        new_page_properties = {
            "Title": {
                "title": [
                    {
                        "type": "text",
                        "text": {
                            "content": "Your page title"
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
        new_page = notion.client.pages.create(parent={"database_id": database_id}, properties=new_page_properties)
        
        return new_page
    
    def get_pages_from_database(self, database_id: str):
        # get all pages from database
        response = notion.client.databases.query(database_id=database_id)
        
        # extract page names and IDs
        page_title = self.PAGE_PROPERTIES[0]
        pages_info = []
        i = 0
        for page in response["results"]:
            i += 1
            page_id = page["id"]
            pprint(page["properties"][page_title]["title"])
            if page["properties"][page_title]["title"] == []:
                page_name = ""
            else:
                page_name = page["properties"][page_title]["title"][0]["text"]["content"]  # Adjust this based on your database's structure
            pages_info.append({"id": page_id, "name": page_name})

        # Print the page names and IDs
        for page in pages_info:
            print(f"Page ID: {page['id']}, Page Name: {page['name']}")
        return 


        

NOTION_TOKEN  = "secret_akufRDBcruwCW8E62hTVvrefbJtpEskd9hOdoDJZpAC"
DATABASE_ID = "3d23e0e454e04767bb4d4b856b613e0c"
PAGE_PROPERTIES = ["Title", "Description"]


notion = Notion(NOTION_TOKEN, DATABASE_ID, PAGE_PROPERTIES)
new_page = notion.get_pages_from_database(DATABASE_ID)

