# MIT License
# 
# Copyright (c) 2016 David Sandberg
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import unittest
import tempfile
import numpy as np
import cv2
import os
import shutil
import train_tripletloss
import train_softmax
import validate_on_lfw
import compare
import download_and_extract_model
import freeze_graph

def memory_usage_psutil():
    # return the memory usage in MB
    import psutil
    process = psutil.Process(os.getpid())
    mem = process.memory_info()[0] / float(2 ** 20)
    return mem

class TrainTest(unittest.TestCase):
  
    @classmethod
    def setUpClass(self):
        print('setUpClass')
        self.tmp_dir = tempfile.mkdtemp()
        self.dataset_dir = os.path.join(self.tmp_dir, 'dataset')
        create_mock_dataset(self.dataset_dir, 160)
        self.lfw_pairs_file = create_mock_lfw_pairs(self.tmp_dir)
        print(self.lfw_pairs_file)
        self.pretrained_model_name = '20170512-110547'
        download_and_extract_model.download_and_extract_model(self.pretrained_model_name, 'data/')
        self.model_file = os.path.join('data', self.pretrained_model_name, 'model-%s.ckpt-250000' % self.pretrained_model_name)
        self.pretrained_model = os.path.join('data', self.pretrained_model_name)
        self.frozen_graph_filename = os.path.join('data', self.pretrained_model_name+'.pb')
        print('Memory utilization (SetUpClass): %.3f MB' % memory_usage_psutil())

        
    @classmethod
    def tearDownClass(self):
        print('tearDownClass')
        # Recursively remove the temporary directory
        shutil.rmtree(self.tmp_dir)
        
    def tearDown(self):
        print('tearDown')
        print('Memory utilization (TearDown): %.3f MB' % memory_usage_psutil())

    # test_align_dataset_mtcnn
    # http://vis-www.cs.umass.edu/lfw/lfw-a.zip
    
    def test_training_classifier_inception_resnet_v1(self):
        print('test_training_classifier_inception_resnet_v1')
        argv = ['--logs_base_dir', self.tmp_dir,
                '--models_base_dir', self.tmp_dir,
                '--data_dir', self.dataset_dir,
                '--model_def', 'models.inception_resnet_v1',
                '--epoch_size', '1',
                '--max_nrof_epochs', '1',
                '--batch_size', '1',
                '--lfw_pairs', self.lfw_pairs_file,
                '--lfw_dir', self.dataset_dir,
                '--lfw_nrof_folds', '2',
                '--lfw_batch_size', '1',
                '--nrof_preprocess_threads', '1' ]
        args = train_softmax.parse_arguments(argv)
        train_softmax.main(args)

    def test_training_classifier_inception_resnet_v2(self):
        print('test_training_classifier_inception_resnet_v2')
        argv = ['--logs_base_dir', self.tmp_dir,
                '--models_base_dir', self.tmp_dir,
                '--data_dir', self.dataset_dir,
                '--model_def', 'models.inception_resnet_v2',
                '--epoch_size', '1',
                '--max_nrof_epochs', '1',
                '--batch_size', '1',
                '--lfw_pairs', self.lfw_pairs_file,
                '--lfw_dir', self.dataset_dir,
                '--lfw_nrof_folds', '2',
                '--lfw_batch_size', '1' ]
        args = train_softmax.parse_arguments(argv)
        train_softmax.main(args)
 
    def test_training_classifier_squeezenet(self):
        print('test_training_classifier_squeezenet')
        argv = ['--logs_base_dir', self.tmp_dir,
                '--models_base_dir', self.tmp_dir,
                '--data_dir', self.dataset_dir,
                '--model_def', 'models.squeezenet',
                '--epoch_size', '1',
                '--max_nrof_epochs', '1',
                '--batch_size', '1',
                '--lfw_pairs', self.lfw_pairs_file,
                '--lfw_dir', self.dataset_dir,
                '--lfw_nrof_folds', '2',
                '--lfw_batch_size', '1',
                '--nrof_preprocess_threads', '1' ]
        args = train_softmax.parse_arguments(argv)
        train_softmax.main(args)

    def test_train_tripletloss_inception_resnet_v1(self):
        print('test_train_tripletloss_inception_resnet_v1')
        argv = ['--logs_base_dir', self.tmp_dir,
                '--models_base_dir', self.tmp_dir,
                '--data_dir', self.dataset_dir,
                '--model_def', 'models.inception_resnet_v1',
                '--epoch_size', '1',
                '--max_nrof_epochs', '1',
                '--batch_size', '6',
                '--people_per_batch', '2',
                '--images_per_person', '3',
                '--lfw_pairs', self.lfw_pairs_file,
                '--lfw_dir', self.dataset_dir,
                '--lfw_nrof_folds', '2' ]
        args = train_tripletloss.parse_arguments(argv)
        train_tripletloss.main(args)
 
    def test_finetune_tripletloss_inception_resnet_v1(self):
        print('test_finetune_tripletloss_inception_resnet_v1')
        argv = ['--logs_base_dir', self.tmp_dir,
                '--models_base_dir', self.tmp_dir,
                '--data_dir', self.dataset_dir,
                '--model_def', 'models.inception_resnet_v1',
                '--pretrained_model', self.model_file,
                '--epoch_size', '1',
                '--max_nrof_epochs', '1',
                '--batch_size', '6',
                '--people_per_batch', '2',
                '--images_per_person', '3',
                '--lfw_pairs', self.lfw_pairs_file,
                '--lfw_dir', self.dataset_dir,
                '--lfw_nrof_folds', '2' ]
        args = train_tripletloss.parse_arguments(argv)
        train_tripletloss.main(args)
 
    def test_compare(self):
        print('test_compare')
        argv = [os.path.join('data/', self.pretrained_model_name),
                'data/images/Anthony_Hopkins_0001.jpg',
                'data/images/Anthony_Hopkins_0002.jpg' ]
        args = compare.parse_arguments(argv)
        compare.main(args)
        
    def test_validate_on_lfw(self):
        print('test_validate_on_lfw')
        argv = [self.dataset_dir,
                self.pretrained_model,
                '--lfw_pairs', self.lfw_pairs_file,
                '--lfw_nrof_folds', '2',
                '--lfw_batch_size', '6']
        args = validate_on_lfw.parse_arguments(argv)
        validate_on_lfw.main(args)

    def test_validate_on_lfw_frozen_graph(self):
        print('test_validate_on_lfw_frozen_graph')
        self.pretrained_model = os.path.join('data', self.pretrained_model_name)
        frozen_model = os.path.join(self.pretrained_model, self.pretrained_model_name+'.pb')
        argv = [self.dataset_dir,
                frozen_model,
                '--lfw_pairs', self.lfw_pairs_file,
                '--lfw_nrof_folds', '2',
                '--lfw_batch_size', '6']
        args = validate_on_lfw.parse_arguments(argv)
        validate_on_lfw.main(args)

    @unittest.skip("This test case results in a memory leak")
    def test_freeze_graph(self):
        print('test_freeze_graph')
        argv = [ self.pretrained_model,
                 self.frozen_graph_filename ]
        args = freeze_graph.parse_arguments(argv)
        freeze_graph.main(args)

