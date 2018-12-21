import boto3.session
import logging

def predict(imageFile):

    client=boto3.session.Session().client('rekognition')

    with open(imageFile, 'rb') as image:
        response = client.detect_labels(Image={'Bytes': image.read()})

    logging.debug('Detected labels in ' + imageFile)

    ret_arr = list()
    for label in response['Labels']:
        ret_arr.append(label["Name"])
        logging.debug(label['Name'] + ' : ' + str(label['Confidence']))

    logging.debug('Done image classification\n')

    return ret_arr;

if __name__ == "__main__":
    print ("")