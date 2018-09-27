import twitter

api = twitter.Api(consumer_key='hk6Ll5M1YSLebZQ2St83sw',
                      consumer_secret='f3uc8haXnIQ1kLHwpAXieBeEvw6e1i58hRg7jveeU',
                      access_token_key='8193352-59orz3jZGBnHgB5hQmEQA39nzeznrOrMopASVfgwN9',
                      access_token_secret='0Lmo8eUlR8yeQfdJKf1SM3uolKm1Y7Ez6LrdY56xS60G6')

#todo: iteração
#todo: guardar último tweet lido
tweets = api.GetSearch(term='#PagSeguro')

print(tweets)
