array = [(0,10),(10,40),(40,10040),(10040,10640)]
def binary_search(target,array):
    first = 0
    last = len(array) - 1
    while first<=last:
        mid = (first+last)//2
        if target>= array[mid][0] and target<= array[mid][1]:
            return mid
        else:
            if array[mid][1] < target:
                first = mid + 1
            else:
                last = mid - 1    

print(binary_search(10020,array))