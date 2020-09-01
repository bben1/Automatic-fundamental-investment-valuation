import requests
import pandas as pd

def get_statement(company_ticker, statement_name, api_key, frequency='annual', df = False):
    """
    Get a financial statement to use for fundamental calculations
    
    inputs:
    company_ticker (str) -- e.g. 'AAPL' for Apple inc.
    statement_name (str) -- one of: 'income-statement','balance-sheet-statement','cash-flow-statement','enterprise-value'
    period (str) -- 'annual' or 'quarter'
    forecast_period (int) -- Number of years you wish to forecast
    api_key (str) -- api key to access financialmodelingprep account
    
    returns:
    Pandas DataFrame object
    """
    if statement_name in ['income-statement','balance-sheet-statement','cash-flow-statement', 'enterprise-value', 'financial-ratios']:
        
        statement = requests.get(f'https://financialmodelingprep.com/api/v3/{statement_name}/{company_ticker}?period={frequency}&apikey={api_key}').json()
        
        if df:
            statement = pd.DataFrame.from_dict(statement[0], orient='index')
            statement = statement.iloc[5:-2]
            statement.columns = ['Year 0']
            statement['Year 0'] = statement['Year 0'].astype('float64')
        
        else:
            pass
    
    return statement