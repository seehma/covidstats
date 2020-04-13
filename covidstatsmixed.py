import json
import urllib.request
import datetime
import time
import filecmp
import os
import os.path
import glob
from urllib.error import HTTPError
from filelock import FileLock

# save date and time from timestamp as string (for filenames)
formatDateTime = "{:%Y-%m-%d_%H-%M-%S}".format(datetime.datetime.now())
formatTimestamp = "{}".format(time.time())
scriptPath = os.path.abspath(os.path.dirname(__file__))
print(formatDateTime + ": start script from path: " + scriptPath)


def download(url, filename, make_file=None):
    global formatDateTime, formatTimestamp, scriptPath

    try:
        samefile = False
        response = urllib.request.urlopen(url)
        final_filename = os.path.join(scriptPath, filename)
        temp_filename = os.path.join(scriptPath, 'temp_' + filename)
        prefix = "_".join(filename.split('_')[0:2])

        print(formatDateTime + ": created Temp File "+temp_filename)

        if make_file is not None:
            make_file(response, temp_filename)
        else:
            with open(temp_filename, 'wb') as f:
                f.write(response.read())

        # check if files are identical => if yes remove newly generated file, if no save it and save old filename
        files = list(filter(os.path.isfile, glob.glob(os.path.join(scriptPath, "*"))))
        files.sort(reverse=True, key=lambda x: os.path.getmtime(x))
        for file in files:
            if file.find(prefix) != -1 and file.find("temp_" + prefix) == -1:

                print("{}: filename website {}".format(formatDateTime, temp_filename))
                print("{}: ToBeChecked {}".format(formatDateTime, file))

                if filecmp.cmp(temp_filename, os.path.join(scriptPath, file), shallow=False):
                    os.remove(temp_filename)
                    samefile = True
                    print(formatDateTime + ": File with same content found! (" + file + ")")
                    break

        if not samefile:
            os.rename(temp_filename, final_filename)
            print(formatDateTime + ": new File: " + final_filename + " angelegt!")

    except HTTPError as ex:
        print(ex.read())


def make_file_json(response, filename):
    print(filename)
    str_response = response.read().decode('utf-8')
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(str_response, f, ensure_ascii=False, indent=4, sort_keys=True)
    f.close()


with FileLock(os.path.join(scriptPath, 'pid.lock'), timeout=2):

    download(url='https://www.sozialministerium.at/Informationen-zum-Coronavirus/Neuartiges-Coronavirus-(2019-nCov).html',
             filename='bmsgpk_website_' + formatDateTime + '_' + formatTimestamp + '.html')

    download(url='https://www.sozialministerium.at/Informationen-zum-Coronavirus/Dashboard/Zahlen-zur-Hospitalisierung',
             filename='bmsgpk_website2_' + formatDateTime + '_' + formatTimestamp + '.html')

    download(url='https://info.gesundheitsministerium.at/',
             filename='bmsgpk_dashboard_' + formatDateTime + '_' + formatTimestamp + '.html')

    download(url='https://info.gesundheitsministerium.at/data/austria_map.json',
             filename='bmsgpk_json_' + formatDateTime + '_' + formatTimestamp + '.json',
             make_file=make_file_json)

