import json

tweets = []
with open('reply.json', 'r') as file:
    # check json format for each line, if not correct, print the line number
    for i, line in enumerate(file):
        try:
            tweets.append(json.loads(line))
        except json.decoder.JSONDecodeError:
            print(i)
            print(line)
            break
