import csv
import uuid
import sys

# Increase CSV field size limit just in case
csv.field_size_limit(sys.maxsize)

INPUT_FILE = '/Volumes/data/dev/teabigdata/data/ok_data_level4.csv'
OUTPUT_FILE = 'dictionary_data.sql'

def generate_sql():
    # Store rows to process them
    rows = []
    # Map original CSV ID to new UUID
    id_map = {}
    # Map original CSV ID to Row Data (for looking up details if needed later)
    data_map = {}

    print(f"Reading {INPUT_FILE}...")
    
    try:
        with open(INPUT_FILE, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Clean up keys if there are BOM or spaces
                clean_row = {k.strip(): v for k, v in row.items() if k}
                rows.append(clean_row)
                
                # Generate new UUID for this item
                new_id = uuid.uuid4()
                original_id = clean_row['id']
                id_map[original_id] = new_id
                data_map[original_id] = clean_row

    except FileNotFoundError:
        print(f"Error: File {INPUT_FILE} not found.")
        return

    print(f"Read {len(rows)} rows. Generating SQL...")

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write("-- Dictionary data for administrative divisions\n")
        
        for row in rows:
            original_id = row['id']
            pid = row['pid']
            name = row['ext_name'] # Using ext_name for full display name
            value = row['id']
            
            # Basic fields
            new_uuid = id_map[original_id]
            code = 'administrative_division'
            
            # Resolve Parent ID
            parent_uuid_str = "NULL"
            if pid != '0' and pid in id_map:
                parent_uuid_str = f"'{id_map[pid]}'"
            
            # Handle quotes in name just in case
            safe_name = name.replace("'", "''")
            
            sql = (
                f"INSERT INTO DICTIONARY "
                f"(ID, CODE, NAME, VALUE, PARENT_ID, SORT_ORDER, ENABLED, CLAZZ) "
                f"VALUES "
                f"('{new_uuid}', '{code}', '{safe_name}', '{value}', {parent_uuid_str}, {value}, TRUE, NULL);\n"
            )
            f.write(sql)

    print(f"Done. Output written to {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_sql()
