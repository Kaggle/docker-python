from torch.utils import model_zoo
from torchvision.models.resnet import model_urls


def download_torchvision_models():
    for url in model_urls.values():
        model_zoo.load_url(url)


if __name__ == '__main__':
    download_torchvision_models()
