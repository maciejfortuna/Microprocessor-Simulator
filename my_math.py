def clip(val, start,end):
    if val <= start:
        return start
    if val >= end:
        return end
    return val
