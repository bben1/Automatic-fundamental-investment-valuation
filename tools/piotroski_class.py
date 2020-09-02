import numpy as np

class Piotroski:
    """
    Summary:
    Stores the financial statements of a company and calculates Piotroski's f-score.
    
    Inputs:
    income_statement -- (json)
    balance_sheet -- (json)
    cash_flow_statement -- (json)
    financial_ratios -- (json)
    
    """
    def __init__(self, income_statement, balance_sheet, cash_flow_statement, financial_ratios):
        self.fr = financial_ratios
        self.inc = income_statement
        self.bs = balance_sheet
        self.cf = cash_flow_statement
        
    def f_score(self):
        """
        Summary: Calculates f1-score based on 9 financial conditions.
        
        Returns:
        dict containing the results.
        
        """
        f1_score = 0
        profitability_score = 0
        leverage_liquidity_score = 0
        operating_efficiency_score = 0
        
        print("Results:\n")

        #profitability conditions
        
        #1) Return on Assets (1 point if it is positive in the current year, 0 otherwise)
        roa = float(self.fr['ratios'][0]['profitabilityIndicatorRatios']['returnOnAssets'])
        print(f"P1(return_on_assets > 0): {roa}")
        
        #2) Operating Cash Flow (1 point if it is positive in the current year, 0 otherwise)
        opcfps = float(self.fr['ratios'][0]['cashFlowIndicatorRatios']['operatingCashFlowPerShare'])
        print(f"P2(opCF > 0): {opcfps}")
        
        #3) Change in Return of Assets (ROA) (1 point if ROA is higher in the current year compared to the previous one, 0 otherwise)
        roa_this_year = float(self.fr['ratios'][0]['profitabilityIndicatorRatios']['returnOnAssets'])
        roa_last_year = float(self.fr['ratios'][1]['profitabilityIndicatorRatios']['returnOnAssets'])
        roa_change = roa_this_year - roa_last_year
        print(f"P3(return_on_assets_change > 0): {roa_change}")
        
        #4) Accruals (1 point if Operating Cash Flow/Total Assets is higher than ROA in the current year, 0 otherwise)
        op_ta = float(self.cf[0]['operatingCashFlow'] / self.bs[0]['totalAssets'])
        print(f"P4(opCF/totalAssets > return_on_assets): {(op_ta, roa)}")
        
        #Leverage, liquidity and source of funds conditions
        
        #5) Change in Leverage (long-term) ratio (1 point if the ratio is lower this year compared to the previous one, 0 otherwise)
        ltd_this_year = float(self.bs[0]['longTermDebt']/self.bs[0]['totalDebt'])
        ltd_last_year = float(self.bs[1]['longTermDebt']/self.bs[1]['totalDebt'])
        ltd_change = ltd_this_year - ltd_last_year
        print(f"LL5(long_term_leverage_change < 0): {ltd_change}")
        
        #6) Change in Current ratio (1 point if it is higher in the current year compared to the previous one, 0 otherwise)
        cur_this_year = float(self.bs[0]['totalCurrentAssets']/self.bs[0]['totalCurrentLiabilities'])
        cur_last_year = float(self.bs[1]['totalCurrentAssets']/self.bs[1]['totalCurrentLiabilities'])
        cur_change = cur_this_year - cur_last_year
        print(f"LL6(current_ratio_change > 0): {cur_change}")
        
        #7) Change in the number of shares (1 point if no new shares were issued during the last year)
        shares_this_year = float(self.inc[0]['weightedAverageShsOutDil'])
        shares_last_year = float(self.inc[1]['weightedAverageShsOutDil'])
        shares_change = shares_this_year - shares_last_year
        print(f"LL7(number_of_shares_change == 0): {shares_change}")
        
        # Operating efficiency conditions
        
        #8) Change in Gross Margin (1 point if it is higher in the current year compared to the previous one, 0 otherwise)
        gm_this_year = float(self.fr['ratios'][0]['profitabilityIndicatorRatios']['returnOnAssets'])
        gm_last_year = float(self.fr['ratios'][1]['profitabilityIndicatorRatios']['returnOnAssets'])
        gm_change = gm_this_year - gm_last_year
        print(f"OE8(gross_margin_change > 0): {gm_change}")
        
        #9) Change in Asset Turnover ratio (1 point if it is higher in the current year compared to the previous one, 0 otherwise)
        at_this_year = float(self.fr['ratios'][0]['operatingPerformanceRatios']['assetTurnover'])
        at_last_year = float(self.fr['ratios'][1]['operatingPerformanceRatios']['assetTurnover'])
        at_change = at_this_year - at_last_year
        print(f"OE9(asset_turnover_ratio_change > 0): {at_change}")
        
        print("\n******************************************************\n")
        
        conditions = {'profitability':{
                                      'profitability1':(roa>0),
                                      'profitability2':(opcfps>0),
                                      'profitability3':(roa_change>0),
                                      'profitability4':(op_ta>roa_this_year)
                                      },
                      'leverage_and_liquidity':{
                                                'leverage_liquidity1':(ltd_change<0),
                                                'leverage_liquidity2':(cur_change>0),
                                                'leverage_liquidity3':(shares_change==0)
                                               },
                      'operational_efficiency':{
                                                'operational_efficiency_1':(gm_change>0),
                                                'operational_efficiency_2':(at_change>0)}
                                               }
        
        print("Conditions satisifed:\n")
        for i in conditions.keys():
            
            for j in conditions[i].keys():
                print(f"{j}: {conditions[i][j]}")
                
                
                if (conditions[i][j]) & (i == 'profitability'):
                   
                    f1_score += 1
                    profitability_score += 1
                
                elif (conditions[i][j]) & (i == 'leverage_and_liquidity'):
                    
                    f1_score += 1
                    leverage_liquidity_score += 1
                    
                elif (conditions[i][j]) & (i == 'operational_efficiency'):
                    
                    f1_score += 1
                    operating_efficiency_score += 1
              
                else:
                    pass
        
        f1_performance = round((f1_score/9)*100,4)
        profitability_performance = round((profitability_score/4)*100,4)
        leverage_liquidity_performance = round((leverage_liquidity_score/3)*100,4)
        operating_efficiency_performance = round((operating_efficiency_score/2)*100,4)
        
        print("\n******************************************************\n")
        
        print("Results summary:")
        
        return {'F1-Score':f1_score, 
                'F1-performance':str(f1_performance)+'%',
                'Profitability-score':profitability_score,
                'Profitability-performance':str(profitability_performance)+'%',
                'leverage-liquidity-score':leverage_liquidity_score,
                'leverage-liquidity-performance':str(leverage_liquidity_performance)+'%',
                'operating-efficiency-score':operating_efficiency_score,
                'operating-efficiency-performance':str(operating_efficiency_performance)+'%'
               }
