# -*- coding: utf-8 -*-
"""
Created on Mon Feb 27 15:54:55 2023

@author: Autozhz
"""

#%% 获取5星期基金结果取十日

import json,os
import pandas as pd
import requests,os,datetime,time

df = pd.read_excel(os.path.join('D:\Python\FundGet', '基金代码.xlsx'),
                   dtype={'code': str},
                   na_filter=0)

# fund codes list
cl = df[df['code'] != '']['code'].to_list()
# cl = ['007937','010364','014256']

t_now = datetime.datetime.now()
t_4 = t_now + datetime.timedelta(weeks=-5)


dd = pd.DataFrame()
# 每次请求API获取50只，太多不好
cl_size = 50
for i in range(0, len(cl), cl_size):
    
    print(len(cl[i:i+cl_size]))
    cl1 = cl[i:i+cl_size]

    # 小熊基金接口
    url = 'https://api.doctorxiong.club/v1/fund/detail/list'
    params = {
        'code':','.join(cl1),
        'startDate':t_4.strftime('%Y-%m-%d'), 
        'endDate':t_now.strftime('%Y-%m-%d')}
    
    dict1 = json.loads(requests.get(url, params).content.decode())
    dd1 = pd.DataFrame(dict1['data'])
    dd = pd.concat([dd,dd1])
    time.sleep(0.2)
dd = dd.reset_index(drop=1)

bb = dd[['code','name','type','manager','netWorth','fundScale',
         'dayGrowth','expectGrowth','lastWeekGrowth','lastMonthGrowth','lastThreeMonthsGrowth']]

bb[['dayGrowth','expectGrowth','lastWeekGrowth','lastMonthGrowth','lastThreeMonthsGrowth']] = \
bb[['dayGrowth','expectGrowth','lastWeekGrowth','lastMonthGrowth','lastThreeMonthsGrowth']].apply(lambda x: x+'%')

# expand netWorthData into column
df1 = pd.DataFrame()
for x in range(len(dd)):
    ee = dd.loc[x,'netWorthData']
    df0 = pd.DataFrame(ee,columns=['date','worth','rate',''])
    # for rate
    df11 = df0[['date','rate']].T
    df11.columns = df11.iloc[0]
    df11 = df11.iloc[1:]
    df1 = pd.concat([df1,df11])
df1 = df1.fillna(0).reset_index(drop=1)

# 使用5星期结果计算，以下使用多个回归方法计算分数来排名，哪个趋势向上哪个向下
import numpy as np

date_colums = df1.columns # bb.iloc[:,10:]
y = df1.to_numpy()
SAMPLE_NUM = date_colums.shape[0]

x = np.linspace(0,SAMPLE_NUM-1, SAMPLE_NUM)
X = x[:, np.newaxis]
Y = y.T.astype(np.float64)

from sklearn.linear_model import LinearRegression, TheilSenRegressor,\
                                 ElasticNet,QuantileRegressor,HuberRegressor,RANSACRegressor
import time
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline


# Pred and Rank with 2D estimators
cutidx = 1
X_train,X_test = X[:X.shape[0]-cutidx],X[X.shape[0]-cutidx:]
Y_train,Y_test = Y[:Y.shape[0]-cutidx],Y[Y.shape[0]-cutidx:]

# Lr1
lr = LinearRegression(fit_intercept=1)
y_predict = lr.fit(X_train, Y_train).predict(X_train)
ee = bb[['code','name']]
ee['l_coef'] = lr.coef_
ee.loc[:,'rank1'] = ee['l_coef'].rank(ascending=0)

estimators = [
    ('OLS', LinearRegression()),
    ('ElasticNet', ElasticNet()),
    ]

# 多项式回归 2 - 4 特征
polyi = 4
t0 = time.time()
for name, estimator in estimators:
    for n in range(2,polyi):
        t0 = time.time()
        model = make_pipeline(PolynomialFeatures(n), estimator)
        model.fit(X_train, Y_train)
        elapsed_time = time.time() - t0
        y_pred = model.predict(X_test)
        ee.loc[:,'poly%s_%s'%(n,name)] = y_pred[0]
        
for name, estimator in estimators:
    for n in range(2,polyi):
        ee.loc[:,'rank%s_%s'%(n,name)] = ee['poly%s_%s'%(n,name)].rank(ascending=0)
print('Rank with 2D runing time: %.3f'%(time.time() - t0))


# Pred and Rank with 1D estimators
cutidx = 1
X_train,X_test = X[:X.shape[0]-cutidx],X[X.shape[0]-cutidx:]
Y_train,Y_test = Y[:Y.shape[0]-cutidx],Y[Y.shape[0]-cutidx:]

# Predict from Regressor as below
estimators1d = [
    ('Huber', HuberRegressor()),
    ('Quantile', QuantileRegressor()),
    ('Theil-Sen', TheilSenRegressor()),
    ('RANSAC', RANSACRegressor()),
    ]
t0 = time.time()
for idx in range(Y_train.shape[1]):
    for name, estimator in estimators1d:
        model = make_pipeline(PolynomialFeatures(2), estimator)
        model.fit(X_train, Y_train[:,idx])
        y_pred = model.predict(X_test)
        ee.at[idx,'pred_%s'%name] = y_pred

# Rank all the predict value with these fund
for name, estimator in estimators1d:
    ee['rank_%s'%name] = ee['pred_%s'%name].rank(ascending=0)
print('Rank with 1D runing time: %.3f'%(time.time() - t0))

# Rank all the Regressor of all the funds
ee['r_all'] = ee.loc[:,ee.columns.str.contains('rank.*')].sum(axis=1).rank(ascending=1,method='average')
ee['r_all1'] = ee['r_all'].rank(ascending=0,method='average')

# 取10日结果输出
ff = pd.concat([bb.iloc[:,:7],
                df1.iloc[:,-10:].applymap(lambda x: '%s%s'%(x,'%')),
                bb.iloc[:,7:],
                ee[['r_all','r_all1']]],axis=1)

save_path = os.path.join('D:\Python\FundGet', 'coef2.xlsx')
ff.to_excel(save_path,index=0)
os.system('start excel %s'%save_path)


