import boto3

def predict(imageFile, classifier):

    client=boto3.Session().client('rekognition')

    with open(imageFile, 'rb') as image:
        response = client.detect_labels(Image={'Bytes': image.read()})

    print('Detected labels in ' + imageFile)

    ret_arr = list()
    for label in response['Labels']:
        ret_arr.append(label["Name"])
        print (label['Name'] + ' : ' + str(label['Confidence']))

    print('Done image classification\n')

    return ret_arr;

if __name__ == "__main__":
    print ("")