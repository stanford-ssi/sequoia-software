from app import App
from random import randint

data_cache_schem = {
        "type": "object",
        "properties": {
            "current_value": {
                "type": "number"
            }
        },
        "required": ["current_value"]
    }

message_schema = {
        "type": "object",
        "properties": {
            "new_value": {
                "type": "number"
            }
        },
        "required": ["new_value"]
    }

app = App("test", data_cache_schem)

@app.startup
async def startup(_, redis, cache):
    print(f"Starting value is {cache['current_value']}")
    return None, None

@app.subscribe("new_values", message_schema)
async def receive_new_value(msg, redis, cache):
    print(f"Old current value: {cache['current_value']}")
    cache["current_value"] = msg["new_value"]
    print(f"New current value: {cache['current_value']}")
    return None, None

@app.interval(3)
async def send_new_value(_, redis, cache):
    new_value = randint(0, 1000)
    print(f"Sending new value: {new_value}")
    return "new_values", {
        "new_value": new_value
    }

if __name__ == "__main__":
    app.run({"current_value": 99})




