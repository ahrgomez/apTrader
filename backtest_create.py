
from api.PricesStream import PricesStream

ticks = [];

def main():
    pricesStream = PricesStream();

    for tick in pricesStream.GetStreamingData("EUR_USD"):
        with open('csvfile.csv','a') as file:
            line = tick['instrument'] + "," + tick['time'] + "," + str(tick['price'])
            file.write(line)
            file.write('\n')
if __name__ == "__main__":
    main()
