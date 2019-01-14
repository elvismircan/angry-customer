import boto3.session
import logging
import logging.config

logging.config.fileConfig('logging.conf')
# create logger
logger = logging.getLogger('file')

def predict(imageFile):

    client=boto3.session.Session().client('rekognition')

    with open(imageFile, 'rb') as image:
        response = client.detect_labels(Image={'Bytes': image.read()})

    log_arr = list()
    log_arr.append(imageFile)

    ret_arr = list()
    for label in response['Labels']:
        ret_arr.append(label["Name"])
        log_arr.append(label["Name"] + ":" + str(label['Confidence']))

    logger.debug(log_arr)

    return ret_arr;

if __name__ == "__main__":
    print ("")