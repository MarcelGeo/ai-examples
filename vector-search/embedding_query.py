import os
from dotenv import load_dotenv

load_dotenv()

FROM_TABLE = os.getenv("FROM_TABLE")

QUERY = f"""SELECT fid, id, version, postcode, street, number, json_extract("json(address_levels)", '$[0].value') as region, json_extract("json(address_levels)", '$[0].value') as county FROM "{FROM_TABLE}" LIMIT 10"""
