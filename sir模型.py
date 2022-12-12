import scipy.integrate as spi
import numpy as np
import pylab as pl


"""
S：Susceptibles 易感人群，未得病者  初始占人群绝大部分比例
R：Recovereds 恢复人群，感染者得病后恢复，此后不再参与感染和被感染过程  初始为0
I：Infectious 患病人群  初始占人群很小比例

beta：感染人群接触对未感染人群的传播率
gamma: 恢复率，感染人群恢复成为移除人群率

ND：时间长度
TS：时间间隔
"""

beta = 0.7000  # 感染参数
gamma = 0.14286  # 康复参数


TS = 1.0  # 时间间隔
ND = 40.0  # 时间长度
S0 = 1 - 1e-6  # 未感染着
I0 = 1e-6  # 感染者比例
INPUT = (S0, I0, 0.0)


def diff_eqs(INP, t):
    '''The main set of equations'''
    Y = np.zeros((3))
    V = INP
    Y[0] = - beta * V[0] * V[1]
    Y[1] = beta * V[0] * V[1] - gamma * V[1]
    Y[2] = gamma * V[1]
    return Y  # For odeint


t_start = 0.0
t_end = ND
t_inc = TS
t_range = np.arange(t_start, t_end + t_inc, t_inc)
RES = spi.odeint(diff_eqs, INPUT, t_range)

print(RES)

# 画图
pl.subplot(111)
pl.plot(RES[:, 1], '-r', label='Infectious')
pl.plot(RES[:, 0], '-g', label='Susceptibles')
pl.plot(RES[:, 2], '-k', label='Recovereds')
pl.legend(loc=0)
pl.title('SIR_Model.py')
pl.xlabel('Time')
pl.ylabel('Infectious Susceptibles and Recovereds')
pl.xlabel('Time')
pl.show()
