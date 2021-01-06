#!/usr/bin/python3

'''
This telegram bot can be used as an interface to get data from sensors
of 6 tanks which have a level control system
Also, it can update the control parameters and the sepoint level for each plant

Author: David Adrián Rodríguez García
'''

from telegram.ext import Updater, CommandHandler
import logging
import paho.mqtt.client as mqtt
import yaml
import time

#Firstly, read the configuration.yaml document
with open("configuration.yaml", "r") as ymlfile:
    cfg = yaml.load(ymlfile,  Loader=yaml.FullLoader)

#Create an instance for your telegram bot
updater = Updater(token=cfg["telegram"]["token"], use_context=True)
dispatcher = updater.dispatcher

#Setting up the logging module
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)

#Storing topics into a dictionary
topics_dict = cfg["topics"]

#Subscribing Function for all the plants
def suscriber_function(topic_type,client):   
    for topic in topics_dict[topic_type].values():
        client.subscribe(topic)

#Defining start function
def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot which will help you to control the level of your tanks")
    #Setting up MQTT Connection
    try:
        global client
        client = mqtt.Client("telegram-bot")
        client.connect(cfg["mqtt"]["broker"],cfg["mqtt"]["port"])
        context.bot.send_message(chat_id=update.effective_chat.id, text="I'm connected to the mqtt broker")
    except:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I could not connect to the mqtt broker")
    
    #Subscribing respective topics
    suscriber_function("data",client)
    suscriber_function("params",client)
    
    #Setting up the callback function to the client  
    client.on_message = on_message

    #Starting to listen from the broker
    client.loop_start()


#Defining callback function
def on_message(client, userdata, message):

    if message.topic == topics_dict["data"]["plant1"]:
        global plant1_data
        plant1_data = message.payload.decode("utf-8").split(";")

    if message.topic == topics_dict["data"]["plant2"]:
        global plant2_data
        plant2_data = message.payload.decode("utf-8").split(";")
    
    if message.topic == topics_dict["data"]["plant3"]:
        global plant3_data
        plant3_data = message.payload.decode("utf-8").split(";")

    if message.topic == topics_dict["data"]["plant4"]:
        global plant4_data
        plant4_data = message.payload.decode("utf-8").split(";")

    if message.topic == topics_dict["data"]["plant5"]:
        global plant5_data
        plant5_data = message.payload.decode("utf-8").split(";")

    if message.topic == topics_dict["data"]["plant6"]:
        global plant6_data
        plant6_data = message.payload.decode("utf-8").split(";")
    
    if message.topic == topics_dict["params"]["plant1"]:
        global plant1_params
        plant1_params = message.payload.decode("utf-8").split(";")

    if message.topic == topics_dict["params"]["plant2"]:
        global plant2_params
        plant2_params = message.payload.decode("utf-8").split(";")
    
    if message.topic == topics_dict["params"]["plant3"]:
        global plant3_params
        plant3_params = message.payload.decode("utf-8").split(";")

    if message.topic == topics_dict["params"]["plant4"]:
        global plant4_params
        plant4_params = message.payload.decode("utf-8").split(";")

    if message.topic == topics_dict["params"]["plant5"]:
        global plant5_params
        plant5_params = message.payload.decode("utf-8").split(";")

    if message.topic == topics_dict["params"]["plant6"]:
        global plant6_params
        plant6_params = message.payload.decode("utf-8").split(";")

#Defining command to update the parameters
def update_parameters(update, context):
    try:
        new_params = list(map(str,context.args))
        context.bot.send_message(chat_id=update.effective_chat.id, text="Updating parameters to plant " + new_params[0] +
                                                                        ":\nSP: " + new_params[1] +
                                                                        "\nKp: " + new_params[2] +
                                                                        "\nTi: " + new_params[3] +
                                                                        "\nTd: " + new_params[4])
        #Parsing to string for the mqtt payload
        plant = new_params.pop(0)
        payload = new_params.pop(0)
        for msg_unit in new_params:
            payload = payload + ";" + msg_unit
        #Publishing new parameters to the plant
        try:
            client.publish(topics_dict["update"]["plant"+plant],payload)
        except:
            context.bot.send_message(chat_id=update.effective_chat.id, text="Not connected to the broker, please run start command")
    except:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Wrong command, please try again")

