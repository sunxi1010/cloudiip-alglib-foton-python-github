import time
import random
from string import Template
from datetime import datetime

import numpy as np 
import pandas as pd 
from statsmodels.tsa.holtwinters import Holt
from sqlalchemy.orm import Session
from fastapi import FastAPI, Depends, Body, HTTPException
from pydantic import BaseModel

from crud.crud_param import get_all_params
from db.database import get_db, SessionLocal
from db.iotdb import get_iotdb

from logging.config import dictConfig
import logging
from config.logconfig import LogConfig

app = FastAPI(title="ML API", description="API for cloudiip-bit-plugins ml model", version="1.0")

# iotdb实时数据接口
IOTDB_API_URL = "http://ip:port/get/device/point"
DATE_TIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DEVICE_NAME = "root.iot_device_BIT_fan.ycfjA"
sql_template = Template("select \
$paramcode from " + DEVICE_NAME + \
" where time >= $starttime" + \
" and time < $currenttime")
DAY_TIMESTAMP = 86400000

dictConfig(LogConfig().dict())
logger = logging.getLogger("mycoolapp")

# 创建请求体
class ModelInput(BaseModel):
    time: int
    real: float
    paramcode: str

class ModelOuput(ModelInput):
    predict: float
    error: float
    similarity: float

rowName = []
rowCode = []

@app.on_event("startup")
def start_up():
    # 模拟设备数据
    # 获取接口数据
    params_list = get_all_params(SessionLocal())
    # 获取设备属性表中的所有列名
    for param in params_list:
        rowName.append(param.param_name)
        rowCode.append(param.param_code)

    print(rowCode)

def array_zero_replace_median(foo):
    # Compute the median of the non-zero elements
    m = np.median(foo[foo > 0])
    # Assign the median to the zero elements 
    foo[foo == 0] = m
    return foo

def array_zero_replace_after(foo):
    # Compute the median of the non-zero elements
    zero_index = np.where(foo==0)[0]
    # Assign the median to the zero elements 
    for index in zero_index:
        if index + 1 == len(foo):
            foo[index] = foo[index - 1]
            return foo
        foo[index] = foo[index + 1]
    return foo


def model_train(data):
    y = array_zero_replace_after(data)
    fit1 = Holt(
        y[:300],
        exponential=True,
        damped_trend=True,
        initialization_method="estimated",
    ).fit(smoothing_level=0.8, smoothing_trend=0.4)

def ts_to_str(timestamp):
    # 获取时间戳位数
    ts_len = len(str(timestamp))
    if ts_len == 10:
        return time.strftime(DATE_TIME_FORMAT,time.localtime(timestamp))
    elif ts_len == 13:
        return time.strftime(DATE_TIME_FORMAT,time.localtime(int(timestamp/1000)))
    else:
        raise HTTPException(status_code=422, detail="时间戳不满足要求，请输入10或13位整数")

def get_iotdb_df(sql):
    iotdb_session = get_iotdb()
    with iotdb_session.execute_query_statement(sql) as result:
        df = result.todf()
    iotdb_session.close()
    return df

@app.post('/predict', tags=["predictions"], response_model=ModelOuput, status_code=200)
async def get_prediction(modelInput: ModelInput):
    '''
    根据历史数据进行预测，每2分钟计算一次
    输入参数：当前值和时间戳，与模型预测值进行比较
    输出结果：预测值，当前值和预测值的差值，相似度
    '''
    # 获取接口数据
    logger.info(f"model input: {modelInput}")
    real = modelInput.real
    timestamp = modelInput.time
    paramcode = modelInput.paramcode

    # 获取历史数据
    sql = sql_template.substitute(paramcode=paramcode, starttime=timestamp - DAY_TIMESTAMP, currenttime=timestamp)
    df = get_iotdb_df(sql)
    
    print(sql)
    data = df[df[DEVICE_NAME + '.' + paramcode] > 0][DEVICE_NAME + '.' + paramcode]
    ind = data.index
    print(data[0])
    # df = health_indicator(data,use_filter=True)
    x = np.array(ind)
    y = np.array(data)

    y = array_zero_replace_after(y)
    fit_model = Holt(
        y,
        exponential=True,
        damped_trend=True,
        initialization_method="estimated",
    ).fit(smoothing_level=0.8, smoothing_trend=0.4)
    
    # 使用模型预测
    predict = fit_model.forecast(1)[0]
    # 计算结果
    error = abs(real - predict)
    similarity = 1 - error/real
    # 更新df数据集
    # index = df[df.time == timestamp].index.tolist()[0]
    # df.loc[index, ['predict', 'error', 'similarity']] = [predict, error, similarity]

    print(df.tail(10))
    # app.df = df

    # 返回结果
    return { 'time': timestamp,
             'paramcode': paramcode,
             'real': real,
             'predict': predict,
             'error': error,
             'similarity': similarity,
    }


@app.post('/corrAnalysis', tags=["statistical analysis"])
async def get_corr(session: Session = Depends(get_db)):
    # # 获取接口数据
    # params_list = get_all_params(session)
    # # 获取设备属性表中的所有列名
    # rowName = []
    # for param in params_list:
    #     rowName.append(param.param_name)
    
    # 获取历史数据
    paramcode = ','.join(rowCode)
    curr_dt = datetime.now()
    timestamp = int(round(curr_dt.timestamp() * 1000))
    sql = sql_template.substitute(paramcode=paramcode, starttime=timestamp - DAY_TIMESTAMP, currenttime=timestamp)
    df = get_iotdb_df(sql)

    df['Time'] = df['Time'].map(lambda x: int(x/1000))
    df = df.groupby('Time').first().reset_index()
    df_columns = rowName.copy()
    df_columns.insert(0, 'Time')
    df.columns = df_columns

    # 计算相关性分析
    corr_df = df.drop(labels='Time', axis=1).corr(numeric_only=True)
    
    # 输出相关系数矩阵
    data_copy = corr_df.values
    corrs_matrix = []
    for corr in data_copy:
        corrs_matrix.append(corr.tolist())
    
    positive_correlation = []
    negative_correlation = []
    for row in rowName:
        positive_corr = corr_df[[row]].sort_values(by=row, ascending=False)
        negative_corr = corr_df[[row]].sort_values(by=row, ascending=True)

        positive_corr = positive_corr[positive_corr > 0.0].dropna(axis=0, how='all')
        positive_corr_dict = positive_corr.to_dict().get(row)
        positive_correlation.append(positive_corr_dict)

        negative_corr = negative_corr[negative_corr < 0.0].dropna(axis=0, how='all')
        negative_corr_dict = negative_corr.to_dict().get(row)
        negative_correlation.append(negative_corr_dict)

    keys = [str(x) for x in np.arange(1, len(positive_correlation) + 1)]

    return {
        "rowsName": rowName,
        "corrsMatrix": corrs_matrix,
        "positiveCorrelation": dict(zip(keys, positive_correlation)),
        "negativeCorrelation": dict(zip(keys, negative_correlation))
    }

