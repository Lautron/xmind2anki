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

def is_nested(children):
    flat_children = flatten(children)
    nested_count = [1 if key.count('children.attached') >= 1 else 0 
                for key in flat_children.keys()]
    #print(nested_count)
    average = sum(nested_count) / len(nested_count)
    return True if average > 0.5 else False

def format_data(clean_data):
    result = []
    for branch in clean_data: 
        title = branch.pop("title")
        children = branch["children"]["attached"]
        nested = is_nested(children)
        #pprint.pprint(flatten(children))
        #print(nested)
        #print()
        if nested:
            build_card = lambda value_list: [f"{title}: {value_list[0]}","<br>\n".join(value_list[1:])]
            card = [ build_card( list(flatten(sub_b).values()) ) for sub_b in children ]
            for res in card: result.append(res)
        else:
            build_card = lambda value_list: "<br>\n".join(value_list)
            card = [ build_card( list(flatten(sub_b).values()) ) for sub_b in children ]
            result.append([title, "<br>\n".join(card)])
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
