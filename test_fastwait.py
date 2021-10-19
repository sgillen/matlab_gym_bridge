import fastwait
f = open("test.txt", "w+")
fastwait.fastwait(f.fileno())
