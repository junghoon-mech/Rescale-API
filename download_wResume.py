########################################################################################################################
#   Author: junghoon@rescale.com                                                                                       #
#   Last updated: Sep 5, 2023                                                                                          #
#   Description: Download a file with resuming if it was terminated unexpectedly                                       #
########################################################################################################################

import os
import sys
import json
import requests


def read_apiconfig(path_home, path_apiconfig):

    try:
        f = open(path_apiconfig, "r", encoding="UTF8")
        lines = f.readlines()
        f.close()
    except FileNotFoundError as e:
        print(e)
        sys.exit(1)

    api_baseurl = lines[1].split('=')[1].rstrip('\n').lstrip().replace("'", "")
    api_key = lines[2].split('=')[1].rstrip('\n').lstrip().replace("'", "")
    api_token = 'Token ' + api_key
    api_fileurl = api_baseurl + '/api/v2/files/'

    return api_token, api_fileurl


def get_filename(api_token, url_download):

    info_file = requests.get(
        url_download,
        headers={'Authorization': api_token}
    )
    info_file_dict = json.loads(info_file.text)
    filename = info_file_dict['name']
    return filename


def download_file(api_token, url_download, filename):
    headers = {}

    try:
        # Get the file size if the file already exists
        file_size = int(open(filename, 'rb').readline().decode().split(' ')[-1])
        headers['Range'] = f'bytes={file_size}-'
    except (FileNotFoundError, ValueError):
        pass

    response = requests.get(url_download, headers=headers, stream=True)

    if response.status_code == 206:  # Partial content
        with open(filename, 'ab') as file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)
    elif response.status_code == 200:  # Full content (initial download)
        with open(filename, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)
    else:
        print(f"Download failed with status code: {response.status_code}")
        

def main():
    path_home = os.path.expanduser("~")
    path_apiconfig = path_home + os.sep + '.config' + os.sep + 'rescale' + os.sep + 'apiconfig'
    api_token, api_fileurl = read_apiconfig(path_home, path_apiconfig)
    print(api_fileurl)
#    id_file = str(sys.argv[1])
    id_file = 'ThUOrg'
    url_download = api_fileurl + id_file + '/'
    print(url_download)
    filename = get_filename(api_token, url_download)
    print(filename)
    download_file(api_token, url_download, filename)


if __name__ == '__main__':
    main()
