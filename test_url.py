import requests

urls = [
    'https://www.enr-scvotes.org/SC/Aiken/19079/index.html',
    'https://www.enr-scvotes.org/Aiken/19079/index.html',
    'https://www.enr-scvotes.org/SC/19077/Aiken/19079/en/summary.html',
    'https://www.enr-scvotes.org/SC/19077/Aiken/19079/index.html',
]

headers = {'User-Agent': 'Mozilla/5.0'}

for url in urls:
    try:
        r = requests.get(url, headers=headers, timeout=5)
        print(f'{url}: {r.status_code}')
        if r.status_code == 200:
            print(f'  ✅ FOUND! Length: {len(r.text)}')
            with open('workspace_files/enr_downloads/aiken_found.html', 'w', encoding='utf-8') as f:
                f.write(r.text)
            break
    except Exception as e:
        print(f'{url}: ERROR - {e}')
