import pandas as pd
import time
from tqdm import tqdm
import os

def operate1(data):
    '''
    筛选留下“FCU送VCU心跳”连续变化
    （连续变化是指相邻60行内有变化，若大于60行无变化，
    则只保留第1行数据）的数据
    '''
    data['diff'] = data["FCU送VCU心跳"].diff()
    starttime = time.time()
    for i in range(len(data)):
        data_i = data.iloc[i:i+60,:]
        if len(data_i) == 0:
            print('break1')
            break
        if data_i["FCU送VCU心跳"].nunique()==1:
            data_i_ = data.iloc[i+1:, :]
            data_i_same = data_i_[data_i_['diff'].map(lambda x:x!=0)]
            if len(data_i_same) == 0:
                data.drop(data.index[i+1:],inplace=True)
                print('break2')
                break
            data_i_index_end = data_i_same.index[0]
            data.drop(index = range(data_i_.index[0], data_i_index_end),inplace=True)
    endtime = time.time()
    print('operate1-运行的时间为:{}secs'.format(round(endtime - starttime, 2)))
    return data

def operate2(data):
    '''
    在上一步基础上，
    筛选留下“最高警告等级”为1或0的数据
    
     '''
    data = data.loc[(data['最高警告等级']==1) | (data['最高警告等级']==0),:]
    return data 

def operate3(data):
    '''
    在上一步基础上，
    筛选留下“电气路设定1（自变量）”为192的数据
    '''
    data = data.loc[data['电气路设定1（自变量）']==192]
    return data 

def operate4(data,length):
    """
    在上一步基础上，
    筛选留下连续（连续是指该组数据内没有任何一行被筛除）大于600行的数据为一组
    """
    group_list = []
    index_list = data.index
    block_list = []
    for x in index_list:
        block_list.append(x)
        if x+1 not in index_list:
            if len(block_list)>length:
                group_list.append(data.loc[block_list[0]:block_list[-1]+1,:])
            block_list = []
    return group_list

def operate5(data):
    '''
    在上一步基础上，筛选留下同时满足
    74.5<“冷却路反馈3”<77.5与74.5<“冷却路反馈5”<77.5的数据
    '''
    block_list = []
    for block in data:
        block1 = block[((74.5<block['冷却路反馈3']) & (block['冷却路反馈3']<77.5)) 
                       & 
                       ((74.5<block['冷却路反馈5']) & (block['冷却路反馈5']<77.5)) 
                      ]
        block_list.append(block1)
    return block_list

def operate6(data):
    '''
    在上一步基础上，
    筛除每组数据的前180行数据
    '''
    block_list = []
    for block in data:
        block1 = block.drop(block.index[0:180])
        block_list.append(block1)
    return block_list

def operate7(data):
    '''
    在上一步基础上，
    将每组数据按照式（1）进行计算，
    求取“电堆性能值”。
    '''
    block_list = []
    for block in data:
        m = block['系统性能均值'].mean()
        block_list.append({
            'data':block,
            'v_mean':m
        })
    return block_list

def data_create(path, filepackage_list):
    """_summary_

    Args:
        path (str): Mxx系统文件夹所在路径
        filepackage_list (list): 系统名列表

    Returns:
        dict: 包含多个系统的每组稳态数据以及每组的【系统性能均值】
    """
    dict1 = {}
    for package in tqdm(filepackage_list):
        print(f'系统 {package} 运行')
        dict1[package] = []
        sys_list = []
        for file in os.listdir(os.path.join(path,package)):
            print(f'读取文件：{os.path.join(os.path.join(path,package,file))}')
            current_file = os.path.join(os.path.join(path,package,file))
            data = pd.read_csv(current_file)
            sys_list.append(data)
        data = pd.concat(sys_list)        
        data.index = range(len(data))
        # return data
        data_ = data
        data_operate1 = operate1(data_)
        data_operate2 = operate2(data_operate1)
        data_operate3 = operate3(data_operate2)
        group_list = operate4(data_operate3,600)
        data_operate5 = operate5(group_list)
        data_operate6 = operate6(data_operate5)
        data_operate7 = operate7(data_operate6)
        for block in data_operate7:
            if len(block['data'])>0:
                dict1[package].append(block)
    return dict1

if __name__ == "__main__":
    """调用示例"""
    """上述调用示例运行较为缓慢，选手可进行优化加速"""
    path = './data/'
    file_test = data_create(path, ['M1', 'M2', 'M3', 'M4', 'M5', 'M6', 'M7'])
    # file_test 为一字典，其中包含索要处理系统，keys：'M1', 'M2', 'M3', 'M4', 'M5', 'M6', 'M7'
    # file_test['M1]为一列表，其中包含n组稳态过程的数据
    # file_test['M1][0]为一dict，表示M1系统第一组稳态，keys：'data', 'v_mean'。其中，data为对应数据，v_mean为该组系统性能均值。
    # 每组v_mean，对应给出的训练集答案