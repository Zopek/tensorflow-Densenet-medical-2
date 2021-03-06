# -*- coding: UTF-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import sys
import numpy as np
import time

def get_num(filepath):

	train_size = 0
	test_size = 0
	# 训练集在3个文件夹中，每个文件夹中数据数几乎相同，总数目乘3可得
	dirs = os.listdir(filepath + '/' + str(1))
	train_size += len(dirs)

	# 测试集在1个文件夹中
	dirs = os.listdir(filepath + '/' + str(4))
	test_size += len(dirs)

	return train_size, test_size

# 多标签转换
def label_convert_mul(label):

	labels = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
	labels[int(label[0])] = 1
	labels[int(label[1]) + 4] = 1
	labels[int(label[2]) + 7] = 1
	labels[int(label[3]) + 11] = 1

	return labels.reshape((1, -1)) 

# 单一标签转换
def label_convert(label):

	labels = np.array([0, 0, 0, 0])
	labels[int(label[0])] = 1

	return labels.reshape((1, -1)) 

def train_next_batch(filepath, step, batch_size):

	train_size, test_size = get_num(filepath)
	current_num = step * batch_size

	# 训练集为1， 2， 3，故+1
	current_file = int(current_num / train_size) + 1
	next_file = int((current_num + batch_size) / train_size) + 1
	# print(current_file, ' ', next_file)
	# 如果当前文件夹剩余数据不足一个batch，则与下一个文件夹数据合并
	if current_file != next_file:
		# 获取当前文件夹下文件名列表
		dirs = os.listdir(filepath + '/' + str(current_file))
		current_file_num = current_num - train_size * (current_file - 1)
		# 取出当前文件夹剩余数据
		for filename in dirs[current_file_num:train_size]:
			# 取出图像
			image = np.load(filepath + '/' + str(current_file) + '/' + filename + '/lesion_voxel.npy')
			# 为了防止显存不够，每个病人最多只随机取一定数量照片
			if image.shape[0] >= 32 / batch_size:
				perm0 = np.arange(image.shape[0])
				np.random.shuffle(perm0)
				image = image[perm0[0:int(32/batch_size)],:,:]
			# image = image.reshape((1, -1))
			if filename == dirs[current_file_num]:
				images = image
				# 记录voxel维度
				voxel = [image.shape[0]]
			else:
				images = np.vstack((images, image))
				voxel.append(image.shape[0])
			# print('current file: ', filename)
			# print(images.shape)
			# 取出标签
			label = np.load(filepath + '/' + str(current_file) + '/' + filename + '/label.npy')
			label = label_convert(label)
			if filename == dirs[current_file_num]:
				labels = label
			else:
				labels = np.vstack((labels, label))

		# 进入下一文件夹
		dirs = os.listdir(filepath + '/' + str(next_file))
		# 下一文件夹需补充数据数
		rest_num = current_num + batch_size - train_size * current_file
		# print(images.shape)
		# 取出下一文件夹数据
		for filename in dirs[0:rest_num]:
			# print('last file: ', filepath, '/', str(next_file), '/', filename)
			# 取出图像
			image = np.load(filepath + '/' + str(next_file) + '/' + filename + '/lesion_voxel.npy')
			if image.shape[0] >= 32 / batch_size:
				perm0 = np.arange(image.shape[0])
				np.random.shuffle(perm0)
				image = image[perm0[0:int(32/batch_size)],:,:]
			# image = image.reshape((1, -1))
			images = np.vstack((images, image))
			voxel.append(image.shape[0])
			# 取出标签
			label = np.load(filepath + '/' + str(next_file) + '/' + filename + '/label.npy')
			label = label_convert(label)
			labels = np.vstack((labels, label))

		#if filename == dirs[rest_num - 1]:
		#	print('last file: ', filepath, '/', str(current_file), '/', filename)

		return images, voxel, labels
	else:
		dirs = os.listdir(filepath + '/' + str(current_file))
		current_file_num = current_num - train_size * (current_file - 1)
		for filename in dirs[current_file_num:(current_file_num + batch_size)]:
			# 取出图像
			image = np.load(filepath + '/' + str(current_file) + '/' + filename + '/lesion_voxel.npy')
			if image.shape[0] >= 32 / batch_size:
				perm0 = np.arange(image.shape[0])
				np.random.shuffle(perm0)
				image = image[perm0[0:int(32/batch_size)],:,:]
			# image = image.reshape((1, -1))
			if filename == dirs[current_file_num]:
				images = image
				# 记录voxel维度
				voxel = [image.shape[0]]
			else:
				images = np.vstack((images, image))
				voxel.append(image.shape[0])
			# 取出标签
			label = np.load(filepath + '/' + str(current_file) + '/' + filename + '/label.npy')
			label = label_convert(label)
			if filename == dirs[current_file_num]:
				labels = label
			else:
				labels = np.vstack((labels, label))

			#if filename == dirs[current_file_num + batch_size - 1]:
			#	print('last file: ', filepath, '/', str(current_file), '/', filename)

		return images, voxel, labels

def test_next_batch(filepath, step):

	# 300 one time
	current_num = step * 300
	dirs = os.listdir(filepath + '/' + str(4))
	for filename in dirs[current_num:(current_num + 300)]:
		# 取出图像
		image = np.load(filepath + '/' + str(4) + '/' + filename + '/lesion_voxel.npy')
		if image.shape[0] >= 32 / batch_size:
				perm0 = np.arange(image.shape[0])
				np.random.shuffle(perm0)
				image = image[perm0[0:int(32/batch_size)],:,:]
		# image = image.reshape((1, -1))
		if filename == dirs[current_num]:
			images = image
			# 记录voxel维度
			voxel = [image.shape[0]]
		else:
			images = np.vstack((images, image))
			voxel.append(image.shape[0])
		# 取出标签
		label = np.load(filepath + '/' + str(4) + '/' + filename + '/label.npy')
		label = label_convert(label)
		if filename == dirs[current_num]:
			labels = label
		else:
			labels = np.vstack((labels, label))

	return images, voxel, labels
	"""
	else:
		for filename in dirs[300:600]:
			# 取出图像
			image = np.load(filepath + '/' + str(4) + '/' + filename + '/image.npy')
			image = image.reshape((1, -1))
			if filename == dirs[300]:
				images = image
			else:
				images = np.vstack((images, image))
			# 取出标签
			label = np.load(filepath + '/' + str(4) + '/' + filename + '/label.npy')
			label = label_convert_mul(label)
			if filename == dirs[300]:
				labels = label
			else:
				labels = np.vstack((labels, label))

		return images, labels
	"""