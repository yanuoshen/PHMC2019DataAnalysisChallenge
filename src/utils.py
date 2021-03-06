import os
import numpy as np
import random
import pandas as pd
import datetime
import configparser
import json
import CONST
from _000_preprocess import _000_preprocess


def get_config_name():
    inifile = configparser.ConfigParser()
    inifile.read(os.path.join(os.path.dirname(__file__), 'conf.ini'))
    return os.path.basename(inifile['conf']['configfile']).split('.')[0]


def get_config():
    inifile = configparser.ConfigParser()
    inifile.read(os.path.join(os.path.dirname(__file__), 'conf.ini'))
    with open(os.path.join(os.path.dirname(__file__), inifile['conf']['configfile']), "r") as fp:
        conf = json.load(fp)
    return conf


def update_result(pred_function_name, score, std, output_file):
    config_name = get_config_name()
    dt_now = datetime.datetime.now().replace(microsecond=0).isoformat()

    new_row = pd.DataFrame([[config_name, pred_function_name, dt_now, score, std, output_file]],
                           columns=['config', 'pred_func_name', 'exec time', 'score', 'std',
                                    'output_file'])
    if os.path.exists(CONST.RESULT_SUMMARY):
        df = pd.read_csv(CONST.RESULT_SUMMARY)
    else:
        df = pd.DataFrame(columns=['config', 'pred_func_name', 'exec time', 'score', 'std', 'output_file'])

    df = pd.concat([df, new_row], axis=0).reset_index(drop=True)
    df.to_csv(CONST.RESULT_SUMMARY, index=False)
    print("=== Update result summary ==== ")
    print(df.tail())


def get_cv_id(seed=42):
    """訓練データのエンジンを寿命が長い順に並べ1-8のidを振っていく
    """
    random.seed(seed)
    trn_base_path, tst_base = _000_preprocess()
    trn = pd.read_feather(trn_base_path)
    nfold = get_config()['nfold']

    flight_max = trn.groupby('Engine').FlightNo.max().sort_values().to_frame('Life')
    remainder_list = list(range(1, len(flight_max) % nfold + 1))
    flight_max['cv_id'] = (
            random.sample(list(range(1, nfold + 1)), nfold) * (len(flight_max) // nfold) +
            random.sample(remainder_list, len(remainder_list)))
    flight_max.reset_index(inplace=True)

    return flight_max[['Engine', 'cv_id']]


if __name__ == '__main__':
    print(get_config_name())
    print(get_config())
    print(get_cv_id())