#Defining command to update the setpoint
def update_setpoint(update, context):
    try:
        new_setpoint = list(map(str,context.args))
        context.bot.send_message(chat_id=update.effective_chat.id, text="Updating setpoint to plant " + new_setpoint[0] +
                                                                        ":\nSP: " + new_setpoint[1])
        #Parsing to string for the mqtt payload
        plant = new_setpoint.pop(0)
        payload = new_setpoint.pop(0)
        for msg_unit in (-1,-1,-1):
            payload = payload + ";" + str(msg_unit)
        #Publishing new setpoint to the plant
        try:
            client.publish(topics_dict["update"]["plant"+plant],payload)
        except:
            context.bot.send_message(chat_id=update.effective_chat.id, text="Not connected to the broker, please run start command")
    except:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Wrong command, please try again")

#Defining command to switch on the plant
def switch_on(update, context):
    try:
        plant = str(context.args[0])
        context.bot.send_message(chat_id=update.effective_chat.id, text="Switching on plant " + plant)
        #Publishing new on_off value to the plant
        try:
            client.publish(topics_dict["update"]["plant"+plant],1)
        except:
            context.bot.send_message(chat_id=update.effective_chat.id, text="Not connected to the broker, please run start command")
    except:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Wrong command, please try again")

#Defining command to switch off the plant
def switch_off(update, context):
    try:
        plant = str(context.args[0])
        context.bot.send_message(chat_id=update.effective_chat.id, text="Switching off plant " + plant)
        #Publishing new on_off value to the plant
        try:
            client.publish(topics_dict["update"]["plant"+plant],0)
        except:
            context.bot.send_message(chat_id=update.effective_chat.id, text="Not connected to the broker, please run start command")
    except:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Wrong command, please try again")

#Defining command to show data from the plant
def get_data(update, context):
    try:
        plant = int(context.args[0])

        if plant == 1:
            data = plant1_data
        if plant == 2:
            data = plant2_data
        if plant == 3:
            data = plant3_data
        if plant == 4:
            data = plant4_data
        if plant == 5:
            data = plant5_data
        if plant == 6:
            data = plant6_data
        
        context.bot.send_message(chat_id=update.effective_chat.id, text="Data values from plant " + str(plant) +
                                                                        ":\nSP: " + data[0] +
                                                                        "\nPV: " + data[1] +
                                                                        "\nCP: " + data[2] +
                                                                        "\nTime: " + data[3])
    except:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Wrong command, please try again")

#Defining command to show parameters from the plant
def get_parameters(update, context):
    try:
        plant = int(context.args[0])
        
        try:
            client.publish(topics_dict["get_params"]["plant"+str(plant)],"")
            time.sleep(0.5)
        except:
           context.bot.send_message(chat_id=update.effective_chat.id, text="Not connected to the broker, please run start command")
        
        if plant == 1:
            params = plant1_params
        if plant == 2:
            params = plant2_params
        if plant == 3:
            params = plant3_params
        if plant == 4:
            params = plant4_params
        if plant == 5:
            params = plant5_params
        if plant == 6:
            params = plant6_params
        if params[4] == "0":
            state = "OFF"
        elif params[4] == "1":
            state = "ON"
        
        context.bot.send_message(chat_id=update.effective_chat.id, text="Parameters values from plant " + str(plant) +
                                                                        ":\nSP: " + params[0] +
                                                                        "\nKp: " + params[1] +
                                                                        "\nTi: " + params[2] +
                                                                        "\nTd: " + params[3] +
                                                                        "\nState: " + state)
    except:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Wrong command, please try again")

#Setting up the previous functions to the respective commands
start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

update_parameters_handler = CommandHandler('update_params', update_parameters)
dispatcher.add_handler(update_parameters_handler)

update_setpoint_handler = CommandHandler('update_setpoint', update_setpoint)
dispatcher.add_handler(update_setpoint_handler)

switch_on_handler = CommandHandler('switch_on', switch_on)
dispatcher.add_handler(switch_on_handler)

switch_off_handler = CommandHandler('switch_off', switch_off)
dispatcher.add_handler(switch_off_handler)

get_data_handler = CommandHandler('get_data', get_data)
dispatcher.add_handler(get_data_handler)

get_params_handler = CommandHandler('get_params', get_parameters)
dispatcher.add_handler(get_params_handler)

#Starting the loop for the bot
updater.start_polling()
