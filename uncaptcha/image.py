import boto3.session
import logging
import logging.config

logging.config.fileConfig('logging.conf')
# create logger
logger = logging.getLogger('file')

def predict(imageFile, x, y):

    client=boto3.session.Session().client('rekognition')

    with open(imageFile, 'rb') as image:
        response = client.detect_labels(Image={'Bytes': image.read()})

    log_arr = list()
    log_arr.append((imageFile + " ({}, {})").format(x , y))

    ret_arr = list()
    for label in response['Labels']:
        log_arr.append(label["Name"] + ":" + str(label['Confidence']))
        if label['Confidence'] > 90:
            ret_arr.append(label["Name"])

    logger.debug(log_arr)

    return ret_arr;

if __name__ == "__main__":
    print ("")