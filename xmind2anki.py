from json_flatten import flatten, unflatten
import json, zipfile, pprint, csv

# get_latex --> clean_data = {key: value for key, value in flattened_data.items() if "content.content" in key}
def write_csv(filename, rows):
    with open(filename, 'w') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerows(rows)

def get_data(filename):
    zip_file = zipfile.ZipFile(filename, 'r')
    raw_json = zip_file.read('content.json')
    content_data = json.loads(raw_json)[0]['rootTopic']['children']['attached']
    return content_data

def clean_data(data):
    flattened_data = flatten(data)
    is_relevant = lambda key: "title" in key or 'content.content' in key
    format_dict = lambda key, value: f'\\({value}\\)' if 'content.content' in key else value
    clean_data = { key: format_dict(key,value) for key, value in flattened_data.items() if value and is_relevant(key) }
    return unflatten(clean_data)

def format_data(clean_data):
    result = []
    for branch in clean_data: 
        title = branch.pop("title")
        get_nodes = lambda sub_b: "<br>".join( flatten(sub_b).values() ).replace('\n', '').replace("<br>", '<br>\n')
        sub_branches = "<br>\n".join([ title + ': ' + get_nodes(sub_b) for sub_b in branch["children"]["attached"] ])
        result.append([title, sub_branches])
        #pprint.pprint(f'{title}: {sub_branches}')
    return result

def main():
    filename = "Algebra_clase1_17-Aug"
    data = get_data(filename + '.xmind')
    cleaned_data = clean_data(data)
    rows = format_data(cleaned_data)
    pprint.pprint(rows)
    write_csv(filename + '.csv', rows)


if __name__ == "__main__":
    main()
