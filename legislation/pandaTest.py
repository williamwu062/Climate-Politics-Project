import pandas as pd

data = {'Name':['Tom', 'nick', 'krish', 'jack'],
        'Age':[20, 21, 19, 18]}

df = pd.DataFrame(data, index=['person id'])

data2 = {'Age':[12, 21, 19, 18], 'Name':['Joe', 'H', 'Rg', 'RGw']}
df2 = pd.DataFrame(data2)

# df = df.append(df2, ignore_index=True)
# print(df)
# df.to_csv('test.csv')
result = pd.concat([df, df2], ignore_index=True)
print(result)
result.to_csv('test.csv')