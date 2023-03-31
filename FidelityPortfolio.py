import sys
import pandas
import yfinance as yf
import numpy as np

class FidelityPortfolio():
    """
    Holds data on a single fidelity portfolio account
    """

    def __init__(self, positions_file = None,name = None):
        self.positions_file = positions_file
        self.positions_df = pandas.read_csv(self.positions_file)
        self.name = name

        self.date = self.positions_df['Account Number'].iloc[-1]

        # Remove any extra rows
        nstocks = len([x for x in self.positions_df['Last Price'] if x is not np.nan])
        self.positions_df = self.positions_df.truncate(after=nstocks-1).copy(deep=True)

        self.total_value    = 0
        self.total_cost     = 0
        self.total_return   = 0
        self.percent_return = 0

        self.update_spot()
        self.report()

    def update_spot(self):
        """
        Update spot prices for each asset
        """

        self.positions_df['Updated Price'] = self.positions_df.loc[:,'Last Price']

        # Read in all stock ID's in portfolio
        stocklist_pyxl = self.positions_df['Symbol']
        spots = {}

        # Call yahoo finance API
        for j in range(len(stocklist_pyxl)):
            symbol = stocklist_pyxl[j]
            if symbol == 'SPAXX**': 
                spots['SPAXX**'] = 1.0
                self.positions_df.loc[j,'Cost Basis Total'] = '$1.0'
            else:
                tickdata = yf.Ticker(symbol)  
                spot = tickdata.history(period='1d')
                spots[symbol] = spot['Close'][0]

            # Update dataframe
            self.positions_df.loc[j,'Updated Price'] = spot['Close'][0]
            self.positions_df.loc[j,'Current Value'] = spot['Close'][0] * self.positions_df['Quantity'][j]
            self.positions_df.loc[j,'Total Gain/Loss Dollar']  = self.positions_df['Current Value'][j] - float(self.positions_df['Cost Basis Total'][j][1:])
            self.positions_df.loc[j,'Total Gain/Loss Percent'] = (self.positions_df['Total Gain/Loss Dollar'][j] / float(self.positions_df['Cost Basis Total'][j][1:])) * 100

    def report(self):
        self.total_value    = self.positions_df['Current Value'].sum()
        self.total_cost     = np.sum([float(x[1:]) for x in self.positions_df['Cost Basis Total']])
        self.total_return   = self.total_value - self.total_cost
        self.percent_return = 100 * (self.total_value - self.total_cost) / self.total_cost

        if self.total_return < 0:
            sign = '-' 
        else:
            sign = ''

        msg = f'\n\nYour {self.name} Fidelity Portfolio Summary\n' + \
              f'Total Value:    ${self.total_value:.2f}\n' + \
              f'Total Cost:     ${self.total_cost:.2f}\n' + \
              f'Total Return:   {sign}${abs(self.total_return):.2f}\n' + \
              f'Percent Return:    {self.percent_return:.2f}%\n' + \
              f'{self.date}\n\n'

        print(msg)

def main(fidelity_report):

    Fid = FidelityPortfolio(fidelity_report,'Stocks')
    return Fid

if __name__ == '__main__':
    fidelity_report = sys.argv[1]
    main(fidelity_report)