from iotdb.Session import Session

IOTDB_IP = "172.16.32.226"
IOTDB_PORT = "6667"
IOTDB_USERNAME = "root"
IOTDB_PASSWORD = "root"



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