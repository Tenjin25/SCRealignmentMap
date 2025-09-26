import json

def list_contest_options(index_path):
    with open(index_path, 'r', encoding='utf-8') as f:
        index = json.load(f)
    print('--- County Contest Dropdown Options ---')
    for year in index['county']['years']:
        contests = index['county']['contests_by_year'].get(year, [])
        if contests:
            print(f'Year {year}:')
            for contest in contests:
                print(f"  - {contest['name']} (id: {contest['id']}, file: {contest['file']})")
        else:
            print(f'Year {year}: No contests found')

if __name__ == '__main__':
    list_contest_options('sc_results_index.json')
