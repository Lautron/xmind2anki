from json_flatten import flatten, unflatten
import json, zipfile, pprint, csv, sys

# get_latex --> clean_data = {key: value for key, value in flattened_data.items() if "content.content" in key}

def handle_input(args):
    args = args[1:]
    if not args:
        print("usage: xmind2anki.py [FILES]\nFile extension must be .xmind")
        sys.exit()

    if all([arg.endswith(".xmind") for arg in args]):
        return args

    else:
        print("Invalid arguments")
        sys.exit()

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

def is_nested(children):
    flat_children = flatten(children)
    nested_count = [1 if key.count('children.attached') >= 1 else 0 for key in flat_children.keys()]
    average = sum(nested_count) / len(nested_count)
    return True if average > 0.5 else False

def build_nested_cards(data, title):
    build_card = lambda value_list: [f"{title}: {value_list[0]}","<br>\n".join(value_list[1:])]
    return [ build_card( list(flatten(sub_b).values()) ) for sub_b in data ]

def build_flat_cards(data, title):
    build_card = lambda value_list: "<br>\n".join(value_list)
    card = "<br>\n".join([ build_card( list(flatten(sub_b).values()) ) for sub_b in data ])
    return [[title, card]]

def format_data(clean_data):
    result = []
    for branch in clean_data: 
        try:
            title = branch.pop("title")
        # if branch head only contains LaTeX there will be a keyError
        except KeyError:
            title = branch['extensions'][0]['content']['content']
        children = branch["children"]["attached"]
        nested = is_nested(children)
        cards = build_nested_cards(children, title) if nested else build_flat_cards(children,title)
        result.extend(cards)

    return result

def main():
    files = handle_input(sys.argv)
    data_list = [(filename, get_data(filename)) for filename in files]
    cleaned_data = [(filename, clean_data(data)) for filename, data in data_list]
    csv_contents = [(filename, format_data(data)) for filename, data in cleaned_data]
    #pprint.pprint(csv_contents)
    for filename, csv_data in csv_contents:
        csv_filename = filename.replace(".xmind", ".csv")
        write_csv(csv_filename, csv_data)
        print(f'Written output for {filename} to {csv_filename}')

if __name__ == "__main__":
    main()
