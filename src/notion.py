from datetime import datetime
from typing import Union, List, Literal
from pprint import pprint

from notion_client import Client

import utils

COLORS = Literal['default', 'gray', 'brown', 'orange', 'yellow', 'green', 'blue', 'purple', 'pink', 'red']
NOTION_PAR_LIM = 2000  # max number of characters in a Notion paragraph block


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
    
    def create_block_paragraph(self, text_to_add: str, text_color: COLORS='default'):
        # Corrected content structure with rich_text field
        paragraph_block = {
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{
                    "type": "text",
                    "text": {
                        "content": text_to_add
                    },
                    "annotations": {
                        "color": text_color
                    }
                }]
            }
        }
        return paragraph_block
    
    def create_block_header(self, text_to_add: str, heading: Literal['#', '##', '###']='#', text_color: COLORS='default'):
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
                    },
                    "annotations": {
                        "color": text_color
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
    """
    Standalone function that appends a transcription to a Notion page, following a specific format.

    Parameters
    ----------
    token : str
        The Notion API token.
    database_id : str
        The ID of the database to append the transcription to.
    page_properties : str
        The properties of the page to append the transcription to.
    transcription : dict
        The transcription to append to the page.

    Returns
    -------
    response : dict
        The response from the Notion API for appending a block.
    """
    notion = Notion(token, database_id, page_properties)
    
    title = create_page_title()
    # does a page with the current week number already exist?
    page_id = get_page_from_database_by_title(notion, title)
    if page_id is False:
        page = notion.create_page_in_database(notion.DATABASE_ID, title)
        page_id = page['id']
    # append the transcription to the new page
    heading, text = get_transcription_heading(), transcription['text']
    print(heading, text)
    blocks = []
    header_block = notion.create_block_header(heading, heading='###')
    blocks.append(header_block)
    # create the paragraph block
    if len(text) > NOTION_PAR_LIM:
        for x in range(0, len(text), NOTION_PAR_LIM):
            block = notion.create_block_paragraph(text[x:x+NOTION_PAR_LIM])
            blocks.append(block)
    else:
        block = notion.create_block_paragraph(text)
        blocks.append(block)
    # append the blocks to the new page
    response = notion.add_blocks_to_page(page_id, blocks)
    return response


def get_page_from_database_by_title(notion:Notion, title:str):
    """
    Check if a page with the given title exists in the database and return the page ID.

    Parameters
    ----------
    notion : Notion
        The Notion object where to search.
    title : str
        The title of the page to search for.

    Returns
    -------
    Union[str, None]
        If the page exists, return the page ID, otherwise return False.
    """
    # get all pages from database
    pages = notion.get_pages_from_database(notion.DATABASE_ID)
    # iterate over pages and return the page ID if the title matches
    for page in pages:
        if page['name'] == title:
            return page['id']
    
    return False

def create_page_title():
    """ Return string with format
            'YYYY Week WW', e.g. '2024 Week 34'
    """
    return datetime.now().strftime("%Y Week %V")  # current week number YYYY-WW

def get_transcription_heading():
    """ Return a string in the form of 
            'Transcription from DD.MM.YYYY HH:MM Timezone', e.g. 'Transcription from 24.08.2021 15:30 CEST'
    """
    date_time = datetime.now().strftime("%d.%m.%Y %H:%M")  # DD.MM.YYYY HH:MM
    timezone = datetime.now().strftime("%Z")  # Timezone
    heading = f"Transcription from {date_time} {timezone}"
    return heading

        

if __name__ == "__main__":
    NOTION_TOKEN  = "secret_akufRDBcruwCW8E62hTVvrefbJtpEskd9hOdoDJZpAC"
    DATABASE_ID = "3d23e0e454e04767bb4d4b856b613e0c"
    PAGE_PROPERTIES = ["Title", "Description"]


    notion = Notion(NOTION_TOKEN, DATABASE_ID, PAGE_PROPERTIES)
    # new_page = notion.create_page_in_database(DATABASE_ID, "new new *new*")
    text = "Hallo Josh, ich freue mich über deine Nachricht. Voll schön, dass du mir schreibst. Erzähl auch mal, wie es dir geht und deine Pläne und Amy. Gibt es bei dir schon was Neues mit Job? Wie ist es da so? Und welchen Ort? Vielleicht gibt es da ja auch schon Neuigkeiten. Erzähl mal, es geht ja immer alles so schnell. Ja, ich vermisse euch. Ich habe auch an euch gedacht. Deine Mom hat mir ein Bild von dir geschickt, dass sie dich überrascht hat. Das ist voll süß. Deine Mom ist so cute. Und auch voll crazy, was sie da macht. Dass sie deine Oma so pflegt. Voll krass. Ich bin gerade mit dem Hund draußen, mit Romeo, dem Hund meines Bruders. Ich war da auf Bali einen Monat und bin dann komplett wieder Weihnachten. Ich bin zu meiner Oma nach Italien und habe sie und meine Cousine aus Italien zusammen mitgenommen. Wir sind zusammen nach Deutschland geflogen. Jetzt hier drei Wochen zusammen. Und jetzt fliegen die am Samstag wieder zurück nach Italien. Und ich habe noch gute zehn Tage hier in Uelzen. Dann fliege ich nach Bali am 22. Januar. Und dann erst mal ein One-Way-Ticket. Dann weiß ich nicht genau, wie lange. Aber ich rechne mal mit einem halben Jahr. Plus, minus. Je nachdem, ob ich mit dem Geld klar komme. Oder ob ich irgendwie keinen Bock mehr habe. Keine Ahnung. Aber wieder nach Bali. Und ja, eigentlich alles wieder gehabt. Ich gebe die Deutschstunden. Die Weihnachtstage waren ziemlich chillig. Da hatte ich tatsächlich auf natürliche Weise wenig Stunden. Weil die Leute halt einfach Urlaub genommen haben. Zeit mit der Familie. Haben ihr Abo pausiert. Das war auch gut für mich. Dann hatte ich mehr Zeit mit der Family. Jetzt habe ich wieder richtig viele Stunden. Teilweise acht Stunden am Tag. Was für mich sehr viel ist. Weil ich die auch vorbereite, nachbereite. Und ich 100% präsent sein muss in so einer Einheit. Ein bisschen anstrengend. Aber es geht irgendwie trotzdem. Weil ich ja einfach nur zu Hause bin. Dann gucke ich rum. Dass ich ein bisschen Sport mache. Und Yoga. Und mit der Family. Ja, aber manchmal schon irgendwie viel. Weil ich ja auch meine nächste Reise vorbereiten muss. Und dann immer so ein bisschen overwhelmed. Naja, aber mir geht es gut. Kleine Krisen zwischendurch. Weil ich meinen Eltern ja gesagt habe, dass ich Therapieausbildung mache. Und man sich ja teilweise schon vorher bewerben muss. Irgendwo sich einen Institutsplatz beschaffen muss. Und das kann ich einfach nicht. Weil ich einfach nicht weiß, wo ich wohnen will. Und keine Ahnung. Dann habe ich zwischendurch gedacht, ja vielleicht gehe ich nach München. Dann habe ich immerhin die Eisbachwelle dort vor Ort. Und kann da gratis surfen. Auf dieser Welle. Ist natürlich kein Surfen. Naja, und dann habe ich mir das irgendwie so vorgestellt. Und dachte, ja vielleicht bleib ich irgendwie ja doch dort. Und gehe nicht woanders hin. Und dann wäre es voll schön. Und ja, keine Ahnung. Dann habe ich mit meinem Dad geredet. Und ja, der hat irgendwie schon für mich ein Therapieinstitut rausgesucht. Tiefenpsychologie in Hannover. Und hat sich ausgemalt, dass ich hier in Uelzen lebe. Zu Hause. Und dann kann ich ihn ja schon in der Praxis unterstützen. Und dann war ich erstmal so ein bisschen geschockt. Und war so, äh ne, ich will systemische Familientherapie machen. Ich will nicht Tiefenpsychologie machen. Und er so, ja wieso denn nicht? Und dann war ich so, ja und hier wohnen will ich halt auch nicht. Und Hannover finde ich überhaupt nicht interessant. Und dann meinte er so, ja aber München ist viel zu teuer. Weil die Therapiebeausbildung ja auch Geld kostet. Und dann verdient man eigentlich so ein Praktikantengehalt. Vor allem in den Großstädten haben die so viel Nachfrage. Die Institute und die Kliniken. Dass sie sich es halt einfach erlauben können. Jemand der ja eigentlich fast Vollzeit arbeitet. Tausend Euro im Monat zu bezahlen. Therapieinstitut kostet ja so 300 Euro im Monat für drei Jahre. Wenn mindestens bei dem was ich machen will schon. Ja und dann war ich erst mal voll, ja keine Ahnung, voll in der Krise. Und dann hab ich gesagt so, kein Bock drauf. Ich geh"
    
    append_transcription(NOTION_TOKEN, DATABASE_ID, PAGE_PROPERTIES, {'text': text})

