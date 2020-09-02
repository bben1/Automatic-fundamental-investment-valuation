import requests
import pandas as pd 
import numpy as np
import datetime

import matplotlib.pyplot as plot
import seaborn as sns

import pandas_datareader.data as web
import datetime
from pandas.util.testing import assert_frame_equal

class DCF:
    
    def __init__(self, income_statement, balance_sheet_statement, balance_sheet_statement_quarterly, cash_flow_statement, enterprise_value, financial_ratios, company_ticker, forecasting_period, api_key):
        """
        Summary:
        Reads data from financial statements and calculates a DCF valuation.
        inputs:
        income_statement (json): 'financialmodelingprep' income statement.
        balance_sheet_statement (json): 'financialmodelingprep' balance sheet statement (period=annual).
        balance_sheet_statement_quarterly (json): 'financialmodelingprep' balance sheet statement (period=quarter).
        cash_flow_statement (json): 'financialmodelingprep' cash flow statement.
        enterprise_value (json): 'financialmodelingprep' enterprise_value_statement.
        financial_ratios (json): 'financialmodelingprep' financial_ratios.
        company_ticker (str): e.g. 'AAPL' for Apple inc.
        forecasting_period (float/int): number of years to forecast.
        api_key (str): 'financialmodelingprep' secret api key.
        """
        
        self.inc = income_statement
        self.bs = balance_sheet_statement
        self.bsq = balance_sheet_statement_quarterly
        self.cf = cash_flow_statement
        self.ev = enterprise_value
        self.fr = financial_ratios
        self.ticker = company_ticker
        self.forecasting_period = forecasting_period
        self._api_key = api_key
    
    def get_interest_coverage_and_risk_free_rate(self):
        """
        Summary:
        Calculates the interest-coverage-ratio and risk-free-rate of the company.
        returns:
        risk_free_rate (float): Assumed risk-free-rate (based on US 1-Year treasury bonds)
        interest_coverage_ratio (float): interest coverage ratio = EBIT/interest_expense
        """
        
        #EBIT
        EBIT = self.inc[0]['ebitda'] - self.inc[0]['depreciationAndAmortization'] 

        #Interest Coverage
        interest_expense = self.inc[0]['interestExpense']
        self.interest_coverage_ratio = EBIT / interest_expense

        #Risk-free rate
        start = datetime.datetime(2019, 7, 10)
        end= datetime.datetime.today().strftime('%Y-%m-%d')
        
        Treasury = web.DataReader(['TB1YR'], 'fred', start, end)
        self.risk_free_rate = float(Treasury.iloc[-1])/100
        
        print(f"Interest coverage ratio: {round(self.interest_coverage_ratio,4)}")
        print(f"Risk free rate: {round(self.risk_free_rate,4)}")
        
    def get_cost_of_debt(self):
        """
        Summary:
        calculates the cost of debt of the company using the credit-rating method.
        Returns:
        cost of debt (float) = rfr / cs
        Where:
        rfr = risk-free-rate
        cs = credit-spread (calculated using interest-coverage-ratio)
        """
        if self.interest_coverage_ratio > 8.5:
            #Rating is AAA
            credit_spread = 0.0063
        elif (self.interest_coverage_ratio > 6.5) & (self.interest_coverage_ratio <= 8.5):
            #Rating is AA
            credit_spread = 0.0078
        elif (self.interest_coverage_ratio > 5.5) & (self.interest_coverage_ratio <=  6.5):
            #Rating is A+
            credit_spread = 0.0098
        elif (self.interest_coverage_ratio > 4.25) & (self.interest_coverage_ratio <=  5.49):
            #Rating is A
            credit_spread = 0.0108
        elif (self.interest_coverage_ratio > 3) & (self.interest_coverage_ratio <=  4.25):
            #Rating is A-
            credit_spread = 0.0122
        elif (self.interest_coverage_ratio > 2.5) & (self.interest_coverage_ratio <=  3):
            #Rating is BBB
            credit_spread = 0.0156
        elif (self.interest_coverage_ratio > 2.25) & (self.interest_coverage_ratio <=  2.5):
            #Rating is BB+
            credit_spread = 0.02
        elif (self.interest_coverage_ratio > 2) & (self.interest_coverage_ratio <=  2.25):
            #Rating is BB
            credit_spread = 0.0240
        elif (self.interest_coverage_ratio > 1.75) & (self.interest_coverage_ratio <=  2):
            #Rating is B+
            credit_spread = 0.0351
        elif (self.interest_coverage_ratio > 1.5) & (self.interest_coverage_ratio <=  1.75):
            #Rating is B
            credit_spread = 0.0421
        elif (self.interest_coverage_ratio > 1.25) & (self.interest_coverage_ratio <=  1.5):
            #Rating is B-
            credit_spread = 0.0515
        elif (self.interest_coverage_ratio > 0.8) & (self.interest_coverage_ratio <=  1.25):
            #Rating is CCC
            credit_spread = 0.0820
        elif (self.interest_coverage_ratio > 0.65) & (self.interest_coverage_ratio <=  0.8):
            #Rating is CC
            credit_spread = 0.0864
        elif (self.interest_coverage_ratio > 0.2) & (self.interest_coverage_ratio <=  0.65):
            #Rating is C
            credit_spread = 0.1134
        elif self.interest_coverage_ratio <=  0.2:
            #Rating is D
            credit_spread = 0.1512
        else:
            credit_spread = 0.1512

        self.cost_of_debt = self.risk_free_rate + credit_spread
        
        print(f"Cost of debt: {round(self.cost_of_debt,4)}")
    
    def get_costofequity(self):
        """
        Summary:
        calculates the CAPM of a company.
        Returns:
        capm (float) = rfr + beta*(iar-rfr)
        Where:
        rfr = risk-free-rate
        beta = company's beta value
        iar = index-annual-return
        """
        #Beta
        beta = requests.get(f'https://financialmodelingprep.com/api/v3/company/profile/{self.ticker}?apikey={self._api_key}').json()
        beta = float(beta['profile']['beta'])

        #Market Return
        start = datetime.datetime(2019, 7, 10)
        end = datetime.datetime.today().strftime('%Y-%m-%d')
        SP500 = web.DataReader(['sp500'], 'fred', start, end)
        SP500.dropna(inplace = True)
        SP500yearlyreturn = (SP500['sp500'].iloc[-1]/SP500['sp500'].iloc[-252]) - 1

        self.capm = self.risk_free_rate+(beta*(SP500yearlyreturn - self.risk_free_rate))
        
        print(f"CAPM: {round(self.capm,4)}")
    
    def get_wacc(self):
        """
        Summary:
        Calculates the weighted-average-cost-of-capital (WACC)
        Returns:
        WACC (float) = (kd*(1-ETR)*dp) + (ke*ep)
        Where:
        kd = cost-of-debt
        ke = cost-of-equity (capm)
        ETR -- effective-tax-rate
        dp -- proportion of company structure attributable to debt
        ep -- proportion of company structure attributable to equity
        """
        #effective tax rate
        self.effective_tax_rate = float(self.fr['ratios'][0]['profitabilityIndicatorRatios']['effectiveTaxRate'])
        #capital structure debt proportion
        dp = self.bsq[0]['totalDebt'] / (self.bsq[0]['totalDebt'] + self.bsq[0]['totalStockholdersEquity'])
        #capital structure equity proportion
        ep = self.bsq[0]['totalStockholdersEquity'] / (self.bsq[0]['totalDebt'] + self.bsq[0]['totalStockholdersEquity'])
        #wacc calculation
        self.wacc = (self.cost_of_debt*(1-self.effective_tax_rate)*dp) + (self.capm*ep)
        
        print(f"WACC: {round(self.wacc,4)}")
    
    def get_enterprise_value(self, earnings_growth_rate, cap_ex_growth_rate, perpetual_growth_rate):
        """
        Summary:
        Calculates the enterprise value of the company.
        Inputs:
        earnings_growth_rate (float): expected growth rate of earnings throughout forecast-period.
        cap_ex_growth_rate (float): expected growth rate of earnings throughout forecast-period.
        perpetual_growth_rate (float): expected long-term growth rate of free-cash-flow.
        Returns:
        enterprise_value = NPVFCF + NPVTV
        enterprise_value = sum(fcf1/(1+i)**1 + ... + fcfn/(1+i)**n) + (fcfn*(1+g)/i-g)/(1+i)**n
        Where:
        n = length of forecasting period
        fcfn = free-cash-flow in year n
        i = discount rate (WACC)
        g = perpetual growth rate
        """
        #define the variables used to calculate un-levered free cash flow
        self.g = perpetual_growth_rate
        self.eg = earnings_growth_rate
        self.cxg = cap_ex_growth_rate

        ebit = float(self.inc[0]['ebitda'] - self.inc[0]['depreciationAndAmortization'])
        non_cash_charges = float(self.cf[0]['depreciationAndAmortization'])
        cwc = float(self.cf[0]['changeInWorkingCapital'])
        cap_ex = float(self.cf[0]['capitalExpenditure'])
        
        ulfcf = ebit * (1-self.effective_tax_rate) + non_cash_charges + cwc + cap_ex
        #store a list of each cash flow and discount appropriately
        self.npv_fcf_list = [ulfcf]

        for yr in range(1, self.forecasting_period+1):    

            # increment each value by growth rate
            ebit = ebit * (1 + (yr * self.eg))
            non_cash_charges = non_cash_charges * (1 + (yr * self.eg))
            cap_ex = cap_ex * (1 + (yr * self.cxg))  
            cwc = cwc*0.7
            
            #calculate new fcf
            ulfcf = ebit * (1-self.effective_tax_rate) + non_cash_charges + cwc + cap_ex

            # discount by WACC
            PV_flow = ulfcf/((1 + self.wacc)**yr)
            self.npv_fcf_list.append(PV_flow)
        
        self.npv_fcf_sum = sum(self.npv_fcf_list)
        #Terminal value via the perpetual-growth method
        final_cashflow = self.npv_fcf_list[-1] * (1 + self.g)
        
        TV = final_cashflow/(self.wacc - self.g)
        
        NPV_TV = TV/(1+self.wacc)**(1+self.forecasting_period)
        #enterprise value calculation
        self.enterprise_value = NPV_TV + self.npv_fcf_sum
        
        print(f"Enterprise_value: {round(self.enterprise_value,4)}")
    
    def get_equity_value(self):
        """
        Summary:
        calculates the instrinsic value of a company.
        Returns:
        (dict) = {'equity value':float,
                  'implied share price': float}
        """
        #get values for enterprise-value to equity-value calculation
        self.debt = float(self.ev['enterpriseValues'][0]['+ Total Debt'])
        self.cash = float(self.ev['enterpriseValues'][0]['- Cash & Cash Equivalents'])
        self.number_of_shares = float(self.ev['enterpriseValues'][0]['Number of Shares'])

        self.equity_value = self.enterprise_value-self.debt+self.cash
        #intrinsic value per share
        self.share_price = self.equity_value/self.number_of_shares

        return {'equity value':self.equity_value, 
                'share_price':round(self.share_price,4)}
    
    def sensitivity(self, confidence_intervals = 0.9, bound = 0.4, plot=True):
        """
        Summary:
        Performs sensitivity analysis on WACC and g values.
        
        Inputs:
        confidence_intervals -- (list/float) A list of all of the confidence intervals at which to perform the sensitivity analysis.
        bound -- (float) Determines the range of WACC and g values. (0 < bound < 1)
        plot -- if True, returns a plot of all the implied share prices for varying WACC, g values.
        
        Returns:
        Summary of sensitivity analysis
        Plots demonstrating the distribution of implied share prices
        """
        #Define a range for the WACC
        wacc_lower_bound = self.wacc*(round(1-bound,2))
        wacc_upper_bound = self.wacc*(round(1+bound,2))
        wacc_step = self.wacc/100    
        wacc_range = np.arange(wacc_lower_bound, wacc_upper_bound, wacc_step)
        
        #Define a range for the long-term growth rate
        g_lower_bound = self.g*(0.6)
        g_upper_bound = self.g*(1.4) 
        g_step = self.g/100
        g_range = np.arange(g_lower_bound, g_upper_bound, g_step)
        
        #Create a function that calculates the implied share price for each wacc, g combination
        def implied_share_price(wacc, g):
            
            last = self.npv_fcf_list[-1]
            npv_tv = ((last*(1+g))/(wacc-g)) / ((1+wacc)**len(self.npv_fcf_list))
            ev = float(self.npv_fcf_sum + npv_tv)
            equity_value = ev-self.debt+self.cash
            share_price = equity_value/self.number_of_shares
        
            return share_price
        
        #Store each combination and the associated implied share price as tuples in a list
        ev_list = [(round(i,2),round(j,5),implied_share_price(i,j)) for j in g_range for i in wacc_range]
     
        #From this list, create a dataframe to store all of these values
        ev_df = pd.DataFrame(ev_list, columns = ['WACC','perpetual (g)','Implied share price'])
        
        #Convert the dataframe into a pivot table to better representation
        ev_piv = ev_df.pivot_table(values='Implied share price',index='WACC',columns='perpetual (g)')
        
        #Start printing the results of the sensitivity analysis
        print("***********************************************\n")
        print("Implied share price sensitivity analysis summary\n")
        
        print(f"Wacc range: {round(wacc_lower_bound,2)} : {round(wacc_upper_bound,2)}")
        print(f"Perpetual growth range: {round(g_lower_bound,2)} : {round(g_upper_bound,2)}\n")
        
        print(f"Minimum: ${round(ev_df['Implied share price'].min(),2)}")
        print(f"Maximum: ${round(ev_df['Implied share price'].max(),2)}")
        print(f"Mean: ${round(ev_df['Implied share price'].mean(),2)}")
        print(f"Median: ${round(ev_df['Implied share price'].median(),2)}\n")
        
        #For each confidence interval, calculate a range of implied share price
        for i in confidence_intervals:
            
            significance_level = (1-i)/2
            
            lower_bound = round(significance_level,4)
            lower_price = ev_df['Implied share price'].quantile(lower_bound)
        
            upper_bound = round(1-significance_level,4)
            upper_price = ev_df['Implied share price'].quantile(upper_bound)
            
            print(f"At confidence level {i}:")
            print(f"Intrinsic share price range: ${round(lower_price,4)} : ${round(upper_price,4)}\n")
        
        print("***********************************************\n")
        #plot the results with a distplot and a boxplot
        if plot:
            g1 = sns.distplot(ev_df['Implied share price'], norm_hist=True, axlabel = 'Implied share price', bins=100)
            plt.xticks(rotation=90)
            plt.ylabel('Frequency')
            plt.title('Implied share price with variation of WACC and g')
            plt.show(g1)
            
            g2 = sns.boxplot(ev_df['Implied share price'])
            plt.xticks(rotation=90)
            plt.title('Implied share price range')
            plt.show(g2)
        else:
            pass

        print("***********************************************\n")
        
        return ev_piv
              
        
