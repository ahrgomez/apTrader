from strategies.Ichimoku import Ichimoku
from lib.ApiData import ApiData

def main():
    lp = ApiData().GetActualPrice('GBP_SGD');
    Ichimoku().PrintIchimoku('GBP_SGD', lp);

if __name__ == "__main__":
    main()
