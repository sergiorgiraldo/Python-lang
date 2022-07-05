import twitter

api = twitter.Api(consumer_key='',
                      consumer_secret='',
                      access_token_key='',
                      access_token_secret='')

#todo: iteração
#todo: guardar último tweet lido
tweets = api.GetSearch(term='#PagSeguro')

print(tweets)
