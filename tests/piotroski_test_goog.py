from data.get_statements import get_statement
from tools.piotroski_class import Piotroski

def main():

    #get the statements
    inc = get_statement(company_ticker = 'GOOG',
                        statement_name = 'income-statement',
                        api_key = api
                        )
    bs = get_statement(company_ticker = 'GOOG',
                        statement_name = 'balance-sheet-statement',
                        api_key = api
                        )
    cf = get_statement(company_ticker = 'GOOG',
                        statement_name = 'cash-flow-statement',
                        api_key = api
                        )
    fr = get_statement(company_ticker = 'GOOG',
                        statement_name = 'financial-ratios',
                        api_key = api
                        )
    
    #instantiate the class
    f1 = Piotroski(income_statement = inc,
                   balance_sheet = bs,
                   cash_flow_statement = cf,
                   financial_ratios = fr)
    
    #perform the analysis
    return f1.f_score()

if __name__ == '__main__':
    main()
