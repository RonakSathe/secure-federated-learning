import random
def label_data(data):
    cpu,memory,connections,bytes_sent,bytes_received = data

    score = 0
    if cpu > 50: score += 1
    if memory > 65: score += 1
    if connections > 20: score += 1
    if bytes_sent > 100000: score += 1
    if bytes_received > 100000: score += 1

    #FOrcing randomness
    if random.random() < 0.3:
        return 1

    return 1 if score >= 2 else 0