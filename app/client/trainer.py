def label_data(data):
    cpu,memory,connections,bytes_sent,bytes_received = data

    score = 0
    if cpu > 70: score += 1
    if memory > 75: score += 1
    if connections > 50: score += 1
    if bytes_sent > 500000: score += 1
    if bytes_received > 500000: score += 1

    return 1 if score >= 2 else 0