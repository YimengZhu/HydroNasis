import pandas as pd
import time
from tqdm import tqdm
import os

def operate1(data):
    data_diff = data["FCU送VCU心跳"].diff().astype('float32')
    i, j = 0, 0
    max_idx = data.shape[0]

    while j < max_idx:
        if data_diff.iloc[j] == 0:
            j += 1
            continue

        if j - i >= 60:
            data.drop(index = range(i + 1, j+1),inplace=True)
        
        i, j =  j + 1, j + 1

    if j > i:
        data.drop(data.index[i+1:],inplace=True)
    endtime = time.time()
    return data

def operate1(data):
    data_diff = data["FCU送VCU心跳"].diff().ne(0).cumsum()

    s = []
    g = data.index.to_series().groupby(data_diff, sort=False)
    for group in g.groups.values():
        if len(group) >= 60:
            s.append(group[0])
        else:
            s.extend(group)
    return data.loc[s]

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
    index_list = data.index
    data['block']=0
    block_list = []
    i=1
    for x in index_list:
        block_list.append(x)
        if x+1 not in index_list:
            if len(block_list)>length:
                data.loc[block_list[0]:block_list[-1]+1,"block"] = i
            block_list=[]
        i=i+1
    data = data[data['block']!=0]
    return data

def operate5(data):
    '''
    在上一步基础上，筛选留下同时满足
    74.5<“冷却路反馈3”<77.5与74.5<“冷却路反馈5”<77.5的数据
    '''
    data = data[(data['冷却路反馈3']>74.5)&(data['冷却路反馈3']<77.5)&(data['冷却路反馈5']>74.5)&(data['冷却路反馈5']<77.5)]
    return data

def operate6(data):
    '''
    在上一步基础上，
    筛除每组数据的前180行数据
    '''
    data['rank']=1
    data['rank'] = data.groupby('block')['rank'].rank(method='first')
    data = data[data['rank']>180]

    return data

def operate7(data):
    '''
    在上一步基础上，
    将每组数据按照式（1）进行计算，
    求取“电堆性能值”。
    '''
    block_list = []
    for _, block in data.iterrows():
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
        for file in sorted(os.listdir(os.path.join(path,package))):
            print(f'读取文件：{os.path.join(os.path.join(path,package,file))}')
            current_file = os.path.join(os.path.join(path,package,file))
            data = pd.read_csv(current_file)
            sys_list.append(data)
        data = pd.concat(sys_list).reset_index()

        data = operate1(data)
        data = operate2(data)
        data = operate3(data)
        data = operate4(data,600)
        data = operate5(data)
        data = operate6(data)

    return data

if __name__ == "__main__":
    """调用示例"""
    """上述调用示例运行较为缓慢，选手可进行优化加速"""

    des_path = '/home/yimeng/data/HydroNasis/train/processed'
    if not os.path.exists(des_path):
        os.makedirs(des_path)

    path = '/home/yimeng/data/HydroNasis/train/'
    file_list = ['M2', 'M3', 'M4', 'M5', 'M6', 'M7']
    row_count_list = []

    for f in file_list:
        file_test = data_create(path, [f])
        file_test = file_test.reset_index()
        file_test.to_csv(f'{des_path}/{f}.csv', index=False)

        row_count = file_test.shape[0]
        print(f'{row_count} rows in f')
        row_count_list.append(row_count)
    
    row_sum = sum(row_count_list)
    print(f'totally {row_sum} rows generated.')


