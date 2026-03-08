
import json
import os
import glob

DIR = 'src/assets/riverbasin'

def convert():
    files = glob.glob(os.path.join(DIR, '*.js'))
    
    for js_file in files:
        try:
            with open(js_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                
            # Naive stripping of "export default " and ";"
            if content.startswith('export default'):
                content = content.replace('export default', '', 1).strip()
            
            if content.endswith(';'):
                content = content[:-1]
                
            # Verify JSON
            data = json.loads(content)
            
            # Save as .json
            base = os.path.basename(js_file).replace('.js', '') # e.g. als.geojson
            if not base.endswith('.json') and not base.endswith('.geojson'):
                 # if filename is als.geojson.js -> als.geojson
                 pass 
            
            # The file names are like als.geojson.js -> target als.geojson
            target_name = base
            
            target_path = os.path.join(DIR, target_name)
            
            with open(target_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False)
                
            print(f"Converted {js_file} -> {target_path}")
            
        except Exception as e:
            print(f"Failed to convert {js_file}: {e}")

if __name__ == '__main__':
    convert()
