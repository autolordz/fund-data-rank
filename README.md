# fund-data_rank

## 获取国内基金数据当前净值，并使用回归方法来排名

理论（个人见解，不代表权威） \
假设平日50只基金有20个主题板块，有涨有跌，排名是在这50只之间，跌就值得买涨就值得卖，一池水流来流去，牛市熊市全部涨跌除外，方便大家一键快速做出抉择


### 用途 \
1. 快速获取近期基金涨跌 \
2. 预测T+1日基金上升或者下跌，简单地综合所有回归来排序 \
3. 排第一T+1有涨趋势，排最后T+1有跌趋势

### 前提 \
准备50只至少20个主题板块的基金

### INPUT \
基金号码列excel表

### OUTPUT \
excel表包含以下字段

['code','name','type','manager','netWorth','fundScale',
         'dayGrowth','expectGrowth','lastWeekGrowth','lastMonthGrowth','lastThreeMonthsGrowth']
         
而且包含回归方法计算出来的排名


         
    
