import numpy
import numpy as np
import csv
#import matplotlib.pyplot as plt


data = np.loadtxt('./M15.csv', delimiter=',', encoding = "Latin-1" ,dtype=str)
#x_data = data[24521:24524,7:11]
#y_data = data[24521:24524,6]

x_data = data[1:38489,7:153]
y_data = data[1:38489,6]


x_data = x_data.astype('float64')
y_data = y_data.astype('float64')
#转换为浮点数

learning_rate = 0.01
#学习率
b = 0
k = 0
n_iterables = 3000
#初始b、k和迭代次数
def compute_mse(b, k, x_data,y_data):
    total_error = 0
    for i in range(len(x_data)):
        total_error += (y_data[i] - (k * x_data[i] + b))

    mse_ = total_error / len(x_data) / 2
    return mse_

def gradient_descent(x_data, y_data, b,  k,  learning_rate,  n_iterables):
    m = len(x_data)
    # 迭代
    for i in range(n_iterables):
        # 初始化b、k的偏导
        b_grad = 0
        k_grad = 0

        # 遍历m次
        for j in range(m):
            # 对b,k求偏导
            b_grad += (1 / m) * ((k * x_data[j] + b) - y_data[j])
            k_grad += (1 / m) * ((k * x_data[j] + b) - y_data[j]) * x_data[j]

        # 更新 b 和 k  减去偏导乘以学习率
        b = b - (learning_rate * b_grad)
        k = k - (learning_rate * k_grad)
        # 每迭代 5 次  输出一次图形
        #if i % 5 == 0:
            #print(f"当前第{i}次迭代")
            #print("b_gard：", b_grad, "k_gard：", k_grad)
            #print("b：", b, "k：", k)
           
    return b, k

print(f"开始：截距b={b},斜率k={k}，损失={compute_mse(b,k,x_data,y_data)}")
print("开始迭代")
b, k = gradient_descent(x_data, y_data, b, k, learning_rate, n_iterables)
print(f"迭代{n_iterables}次后：截距b={b},斜率k={k}，损失={compute_mse(b,k,x_data,y_data)}")
