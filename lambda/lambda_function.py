variable_name = "Ultron"

#06/08/2023

from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_core.dispatch_components import (AbstractRequestHandler, AbstractExceptionHandler, AbstractRequestInterceptor, AbstractResponseInterceptor)
from ask_sdk_core.skill_builder import SkillBuilder
from airtable import Airtable
import datetime


import logging
import json
import random
import requests

#import logging
import ask_sdk_core.utils as ask_utils
import openai
#from ask_sdk_core.skill_builder import SkillBuilder
#from ask_sdk_core.dispatch_components import AbstractRequestHandler
#from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response

# Set your OpenAI API key
openai.api_key = "sk-xx"

base_id = 'appk2ub46EnjAAKyi'
table_name = 'demo'
api_key = 'keyo74XaqLuKh1QXO'

table = Airtable(base_id, table_name, api_key)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class LaunchRequestHandler(AbstractRequestHandler):
    
    def can_handle(self, handler_input):
        return is_request_type("LaunchRequest")(handler_input)
    
    def handle(self, handler_input):
        language_prompts = handler_input.attributes_manager.request_attributes["_"]
        skill_name = language_prompts["SKILL_NAME"]
        
        speech_output = random.choice(language_prompts['WELCOME']).format(skill_name)
        reprompt = random.choice(language_prompts['WELCOME_REPROMPT'])
        
        return (
            handler_input.response_builder
                .speak(speech_output)
                .ask(reprompt)
                .response
            )

class GetchoixIntentHandler(AbstractRequestHandler):
    
    def can_handle(self, handler_input):
        return is_intent_name("GetchoixIntent")(handler_input)
    
    def handle(self, handler_input):
        language_prompts = handler_input.attributes_manager.request_attributes["_"]
        
        try :
            choix_use = handler_input.request_envelope.request.intent.slots["choix"].value
            search_record = table.match('choix', choix_use)
            entree_use = search_record['fields']['entrée']
            plat_use = search_record['fields']['plat']
            dessert_use = search_record['fields']['dessert']
            speech_output = random.choice(language_prompts['GET_choix_CONFIRMED']).format(choix_use, entree_use, plat_use, dessert_use)
            reprompt = random.choice(language_prompts['GET_choix_REPROMPT_CONFIRMED'])
            
        except:
            speech_output = random.choice(language_prompts['GET_choix_UNCONFIRMED'])
            reprompt = random.choice(language_prompts['GET_choix_REPROMPT_UNCONFIRMED'])
        
        return (
            handler_input.response_builder
                .speak(speech_output)
                .ask(reprompt)
                .response
            )
class GptQueryIntentHandler(AbstractRequestHandler):
    """Handler for Gpt Query Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("GptQueryIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        query = handler_input.request_envelope.request.intent.slots["query"].value
        response = generate_gpt_response(query, handler_input)

        return (
                handler_input.response_builder
                    .speak(response)
                    .ask("pas d'autres questions?")
                    .response
            )

class CancelOrStopIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return (is_intent_name("AMAZON.CancelIntent")(handler_input) or
                is_intent_name("AMAZON.StopIntent")(handler_input))
    
    def handle(self, handler_input):
        language_prompts = handler_input.attributes_manager.request_attributes["_"]
        speech_output = random.choice(language_prompts["CANCEL_STOP_RESPONSE"])
    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Fin du Chat G.P.T. mode"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )

def generate_gpt_response(query, handler_input):
    try:
        #messages = [{"role": "system", "content": "You are a helpful assistant."},
        #messages = [{"role": "system", "content": "Imagine that you are " + variable_name + " and answer my question in a short and concise manner."},
        messages = [{"role": "system", "content": "Imagine que tu es " + variable_name + " et et répond moi de façon coutre et concise."},
                    {"role": "user", "content": query}]
        # Get the previous conversation history from the Alexa session
        session_attributes = handler_input.attributes_manager.session_attributes
        if "conversation_history" in session_attributes:
            messages += session_attributes["conversation_history"]
        messages.append({"role": "user", "content": query})
        # Update the conversation history in the Alexa session
        session_attributes["conversation_history"] = messages
        # Generate a response using the OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=100,
            n=1,
            stop=None,
            temperature=0.5
        )
        # Return the response
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"Error generating response: {str(e)}"
    return (
            handler_input.response_builder
                .speak(speech_output)
                .set_should_end_session(True)
                .response
            )

class HelpIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.HelpIntent")(handler_input)
    
    def handle(self, handler_input):
        language_prompts = handler_input.attributes_manager.request_attributes["_"]
        speech_output = random.choice(language_prompts["HELP"])
        reprompt = random.choice(language_prompts["HELP_REPROMPT"])
        
        return (
            handler_input.response_builder
                .speak(speech_output)
                .ask(reprompt)
                .response
            )

class FallbackIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.FallbackIntent")(handler_input)
    
    def handle(self, handler_input):
        language_prompts = handler_input.attributes_manager.request_attributes["_"]
        speech_output = random.choice(language_prompts["FALLBACK"])
        reprompt = random.choice(language_prompts["FALLBACK_REPROMPT"])
        
        return (
            handler_input.response_builder
                .speak(speech_output)
                .ask(reprompt)
                .response
            )

class SessionEndedRequesthandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_request_type("SessionEndedRequest")(handler_input)
    
    def handle(self, handler_input):
        logger.info("Session ended with the reason: {}".format(handler_input.request_envelope.request.reason))
        return handler_input.response_builder.response

class CatchAllExceptionHandler(AbstractExceptionHandler):
    
    def can_handle(self, handler_input, exception):
        return True
    
    def handle(self, handler_input, exception):
        logger.error(exception, exc_info=True)
        
        language_prompts = handler_input.attributes_manager.request_attributes["_"]
        
        speech_output = language_prompts["ERROR"]
        reprompt = language_prompts["ERROR_REPROMPT"]
        
        return (
            handler_input.response_builder
                .speak(speech_output)
                .ask(reprompt)
                .response
            )

class RequestLogger(AbstractRequestInterceptor):

    def process(self, handler_input):
        logger.debug("Alexa Request: {}".format(
            handler_input.request_envelope.request))

class ResponseLogger(AbstractResponseInterceptor):

    def process(self, handler_input, response):
        logger.debug("Alexa Response: {}".format(response))

class LocalizationInterceptor(AbstractRequestInterceptor):

    def process(self, handler_input):
        locale = handler_input.request_envelope.request.locale
        logger.info("Locale is {}".format(locale))
        
        try:
            with open("languages/"+str(locale)+".json") as language_data:
                language_prompts = json.load(language_data)
        except:
            with open("languages/"+ str(locale[:2]) +".json") as language_data:
                language_prompts = json.load(language_data)
        
        handler_input.attributes_manager.request_attributes["_"] = language_prompts

sb = SkillBuilder()
sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(GetchoixIntentHandler())
sb.add_request_handler(GptQueryIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequesthandler())

sb.add_exception_handler(CatchAllExceptionHandler())

sb.add_global_request_interceptor(LocalizationInterceptor())
sb.add_global_request_interceptor(RequestLogger())
sb.add_global_response_interceptor(ResponseLogger())

lambda_handler = sb.lambda_handler()