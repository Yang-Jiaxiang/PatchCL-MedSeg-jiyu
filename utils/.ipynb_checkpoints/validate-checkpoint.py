import torch
from tqdm import tqdm
from utils.performance import DiceCoefficient, MeanIOU

dev = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def validate(model, val_loader, criterion, num_classes):
    model.eval()
    model.module.contrast = False
    val_loss = 0.0
    total_samples = 0

    dice_coeff = DiceCoefficient()
    miou_metric = MeanIOU()

    with torch.no_grad():
        for imgs, masks in tqdm(val_loader, desc='Validating', leave=True):
            imgs = imgs.to(dev)
            masks = masks.to(dev)

            out = model(imgs)
            
            loss = criterion(out, masks)
            dice_coeff.add_batch(out, masks)
            miou_metric.add_batch(out, masks)
            
            val_loss += loss.item() * imgs.size(0)
            total_samples += imgs.size(0)

    val_loss /= total_samples
    val_dice = dice_coeff.evaluate()
    val_miou = miou_metric.evaluate()

    return val_loss, val_miou, val_dice