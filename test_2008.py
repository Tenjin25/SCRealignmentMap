from bs4 import BeautifulSoup

soup = BeautifulSoup(open('workspace_files/enr_downloads/2008_senate_select_county.html', encoding='utf-8').read(), 'html.parser')
aiken = soup.find('a', id='Aiken')
print(f'Aiken 2008 path: {aiken["value"]}')

# Now try to get the JSON
import requests
# Path is /Aiken/19079/index.html
# Need to follow redirects
base = 'https://www.enr-scvotes.org/SC/Aiken/19079'
r = requests.get(f'{base}/index.html', headers={'User-Agent': 'Mozilla/5.0'})
print(f'Redirect content: {r.text}')

# Extract the actual path from redirect
import re
match = re.search(r'URL=\./(\d+)/en/summary\.html', r.text)
if match:
    contest_id = match.group(1)
    print(f'Contest ID: {contest_id}')
    
    # Now get the JSON
    json_url = f'{base}/{contest_id}/json/sum.json'
    print(f'JSON URL: {json_url}')
    
    r2 = requests.get(json_url, headers={'User-Agent': 'Mozilla/5.0'})
    if r2.status_code == 200:
        print('✅ Got JSON!')
        import json
        data = r2.json()
        with open('workspace_files/enr_downloads/aiken_2008.json', 'w') as f:
            json.dump(data, f, indent=2)
        print(f'Saved to aiken_2008.json')
        
        # Show first contest
        if data.get('Contests'):
            print(f'\nFirst contest: {data["Contests"][0]["C"]}')
    else:
        print(f'❌ Failed: {r2.status_code}')
