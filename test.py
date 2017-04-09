
from strategies.Ichimoku import Ichimoku

def main():
    ichimoku = Ichimoku();

    print ichimoku._calculateTenkanDegrees("HKD_JPY");


if __name__ == "__main__":
    main()
