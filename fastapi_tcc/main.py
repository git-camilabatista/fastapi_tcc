from fastapi import FastAPI

app = FastAPI()

dict_item = {
    'key1': 'item 1',
    'key2': 'item 2',
}

@app.get("/items/{item_id}")
async def show_item(item_id: str):
    return {'results': dict_item[item_id]}