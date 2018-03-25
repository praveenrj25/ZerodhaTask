from bs4 import BeautifulSoup
import requests
import zipfile
import io
import redis
from . import constants


# returns iframe's url
def get_frame_source_url(frame):
    frame_elements = str(frame).split()
    frame_src = frame_elements[5].split('"')[1]
    return frame_src


# returns zip file url
def get_zip_file_url(attr_list):
    attributes = str(attr_list[0]).split()
    zip_url = attributes[2].split('"')[1]
    return zip_url


# function to connect redis database
def connect_redis_db():
    r = redis.StrictRedis(host=constants.REDIS_HOST, port=constants.REDIS_PORT,
                          password=constants.REDIS_PWD, charset=constants.REDIS_CHARSET, decode_responses=True)
    return r


# returns absolute file path to work on
def get_downloaded_file_path():
    page = requests.get(constants.BSE_URL)  # get page content from API
    soup = BeautifulSoup(page.content, constants.HTML_PARSER)

    '''The desired link is in iframe. 
    So find frame and get source url'''
    iframe = soup.find(constants.IFRAME)
    frame_page = requests.get(constants.URL_PREFIX + get_frame_source_url(iframe))
    soup = BeautifulSoup(frame_page.content, constants.HTML_PARSER)
    resultant_list = soup.select(constants.ZIP_FILE_LOCATOR_ID)

    # get zip file url
    zip_file_url = get_zip_file_url(resultant_list)
    # download zip file
    zip_file = requests.get(zip_file_url)
    # read zip contents
    z = zipfile.ZipFile(io.BytesIO(zip_file.content))
    # extracts it to a folder
    z.extractall(constants.RESOURCES)
    # returns absolute file path
    return str(constants.RESOURCES + '/' + z.namelist()[0])


# returns top 10 stock list
def get_top_10_list():
    equity_csv_file = get_downloaded_file_path()  # get file source

    conn = connect_redis_db()  # get redis connection

    ''' open csv file and read each lines.
    Store the split values in db with appropriate fields'''
    with open(equity_csv_file, 'r') as file:
        headers = next(file).split(',')  # split headers for hashes filed entries
        for line in file:
            values = line.split(',')
            mapping = {headers[0]: values[0].strip(), headers[1]: values[1].strip(), headers[2]: values[2].strip(),
                       headers[3]: values[3].strip(), headers[4]: float(values[4]), headers[5]: float(values[5]),
                       headers[6]: float(values[6]), headers[7]: float(values[7]), headers[8]: float(values[8]),
                       headers[9]: float(values[9]), headers[10]: int(values[10]), headers[11]: int(values[11]),
                       headers[12]: float(values[12])}
            conn.hmset(values[1].strip(), mapping)

    '''run redis command to get all hash values.
    Return top 10 list based on the diff between close price & open price'''
    db_values = []
    for hashes in conn.keys('*'):
        db_values.append(conn.hgetall(hashes))

    sorted_list = sorted(db_values, key=lambda k: (float(k[constants.CLOSE]) - float(k[constants.OPEN])), reverse=True)
    return sorted_list[:10]


# returns stock by name
def get_stock_by_name(name):
    conn = connect_redis_db()  # get redis connection
    return conn.hgetall(str(name).upper())
