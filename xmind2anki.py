from json_flatten import flatten, unflatten
import json, zipfile, pprint, csv, sys

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
        tag = [filename.replace(".csv", "").replace(" ", "_")]
        csv_writer.writerows([row + tag for row in rows])

def get_data(filename):
    zip_file = zipfile.ZipFile(filename, 'r')
    raw_json = zip_file.read('content.json')
    content_data = json.loads(raw_json)[0]['rootTopic']['children']['attached']
    return content_data

def clean_data(data):
    flattened_data = flatten(data)
    is_relevant = lambda key: "title" in key or 'content.content' in key 
    format_dict = lambda key, value: '$'+ value.replace("\n","") +'$' if 'content.content' in key else value
    clean_data = { key: format_dict(key,value) for key, value in flattened_data.items() if value and is_relevant(key) }
    return unflatten(clean_data)

def is_nested(children):
    res = ["children" in child for child in children]
    return all(res)

def build_nested_card(sub_b, title):
    flat_data = flatten(sub_b)
    first_value = flat_data.pop(list(flat_data.keys())[0])
    unflat_data = unflatten(flat_data)
    print("  ", first_value)
    try:
        sub_branches = unflat_data['children']['attached']
    # If branch only has one node unflat_data will become empty and there will be a KeyError
    except KeyError: 
        raise Exception(f"Sub branch has only 1 value or is empty")

    subtitle = f"[latex]{first_value}[/latex]" if "$" in first_value else first_value
    sentences = [" ".join(flatten(sentence).values()) for sentence in sub_branches]
    return [f"{title}: {subtitle}","[latex]"+"<br>\n".join(sentences)+"[/latex]"]

def build_nested_cards(data, title):
    return [ build_nested_card(sub_b, title) for sub_b in data ]

def build_flat_cards(data, title):
    build_card = lambda value_list: "\n".join(value_list)
    card = "<br>\n".join([ build_card( list(flatten(sub_b).values()) ) for sub_b in data ])
    return [[title, f'[latex]{card}[/latex]']]

def format_data(clean_data):
    result = []
    for branch in clean_data: 
        try:
            title = branch.pop("title")
        except KeyError: # if branch head only contains LaTeX there will be a keyError
            title = branch['extensions'][0]['content']['content']
        children = branch['children']
        summary = children.get('summary', [])
        content = children["attached"] + summary
        print(title)
        nested = is_nested(content)
        cards = build_nested_cards(content, title) if nested else build_flat_cards(content, title)
        print("-"*100)
        result.extend(cards)

    return result

def main():
    files = handle_input(sys.argv)
    data_list = [(filename, get_data(filename)) for filename in files]
    cleaned_data = [(filename, clean_data(data)) for filename, data in data_list]
    csv_contents = [(filename, format_data(data)) for filename, data in cleaned_data]
    for filename, csv_data in csv_contents:
        csv_filename = filename.replace(".xmind", ".csv")
        write_csv(csv_filename, csv_data)
        print(f'Written output for {filename} to {csv_filename}')

if __name__ == "__main__":
    main()