# Create a mock dataset with random pixel images
def create_mock_dataset(dataset_dir, image_size):
   
    nrof_persons = 3
    nrof_images_per_person = 2
    np.random.seed(seed=666)
    os.mkdir(dataset_dir)
    for i in range(nrof_persons):
        class_name = '%04d' % (i+1)
        class_dir = os.path.join(dataset_dir, class_name)
        os.mkdir(class_dir)
        for j in range(nrof_images_per_person):
            img_name = '%04d' % (j+1)
            img_path = os.path.join(class_dir, class_name+'_'+img_name + '.png')
            img = np.random.uniform(low=0.0, high=255.0, size=(image_size,image_size,3))
            cv2.imwrite(img_path, img) #@UndefinedVariable

# Create a mock LFW pairs file
def create_mock_lfw_pairs(tmp_dir):
    pairs_filename = os.path.join(tmp_dir, 'pairs_mock.txt')
    with open(pairs_filename, 'w') as f:
        f.write('10 300\n')
        f.write('0001 1 2\n')
        f.write('0001 1 0002 1\n')
        f.write('0002 1 0003 1\n')
        f.write('0001 1 0003 1\n')
        f.write('0002 1 2\n')
        f.write('0001 2 0002 2\n')
        f.write('0002 2 0003 2\n')
        f.write('0001 2 0003 2\n')
        f.write('0003 1 2\n')
        f.write('0001 1 0002 2\n')
        f.write('0002 1 0003 2\n')
        f.write('0001 1 0003 2\n')
    return pairs_filename

if __name__ == "__main__":
    unittest.main()
    