import os
import argparse
from tqdm import tqdm
import torch
import torch.nn as nn
import torch.optim as optim
from torch.optim import lr_scheduler

from model.model import get_model
from model.data import get_dataloaders


def save_checkpoint(state, is_best, output_dir, filename='checkpoint.pth'):
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, filename)
    torch.save(state, path)
    if is_best:
        best_path = os.path.join(output_dir, 'best.pth')
        torch.save(state, best_path)


def accuracy(output, target):
    preds = torch.argmax(output, dim=1)
    correct = (preds == target).sum().item()
    return correct / target.size(0)


def train_epoch(model, loader, criterion, optimizer, device):
    model.train()
    running_loss = 0.0
    running_acc = 0.0
    for images, labels in tqdm(loader, desc='Train', leave=False):
        images = images.to(device)
        labels = labels.to(device)
        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        running_loss += loss.item() * images.size(0)
        running_acc += accuracy(outputs, labels) * images.size(0)

    n = len(loader.dataset)
    return running_loss / n, running_acc / n


def validate(model, loader, criterion, device):
    model.eval()
    running_loss = 0.0
    running_acc = 0.0
    with torch.no_grad():
        for images, labels in tqdm(loader, desc='Val', leave=False):
            images = images.to(device)
            labels = labels.to(device)
            outputs = model(images)
            loss = criterion(outputs, labels)
            running_loss += loss.item() * images.size(0)
            running_acc += accuracy(outputs, labels) * images.size(0)

    n = len(loader.dataset)
    return running_loss / n, running_acc / n


def main():
    current_path = os.path.abspath(__file__)
    current_dir = os.path.dirname(current_path)
    parent_dir = os.path.dirname(current_dir)

    parser = argparse.ArgumentParser(description='Train FER2013 emotion model')
    parser.add_argument('--data-dir', default='dataset/FER2013/archive', help='Path to dataset archive directory (e.g. dataset/FER2013/archive)')
    parser.add_argument('--epochs', type=int, default=20)
    parser.add_argument('--batch-size', type=int, default=64)
    parser.add_argument('--lr', type=float, default=1e-4)
    parser.add_argument('--img-size', type=int, default=224)
    parser.add_argument('--output', default=parent_dir+'\\checkpoints', help='Directory to save checkpoints')
    parser.add_argument('--num-workers', type=int, default=4)
    parser.add_argument('--device', default='cuda' if torch.cuda.is_available() else 'cpu')
    parser.add_argument('--resume', default=None, help='Path to checkpoint to resume training')
    parser.add_argument('--pretrained-weights', default=None, help='Path to weights for fine-tuning (loads weights but not optimizer)')
    args = parser.parse_args()

    device = torch.device(args.device)

    train_loader, val_loader, classes = get_dataloaders(args.data_dir, batch_size=args.batch_size,
                                                       img_size=args.img_size, num_workers=args.num_workers)
    num_classes = len(classes)

    model = get_model(num_classes=num_classes, pretrained=True)
    model = model.to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=args.lr)
    scheduler = lr_scheduler.StepLR(optimizer, step_size=7, gamma=0.1)

    start_epoch = 0
    best_acc = 0.0

    # Optionally load pretrained weights for fine-tuning (model weights only)
    if args.pretrained_weights:
        print(f'Loading pretrained weights from {args.pretrained_weights} (model only)')
        checkpoint = torch.load(args.pretrained_weights, map_location=device)
        model.load_state_dict(checkpoint['model_state_dict'])

    # Optionally resume full training state
    if args.resume:
        print(f'Resuming from checkpoint {args.resume}')
        checkpoint = torch.load(args.resume, map_location=device)
        model.load_state_dict(checkpoint['model_state_dict'])
        optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        scheduler.load_state_dict(checkpoint.get('scheduler_state_dict', {}))
        start_epoch = checkpoint.get('epoch', 0) + 1
        best_acc = checkpoint.get('best_acc', 0.0)

    for epoch in range(start_epoch, args.epochs):
        print(f'Epoch {epoch+1}/{args.epochs}')
        train_loss, train_acc = train_epoch(model, train_loader, criterion, optimizer, device)
        val_loss, val_acc = validate(model, val_loader, criterion, device)
        scheduler.step()

        is_best = val_acc > best_acc
        if is_best:
            best_acc = val_acc

        print(f'Train loss {train_loss:.4f} acc {train_acc:.4f} | Val loss {val_loss:.4f} acc {val_acc:.4f}')

        save_checkpoint({
            'epoch': epoch,
            'model_state_dict': model.state_dict(),
            'optimizer_state_dict': optimizer.state_dict(),
            'scheduler_state_dict': scheduler.state_dict(),
            'best_acc': best_acc,
            'num_classes': num_classes,
        }, is_best, args.output, filename=f'checkpoint_epoch{epoch+1}.pth')

    print('Training finished. Best val acc: {:.4f}'.format(best_acc))


if __name__ == '__main__':
    main()
