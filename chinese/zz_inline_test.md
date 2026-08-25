# 行内公式渲染测试 Round 2

## Tight inside + space outside (candidate fix form)

V12: 参数 $\phi$ 拟合模型

V13: 损失函数 $L[\phi]$ 的最小值

V14: $ \phi $ ascii-spaces-outside-tight-inside-check: a$\phi$b

V15: a $\phi$ b

## One-sided CJK adjacency

V16: 中文在前$\phi$后跟空格

V17: 空格在前 $\phi$中文在后

## Braces tight

V18: 训练集 $\{\mathbf x_{i}, \mathbf y_{i}\}$ 作为输入

V19: 模型 $\mathbf f [\mathbf x, \phi]$ 拟合

## Multiple formulas one line, tight inside

V20: 用参数 $\phi$ 去拟合模型 $\mathbf f [\mathbf x, \phi]$，从而找到损失函数 $L[\phi]$
