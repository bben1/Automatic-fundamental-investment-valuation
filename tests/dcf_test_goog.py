from keys.secrets import *
from data.get_statements import get_statement
from tools.dcf_class import DCF 
from tools.piotroski_class import Piotroski

def main():
    #get the data
    inc = get_statement(company_ticker = 'GOOG',
                    statement_name = 'income-statement',
                    api_key = api
                    )
    bs = get_statement(company_ticker = 'GOOG',
                        statement_name = 'balance-sheet-statement',
                        api_key = api
                        )
    bsq = get_statement(company_ticker = 'GOOG',
                        statement_name = 'balance-sheet-statement',
                        api_key = api,
                        frequency = 'quarter'
                        )
    cf = get_statement(company_ticker = 'GOOG',
                        statement_name = 'cash-flow-statement',
                        api_key = api
                        )
    ev = get_statement(company_ticker = 'GOOG',
                        statement_name = 'enterprise-value',
                        api_key = api
                        )
    fr = get_statement(company_ticker = 'GOOG',
                        statement_name = 'financial-ratios',
                        api_key = api,
                        )
    #create the dcf object
    dcf = DCF(income_statement = inc,
          balance_sheet_statement = bs,
          balance_sheet_statement_quarterly = bsq,
          cash_flow_statement = cf,
          enterprise_value = ev,
          financial_ratios = fr,
          company_ticker = 'GOOG',
          forecasting_period = 4,
          api_key = api
          )

    #calculate the dcf
    dcf.get_interest_coverage_and_risk_free_rate()
    dcf.get_cost_of_debt()
    dcf.get_costofequity()
    dcf.get_wacc()
    
    #still need to calculate these arguments (currently from google search)
    dcf.get_enterprise_value(earnings_growth_rate = 0.1,
                             cap_ex_growth_rate = 0.2,
                             perpetual_growth_rate = 0.02)
    
    # Iinitial calculation to get implied share price
    dcf.get_equity_value()
    
    #Finish by performing sensitivity analysis on the results
    return dcf.sensitivity(confidence_intervals = [0.95, 0.9, 0.85, 0.8, 0.75, 0.7], bound = 0.3)

if __name__ == '__main__':
    main()
