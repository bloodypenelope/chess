q = input()
a, b, c, d = map(int, q.split())

diff = d - b
result = a
if diff > 0:
    result += c * diff
print(result)
