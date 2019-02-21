# -*- coding: utf-8 -*-
"""
Created on Thu Feb 21 10:07:28 2019

@author: sgiraldo
"""

from chatterbot.trainers import ListTrainer
from chatterbot import ChatBot
import logging 

logger = logging.getLogger() 
logger.setLevel(logging.CRITICAL)

bot = ChatBot('ChatWhats')


conv = ['oi','oi','tudo bem?','tudo e voce?', 'bem tb','que bom','qual seu nome?','meu nome é Bruno e o seu?','meu nome é Inteligencia Artifical']

trainer = ListTrainer(bot)

trainer.train(conv)

while True:
   quest = input('Voce: ')
   resposta = bot.get_response(quest)

   if float (resposta.confidence > 0.5):
       print('bot: ',resposta)
   else:
       print('bot: Nao entendi')