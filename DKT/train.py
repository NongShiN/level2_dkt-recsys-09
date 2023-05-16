import os
import numpy as np
import torch
import wandb
import lightgbm as lgb
from matplotlib import pyplot as plt

from args import parse_args
from model.preprocess import load_data, feature_engineering, custom_train_test_split, categorical_label_encoding, convert_time, add_diff_feature
from trainer.trainer import train_model


if __name__ == "__main__":
    wandb.login()
    args = parse_args(mode="train")
    args.device = "cuda" if torch.cuda.is_available() else "cpu"

    # 사용할 Feature 설정
    FEATS = ['KnowledgeTag', 'user_correct_answer', 'user_acc', 'test_mean',
     'test_sum','tag_mean', 'assessmentItemID', 'Timestamp', 'diff', 'mean']

    # Preprocessing
    print("Preparing data ...")
    df = load_data(args)
    df = feature_engineering(df)
    df = categorical_label_encoding(args, df, is_train=True)
    df["Timestamp"] = df["Timestamp"].apply(convert_time)
    df = add_diff_feature(df)

    train, test = custom_train_test_split(args, df)
    print("Done Preprocessing!!")

    wandb.init(project="dkt", config=vars(args))


    # Train a selected model
    print("Start Training ...")
    trained_model = train_model(args, train, test, FEATS)
    print("Done training!!")

    # Save a feature importance
    x = lgb.plot_importance(trained_model)
    if not os.path.exists(args.pic_dir):
        os.makedirs(args.pic_dir)
    plt.savefig(os.path.join(args.pic_dir, 'lgbm_feature_importance.png'))
    
    print("Done!")





















"""import argparse
import collections
import torch
import numpy as np
import data_loader.data_loaders as module_data
import model.loss as module_loss
import model.metric as module_metric
import model.model as module_arch
from parse_config import ConfigParser
from trainer import Trainer
from utils import prepare_device
import warnings
warnings.filterwarnings(action='ignore')

# fix random seeds for reproducibility
SEED = 42
torch.manual_seed(SEED)
torch.backends.cudnn.deterministic = True
torch.backends.cudnn.benchmark = False
np.random.seed(SEED)

def main(config):
    logger = config.get_logger('train')

    # setup data_loader instances
    data_loader = config.init_obj('data_loader', module_data)
    valid_data_loader = data_loader.split_validation()

    # build model architecture, then print to console
    model = config.init_obj('arch', module_arch)
    logger.info(model)

    # prepare for (multi-device) GPU training
    device, device_ids = prepare_device(config['n_gpu'])
    model = model.to(device)
    if len(device_ids) > 1:
        model = torch.nn.DataParallel(model, device_ids=device_ids)

    # get function handles of loss and metrics
    criterion = getattr(module_loss, config['loss'])
    metrics = [getattr(module_metric, met) for met in config['metrics']]

    # build optimizer, learning rate scheduler. delete every lines containing lr_scheduler for disabling scheduler
    trainable_params = filter(lambda p: p.requires_grad, model.parameters())
    optimizer = config.init_obj('optimizer', torch.optim, trainable_params)
    lr_scheduler = config.init_obj('lr_scheduler', torch.optim.lr_scheduler, optimizer)

    trainer = Trainer(model, criterion, metrics, optimizer,
                      config=config,
                      device=device,
                      data_loader=data_loader,
                      valid_data_loader=valid_data_loader,
                      lr_scheduler=lr_scheduler)

    trainer.train()


if __name__ == '__main__':
    args = argparse.ArgumentParser(description='PyTorch Template')
    args.add_argument('-c', '--config', default=None, type=str,
                      help='config file path (default: None)')
    args.add_argument('-r', '--resume', default=None, type=str,
                      help='path to latest checkpoint (default: None)')
    args.add_argument('-d', '--device', default=None, type=str,
                      help='indices of GPUs to enable (default: all)')

    # custom cli options to modify configuration from default values given in json file.
    CustomArgs = collections.namedtuple('CustomArgs', 'flags type target')
    options = [
        CustomArgs(['--lr', '--learning_rate'], type=float, target='optimizer;args;lr'),
        CustomArgs(['--bs', '--batch_size'], type=int, target='data_loader;args;batch_size')
    ]
    config = ConfigParser.from_args(args, options)
    main(config)
"""