import json
import os
import argparse
import datetime

def parse_json(json_file):
    with open(json_file, 'r') as f:
        data = json.load(f)
    return data

def list_contents(data, show_hidden=False):
    L1 = []
    contents = data.get('contents', [])
    for item in contents:
        if show_hidden or not item['name'].startswith('.'):
            # print(item['name'])
            L1.append(item['name'])
    print(" ".join(L1))

def pyls(json_file, show_hidden=False):
    data = parse_json(json_file)
    list_contents(data, show_hidden)

def format_permissions(permissions):
    # Mapping of permission bits to symbols
    perm_map = {
        '0': '---',
        '1': '--x',
        '2': '-w-',
        '3': '-wx',
        '4': 'r--',
        '5': 'r-x',
        '6': 'rw-',
        '7': 'rwx'
    }
    # Get permission for each group (owner, group, others)
    perms = [perm_map[p] for p in permissions]
    return ''.join(perms)

def format_time(timestamp):
    # Convert timestamp to datetime object
    dt_object = datetime.datetime.fromtimestamp(timestamp)
    # Format datetime object
    return dt_object.strftime("%b %d %H:%M")

def pyls_l(json_file):
    data = parse_json(json_file)
    list_contents_l(data)

def pyls_l_r(json_file, reverse=False):
    data = parse_json(json_file)
    list_contents_l(data, reverse)

def find_path_contents(data, path):
    path_parts = path.split('/')
    curr_data = data
    for part in path_parts:
        found = False
        for item in curr_data.get('contents', []):
            if item['name'] == part:
                curr_data = item
                found = True
                break
        if not found:
            return None
    return curr_data

def list_contents_l(data, reverse=False,filter_option=None):
    contents = data.get('contents', [])
    # Sort contents by time_modified
    sorted_contents = sorted(contents, key=lambda x: x['time_modified'], reverse=reverse)
    
    if filter_option == 'file':
        sorted_contents = [item for item in sorted_contents if not item.get('contents')]
    elif filter_option == 'dir':
        sorted_contents = [item for item in sorted_contents if item.get('contents')]
    else:
        pass

    for item in sorted_contents:
        permissions = item['permissions']
        size = item['size']
        time_modified = item['time_modified']
        name = item['name']
        formatted_time = format_time(time_modified)
        print(f"{permissions} {size} {formatted_time} {name}")
    
def pyls_l_r_t(json_file, reverse=False):
    data = parse_json(json_file)
    list_contents_l(data, reverse)

def pyls_l_r_t_filter(json_file, reverse=False, filter_option=None):
    data = parse_json(json_file)
    list_contents_l(data, reverse, filter_option)

def pyls_l_r_t_filter_path(json_file, reverse=False, filter_option=None, path=None):
    data = parse_json(json_file)
    
    if path:
        path_data = find_path_contents(data, path)
        if path_data is None:
            print(f"error: cannot access '{path}': No such file or directory")
            return
        if path_data.get('contents'):
            list_contents_l(path_data['contents'], reverse, filter_option)
        else:
            permissions = path_data['permissions']
            size = path_data['size']
            time_modified = path_data['time_modified']
            name = path_data['name']
            formatted_time = format_time(time_modified)
            print(f"{permissions} {size} {formatted_time} ./{path}")

    else:
        list_contents_l(data.get('contents', []), reverse, filter_option)

def pyls_help():
    parser = argparse.ArgumentParser(description="Python ls utility")
    parser.add_argument("json_file", type=str, help="Path to the JSON file")
    parser.add_argument("-l", "--long", action="store_true", help="Print additional information")
    parser.add_argument("-r", "--reverse", action="store_true", help="Print results in reverse")
    parser.add_argument("-t", "--time-sort", action="store_true", help="Sort results by time_modified")
    parser.add_argument("--filter", choices=['file', 'dir'], help="Filter results by 'file' or 'dir'")
    parser.add_argument("path", nargs='?', default=None, help="Optional path to directory or file")
    parser.print_help()

def main():
    parser = argparse.ArgumentParser(description="Python ls utility")
    parser.add_argument("json_file", type=str, help="structure.json")

    parser.add_argument("-A", "--all", action="store_true", help="Do not ignore entries starting with '.'")
    parser.add_argument("-l", "--long", action="store_true", help="Print additional information")
    parser.add_argument("-r", "--reverse", action="store_true", help="Print results in reverse")
    parser.add_argument("-t", "--time-sort", action="store_true", help="Sort results by time_modified")
    parser.add_argument("--filter", type=str, help="Filter results by 'file' or 'dir'")
    parser.add_argument("path", nargs='?', default=None, help="Optional path to directory or file")

    args = parser.parse_args()

    if args.long == True and args.reverse == True and args.time_sort == True and args.filter == 'dir':
        pyls_l_r_t_filter(args.json_file, args.reverse, args.filter)
    elif args.long == True and args.reverse == True and args.time_sort == True and args.filter == 'file':
        pyls_l_r_t_filter(args.json_file, args.reverse, args.filter)
    elif args.long == True and args.reverse == True and args.time_sort == True and args.filter == None:
        pyls_l_r_t(args.json_file, args.reverse)
    elif args.long == True and args.reverse == True and args.time_sort == False:        
        pyls_l_r(args.json_file, args.reverse)
    elif args.long == True and args.reverse == False and args.time_sort == False:
        pyls_l(args.json_file)  
    elif args.long == False and args.reverse == False and args.time_sort == False:
        pyls(args.json_file, args.all)
    else:
        pyls_help()

if __name__ == "__main__":
    main()