from torchvision import datasets, transforms
from torch.utils.data import DataLoader, Dataset
from base import BaseDataLoader
import pandas as pd
import os
from .data_preprocess_GCN import ultragcn_preprocess


class MnistDataLoader(BaseDataLoader):
    """
    MNIST data loading demo using BaseDataLoader
    """
    def __init__(self, data_dir, batch_size, shuffle=True, validation_split=0.0, num_workers=1, training=True):
        trsfm = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize((0.1307,), (0.3081,))
        ])
        self.data_dir = data_dir
        self.dataset = datasets.MNIST(self.data_dir, train=training, download=True, transform=trsfm)
        super().__init__(self.dataset, batch_size, shuffle, validation_split, num_workers)


class UltraGCNDataset(Dataset):
    def __init__(self, data_dir):
        
        if not os.path.exists(os.path.join(data_dir, "data.csv")):
            self.train = pd.read_csv(os.path.join(data_dir, "train_data.csv"))
            self.test = pd.read_csv(os.path.join(data_dir, "test_data.csv"))
            ultragcn_preprocess(self.train, self.test)

        self.data = pd.read_csv(os.path.join(data_dir, "data.csv"))
        self.X = self.data.drop('answerCode', axis=1)
        self.y = self.data.answerCode
        
    def __getitem__(self, index):
        return self.X.loc[index].values, self.y.loc[index]
    
    def __len__(self):
        return len(self.data)      


class UltraGCNDataLoader(BaseDataLoader):
    def __init__(self, data_dir, batch_size, shuffle=False, num_workers=1, validation_split=0.0):
        
        self.data_dir = data_dir
        self.dataset = UltraGCNDataset(data_dir)
        
        super().__init__(self.dataset, batch_size, shuffle, validation_split, num_workers)