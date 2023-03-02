from iotdb.Session import Session

from config import envconfig

IOTDB_IP = envconfig.Settings().iotdb_ip
IOTDB_PORT = envconfig.Settings().iotdb_port
IOTDB_USERNAME = envconfig.Settings().iotdb_username
IOTDB_PASSWORD = envconfig.Settings().iotdb_password



def get_iotdb():
    """
    Function to generate db session
    :return: Session
    """
    session = Session(IOTDB_IP, IOTDB_PORT, IOTDB_USERNAME, IOTDB_PASSWORD)
    session.open(False)
    try:
        db = session
        return db
    except:
        print("释放资源iotdb")
        db.close()