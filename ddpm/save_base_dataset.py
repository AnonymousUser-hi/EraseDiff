import torchvision.transforms as transforms
from torchvision.datasets import CIFAR10, STL10
from torchvision.utils import save_image
from torch.utils.data import ConcatDataset
import torch
import argparse
import os
import tqdm


def parse_args():
    
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--data_path", type=str, default='/data/datasets/CIFAR10', help="Path of your cifar10 dataset"
    )
    parser.add_argument(
        "--dataset", type=str, required=True, choices=['cifar10', 'stl10'], help="Dataset type, either cifar10 or stl10"
    )
    parser.add_argument(
        "--label_to_forget", type=int, default=0, help="will save all images *except* from this class label" 
    )
    args = parser.parse_args()
    return args


def all_but_one_class_dataset(data_path, dataset, label_to_forget):
    
    def find_indices(lst, condition):
        return [i for i, elem in enumerate(lst) if elem != condition]
    
    if dataset == "cifar10":
        dataset = CIFAR10(
            data_path,
            transform=transforms.ToTensor(),
        )
        
        idx = find_indices(dataset.targets, label_to_forget)
        subset = torch.utils.data.Subset(dataset, idx)
        loader = torch.utils.data.DataLoader(subset, batch_size=1000, shuffle=True, drop_last=False)
    
    elif dataset == "stl10":
        train_dataset = STL10(
            data_path,
            split="train",
            download=True,
            transform=transforms.Compose([transforms.Resize(64), 
                                         transforms.ToTensor()
                                         ])
        ) 
        test_dataset = STL10(
            data_path,
            split="test",
            download=True,
            transform=transforms.Compose([transforms.Resize(64), 
                                         transforms.ToTensor()
                                         ])
        )
        
        train_idx = find_indices(train_dataset.labels, label_to_forget) # note that STL10 uses .labels instead of .targets
        train_subset = torch.utils.data.Subset(train_dataset, train_idx)
        test_idx = find_indices(test_dataset.labels, label_to_forget)
        test_subset = torch.utils.data.Subset(test_dataset, test_idx)
        dataset = ConcatDataset([train_subset, test_subset])
        loader = torch.utils.data.DataLoader(dataset, batch_size=1000, shuffle=True, drop_last=False)
    
    return loader

if __name__ == "__main__":
    
    args = parse_args()
    dataloader = all_but_one_class_dataset(args.data_path, args.dataset, args.label_to_forget)
    save_dir_root = f"./{args.dataset}_without_label_" + str(args.label_to_forget)
    os.makedirs(save_dir_root, exist_ok=True)
    
    img_id = 0
    for x, c in tqdm.tqdm(dataloader):
        for x_ in x:
            save_image(x_, os.path.join(save_dir_root, f"{img_id}.png"), normalize=True)
            img_id += 1

    print(f"Saved {img_id} images without label {args.label_to_forget} to {save_dir_root}")