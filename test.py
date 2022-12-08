L = ["1", "2", "3"]
res = [""]
for e in L:
    res += [sub + e for sub in res]
print(res)