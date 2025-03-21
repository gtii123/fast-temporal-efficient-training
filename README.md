# Exploring Temporal Information Dynamics in Spiking Neural Networks: Fast Temporal Efficient Training
Hi, well come to the github home of paper "Exploring Temporal Information Dynamics in Spiking Neural Networks: Fast Temporal Efficient Training". You can use our codes, and we provide .pth files with you at https://pan.baidu.com/s/1UlKI2rLdj-PGl_TPrSfNHw, password: ffh5, to copy our experiment 
## Prerequisites
The Following Setup is tested and it is working:
* Python>=3.5
* Pytorch>=1.9.0
* Cuda>=10.2
## Preprocess of DVS-CIFAR
* Download CIFAR10-DVS dataset
* transform .aedat to .mat by test_dvs.m with matlab.
* prepare the train and test data set by dvscifar_dataloader.py
## Steps
1. traing VGGSNN models by main_training_parallel.py
2. calculating fisher information by calculating_fisherinfo.py
## Receiving
I am very happy,because my papaer have been received. If my papaer can help you, you can cite it.

## CITION
@article{HAN2025110401,
 author = {Changjiang Han and Li-Juan Liu and Hamid Reza Karimi},  
 title = {Exploring temporal information dynamics in Spiking Neural Networks: Fast Temporal Efficient Training},   
 journal = {Journal of Neuroscience Methods},   
 volume = {417},   
 pages = {110401},   
 year = {2025},   
 issn = {0165-0270},   
 doi = {https://doi.org/10.1016/j.jneumeth.2025.110401},  
 url = {https://www.sciencedirect.com/science/article/pii/S0165027025000421},   
}
