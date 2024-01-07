""" This script handles all the Notion API calls."""
import requests
import random



class Notion:

    NOTION_TOKEN: str
    DATABASE_ID: str

    headers: dict
    
    def __init__(self, notion_token: str, database_id: str) -> None:
        self.NOTION_TOKEN = notion_token
        self.DATABASE_ID = database_id
        self.headers= {
            "Authorization": "Bearer " + self.NOTION_TOKEN,
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28",
        }
    
    
    def create_page(self, data: dict):
        create_url = "https://api.notion.com/v1/pages"

        payload = {"parent": {"database_id": self.DATABASE_ID}, "properties": data}

        res = requests.post(create_url, headers=self.headers, json=payload)
        # print(res.status_code)
        return res
    
    def get_pages(self, num_pages=None):
        """
        If num_pages is None, get all pages, otherwise just the defined number.
        """
        url = f"https://api.notion.com/v1/databases/{self.DATABASE_ID}/query"

        get_all = num_pages is None
        page_size = 100 if get_all else num_pages

        payload = {"page_size": page_size}
        response = requests.post(url, json=payload, headers=self.headers)

        data = response.json()

        # Comment this out to dump all data to a file
        # import json
        # with open('db.json', 'w', encoding='utf8') as f:
        #    json.dump(data, f, ensure_ascii=False, indent=4)

        results = data["results"]
        while data["has_more"] and get_all:
            payload = {"page_size": page_size, "start_cursor": data["next_cursor"]}
            url = f"https://api.notion.com/v1/databases/{self.DATABASE_ID}/query"
            response = requests.post(url, json=payload, headers=self.headers)
            data = response.json()
            results.extend(data["results"])

        return results
    
    
    def update_page(self, page_id: str, data: dict):
        url = f"https://api.notion.com/v1/pages/{page_id}"

        payload = {"properties": data}

        res = requests.patch(url, json=payload, headers=self.headers)
        return res
    
    def delete_page(self, page_id: str):
        url = f"https://api.notion.com/v1/pages/{page_id}"

        payload = {"archived": True}

        res = requests.patch(url, json=payload, headers=self.headers)
        return res
    
    
NOTION_TOKEN  = "secret_akufRDBcruwCW8E62hTVvrefbJtpEskd9hOdoDJZpAC"
DATABASE_ID = "3d23e0e454e04767bb4d4b856b613e0c"
notion  = Notion(NOTION_TOKEN, DATABASE_ID)

random_number = random.randint(0, 100)
title = "Test title xyz " + str(random_number)
data = {
    "Title": {"title": [{"text": {"content": title}}]},
    "Description": {"rich_text": [{"text": {"content": "Test description"}}]},
}

# result = notion.create_page(data)
result = notion.delete_page("a09cfcd3-34ac-4e83-994c-000bd7ecfe2d")

print(result.status_code)
if result.status_code != 200:
    print(result.json())
print(result.json())
    