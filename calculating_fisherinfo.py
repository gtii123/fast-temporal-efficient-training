import argparse
import shutil
import os
import time
import torch
import warnings
import torch.nn as nn
import torch.nn.parallel
import torch.optim
from models.VGG_models import *
from models.resnet_models import *
import data_loaders
from functions import TET_loss, seed_all, get_logger
from copy import deepcopy

os.environ["CUDA_VISIBLE_DEVICES"] = "0,1,2,3,4,5,6,7"
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


parser = argparse.ArgumentParser(description='PyTorch Temporal Efficient Training')
parser.add_argument('-j',
                    '--workers',
                    default=16,
                    type=int,
                    metavar='N',
                    help='number of data loading workers (default: 10)')
parser.add_argument('--epochs',
                    default=150,
                    type=int,
                    metavar='N',
                    help='number of total epochs to run')
parser.add_argument('--start_epoch',
                    default=0,
                    type=int,
                    metavar='N',
                    help='manual epoch number (useful on restarts)')
parser.add_argument('-b',
                    '--batch_size',
                    default=2,
                    type=int,
                    metavar='N',
                    help='mini-batch size (default: 256), this is the total '
                         'batch size of all GPUs on the current node when '
                         'using Data Parallel or Distributed Data Parallel')
parser.add_argument('--lr',
                    '--learning_rate',
                    default=0.001,
                    type=float,
                    metavar='LR',
                    help='initial learning rate',
                    dest='lr')
parser.add_argument('--seed',
                    default=1000,
                    type=int,
                    help='seed for initializing training. ')
parser.add_argument('-T',
                    '--timestep',
                    default=10,
                    type=int,
                    metavar='N',
                    help='snn simulation time (default: 2)')
parser.add_argument('--means',
                    default=1.0,
                    type=float,
                    metavar='N',
                    help='make all the potential increment around the means (default: 1.0)')
parser.add_argument('--TET',
                    default=True,
                    type=bool,
                    metavar='N',
                    help='if use Temporal Efficient Training (default: True)')
parser.add_argument('--lamb',
                    default=1e-3,
                    type=float,
                    metavar='N',
                    help='adjust the norm factor to avoid outlier (default: 0.0)')
args = parser.parse_args()

if __name__ == '__main__':
    train_dataset, val_dataset = data_loaders.build_dvscifar('cifar-dvs')
    train_loader = torch.utils.data.DataLoader(train_dataset, batch_size=args.batch_size, shuffle=True,
                                               num_workers=args.workers, pin_memory=True)
    test_loader = torch.utils.data.DataLoader(val_dataset, batch_size=args.batch_size,
                                              shuffle=False, num_workers=args.workers, pin_memory=True)
    
    model = VGGSNNwoAP()

    criterion = nn.CrossEntropyLoss().to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)

    scheduler =  torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, eta_min=0, T_max=args.epochs)

    best_acc = 0
    best_epoch = 0

    fisherlist = []
    for t in range(args.timestep):
        fisherlist.append([])

    epochlist= [20,120,300]

    ep_ic_list = []
    
    logger = get_logger('exp.log')
    logger.info('start training!')
    
    for ep in epochlist:
        #TODO need to load model .pth here
        model.load_state_dict(torch.load(f"snapshots/T{str(args.timestep)}_ckpt_{str(ep).zfill(4)}.pth"))
        print ('Ep',str(ep),'--total time', str(args.timestep))
        ep_fisher_list = []
        for timestep in range(1, args.timestep+1):
            params = {n: p for n, p in model.named_parameters() if p.requires_grad}
            precision_matrices = {}   
            for n, p in deepcopy(params).items():
                p.data.zero_()
                precision_matrices[n] = p.data
            model.eval()
            running_loss = 0
            start_time = time.time()
            M = len(train_loader)
            total = 0
            correct = 0

            for step, (images, labels) in enumerate(train_loader):
                model.zero_grad()
                labels = labels.to(device)
                images = images.to(device)
                outputs = model(images)
                mean_out = outputs.mean(1)
                if args.TET:
                    loss = TET_loss(outputs,labels,criterion,args.means,args.lamb)
                else:
                    loss = criterion(mean_out,labels)
                running_loss += loss.item()
                loss.mean().backward()
                total += float(labels.size(0))
                _, predicted = mean_out.cpu().max(1)
                correct += float(predicted.eq(labels.cpu()).sum().item())
                running_loss, 100 * correct / total

                for n, p in model.named_parameters():
                    precision_matrices[n].data += p.grad.data ** 2 /100#len(train_loader)
                if step == 100:
                    break


            precision_matrices = {n: p for n, p in precision_matrices.items()}
            fisher_trace_info  = 0
            for p in precision_matrices:

                weight = precision_matrices[p]
                fisher_trace_info += weight.sum()

            print ("time", timestep, fisher_trace_info)
            fisherlist[timestep-1].append(float(fisher_trace_info.cpu().data.numpy()))
            ep_fisher_list.append(float(fisher_trace_info.cpu().data.numpy()))

        print ('fisher list', ep_fisher_list)
        with open('record.csv', 'a') as object_file:
            object_file.write(f'{str(ep_fisher_list)}\n')



    fisher_print = []
    for t in range(args.timestep):
        print ("----------fisher info at time", t)
        print (fisherlist[t])
        fisher_print.append(fisherlist[t][0])
    print ("fisher_print", fisher_print)         
