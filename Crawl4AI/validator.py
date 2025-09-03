import jsonschema
import json
import hashlib

with open("schemas/output_schema.json", 'r') as f:
    SCHEMA = json.load(f)

def validate_schema(data):
    try:
        jsonschema.validate(instance=data, schema=SCHEMA)
        return True
    except jsonschema.ValidationError as e:
        print(f"Schema validation error: {e}")
        return False

def post_process_data(text, min_length):
    return len(text.strip()) < min_length

def check_for_duplicates(data):
    seen_hashes = set()
    duplicates = set()
    for item in data:
        if 'clean_text' in item:
            text_hash = hashlib.sha256(item['clean_text'].encode('utf-8')).hexdigest()
            if text_hash in seen_hashes:
                duplicates.add(item['url'])
            else:
                seen_hashes.add(text_hash)
    return list(duplicates)