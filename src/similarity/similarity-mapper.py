# import the necessary packages
from skimage.measure import structural_similarity as ssim
import numpy as np
import cv2
import sys

def encode_base64_image(image):
    ret,jpeg_encoded_image = cv2.imencode('.jpg',image)
    if ret:
        base64_image=base64.b64encode(jpeg_encoded_image)
        return image


def decode_base64_image(b64image):
    jpeg_image = b64image.decode('base64')
    jpeg_image_array = np.frombuffer(jpeg_image,np.uint8)
    image = cv2.imdecode(jpeg_image_array,1)
    #testing 
    #cv2.imshow("decoded",image)
    return image

def mse(imageA, imageB):
	# the 'Mean Squared Error' between the two images is the
	# sum of the squared difference between the two images;
	# NOTE: the two images must have the same dimension
	err = np.sum((imageA.astype("float") - imageB.astype("float")) ** 2)
	err /= float(imageA.shape[0] * imageA.shape[1])	
	# return the MSE, the lower the error, the more "similar"
	# the two images are
	return err
 
def compare_images(imageA, imageB):
	# compute the mean squared error and structural similarity
	# index for the images
	m = mse(imageA, imageB)
	s = ssim(imageA, imageB)
	return m,s

hash_list=[]
with open("similar_images.txt","r") as f:
	for line in f:
		hash_list.append(line.split("\t")[1])

for line in sys.stdin:
	data=line.split("\t")
	timestamp=data[0]
	img=data[1]
	imageA=decode_base64_image(img)
	for ref in hash_list:
		imageB=decode_base64_image(ref)
		original = cv2.cvtColor(imageA, cv2.COLOR_BGR2GRAY)
		reference = cv2.cvtColor(imageB, cv2.COLOR_BGR2GRAY)
		me,sim = compare_images(original,reference)
		print timestamp+"\t"+str(sim)+"\t"+img  
