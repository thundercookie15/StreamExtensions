'''
This is the main file for the user interface.
'''
import os
import subprocess
import sys
import threading
from collections import deque
from functools import partial
from json import JSONDecodeError
from ssl import SSLContext, create_default_context, SSLSocket
from time import time, sleep

import PySimpleGUI as sg
import psutil
import pydirectinput
from irc.bot import SingleServerIRCBot
from irc.client import ServerConnection, ServerNotConnectedError, Event
from irc.connection import Factory
from jsonschema import ValidationError
from pyuac import main_requires_admin

from chatplays.streamchatwars._interfaces._chatbot import AbstractMessageSender
from chatplays.streamchatwars._interfaces._thread_support import AbstractThreadSupport
from chatplays.streamchatwars._shared.constants import RANDOM_ACTIONS_FILE, ACCEPT_INPUT_FILE, DEFAULT_CREDENTIAL_FILE, \
    CHECK_JOIN_INTERVAL
from chatplays.streamchatwars._shared.global_data import GlobalData
from chatplays.streamchatwars._shared.helpers_color import ColorText
from chatplays.streamchatwars._shared.helpers_print import thread_print_timestamped, thread_print
from chatplays.streamchatwars._shared.types import CredentialDict, TwitchChatCredentialDict, ConfigDict
from chatplays.streamchatwars.chat.chatbot import Custom_Reactor, StopBotException
from chatplays.streamchatwars.chat.chatmsg import ChatMessage
from chatplays.streamchatwars.config import json_utils
from chatplays.streamchatwars.config.config import read_json_configs, IRC_Settings, extract_irc_settings
from chatplays.streamchatwars.config.json_utils import InvalidCredentialsError
from chatplays.streamchatwars.events.events_states import GlobalEventStates
from userinterface import games, obsplugin

allowed_file_types = (("Image Files", "*.png"), ("Image Files", "*.jpg"), ("Image Files", "*.jpeg"),
                      ("Image Files", "*.webp"), ("Image Files", "*.gif"))

mods = ['thundercookie15', 'suitwo', 'reldeththesummoner', 'joshthecarrot', 'ssbcraft', 'lord_df_01', 'a_scarling',
        'bro0ns', 'meyvol', 'unfairballoon7', 'king_o_peace']

channels: set[str] = set()

channels.update(['#thundercookie15', '#nagzz21'])


@main_requires_admin
def main():
    check_directories()
    this = GUI()
    this.__init__()


def check_directories():
    if not os.path.exists('userinterface/images'):
        os.makedirs('userinterface/images')
    if not os.path.exists('userinterface/pokemon'):
        os.makedirs('userinterface/pokemon')
    if not os.path.exists('userinterface/SNES'):
        os.makedirs('userinterface/SNES')


def main_layout():
    return [
        [sg.Text('Stream Extensions Control', justification='center', font=("Helvetica", 30), size=(800, 1))],
        [sg.HSeparator()],
        # Selector for Chat Picks and Stream Chat Wars
        [sg.Column(layout=[
            [sg.Frame(title='Select which Control Panel to run', title_color='orange', relief=sg.RELIEF_SUNKEN,
                      element_justification='center', key='select_control_panel', vertical_alignment='center',
                      layout=[
                          [sg.Button('Chat Picks', font="Helvetica", key='chat_picks',
                                     button_color=('white', 'gold'),
                                     border_width=3),
                           sg.Button('Chat Plays', font="Helvetica", key='stream_chat_wars',
                                     button_color=('white', 'gold'),
                                     border_width=3)],
                          [sg.Button('Reset credentials', font="Helvetica", key='reset_credentials',
                                     button_color=('white', 'red'), border_width=3)],
                      ])],
            [sg.Button('Exit', font="Helvetica", key='Exit', button_color=('white', 'red'),
                       border_width=3)]
        ], justification='center', element_justification='center', vertical_alignment='center')],
    ]


def chat_picks_layout():
    return [
        [sg.Text('Chat Picks Control Panel', justification='center', font=("Helvetica", 30), size=(800, 1),
                 relief=sg.RELIEF_RIDGE, key='title', text_color='white', background_color='blue', border_width=3)],
        [sg.HSeparator()],
        # Chat Picks Control Panel Frame
        [sg.Column(layout=[
            [sg.Frame(title="Main Controls", layout=[
                [sg.Button('Start OBS Connection', font="Helvetica", key='start_webserver',
                           button_color=('white', 'green'), ),
                 sg.Button('Stop OBS Connection', font="Helvetica", key='stop_webserver',
                           button_color=('white', 'red'), )],
                # [sg.Button('TestButton', font="Helvetica", key='test_button', button_color=('white', 'green'), )],
            ], element_justification='center', title_location='n')],
            [sg.Column(layout=[
                [sg.Column(layout=[
                    [sg.Frame(title='OBS Setup', layout=setup_obs_inner_layout(),
                              element_justification='center', title_location='n')]], key='obs_setup', visible=False),
                    sg.Column(layout=[
                        [sg.Frame(title='Controls', layout=controls_layout(), element_justification='center',
                                  title_location='n')]], key='controls',
                        visible=False)],
            ])],
            [sg.Text(
                'Do not adjust the sources created by the program. They are used for the program to work and will not function properly without them.'
                '\nYou can change the position of the sources in OBS but don\'t change the name or properties of the sources.',
                text_color='red', font=("Helvetica", 8), justification='center')],
            [sg.HSeparator()],
            [sg.Button('Main Menu', font="Helvetica", key='Main_Menu', button_color=('white', 'red'),
                       border_width=3), ]
        ], justification='center', element_justification='center', vertical_alignment='center')],
    ]


def setup_obs_inner_layout():
    return [
        [sg.Text('Select OBS Scene: ', font=("Helvatica", 15)),
         sg.Combo(default_value='none', key='selected_scene',
                  font=("Helvetica", 12), size=(18, 1), values=[])],
        [sg.Text('Twitch Username:', font=("Helvetica", 15)),
         sg.Input(key='streamer_name', font=("Helvetica", 12), size=(18, 1), )],
        [sg.Button('Setup OBS', font="Helvetica", key='setup_obs', button_color=('white', 'green'), )],
    ]


def controls_layout():
    return [
        [sg.Text('Scene with Setup: ', font=("Helvatica", 15), key='scene_with_setup'),
         sg.Text('None', key='scene_setup', font=("Helvatica", 15), text_color='red'),
         sg.Button('Go to Scene', font="Helvetica", key='go_to_scene', button_color=('white', 'green'), )],
        [sg.Text('Current Scene:', font=("Helvatica", 15), key='current_scene'),
         sg.Text('None', key='scene_text', font=("Helvatica", 15), text_color='red'), ],
        [sg.Frame(title='Image Controls', layout=[
            [sg.Button('Show Image', font="Helvetica", key='set_visible', button_color=('white', 'green'), ),
             sg.Button('Hide Image', font="Helvetica", key='set_invisible', button_color=('white', 'red'), )],
            [sg.Text('Enter image URL: '),
             sg.InputText(key='-FILEIN-', size=(20, 1)), ],
            [sg.Button('Upload', key='upload_image'),
             sg.Button('Clear Image', key='clear_image', button_color=('white', 'red'), )],
        ], element_justification='center', title_location='n')],
        [sg.Frame(title='Poll Controls', layout=[
            [sg.Text('Poll Status: ', font=("Helvatica", 15), key='poll_status'),
             sg.Text('', key='poll_status_text', )],
            [sg.Button('Enable Poll', font="Helvetica", key='enable_poll', button_color=('white', 'green'), ),
             sg.Button('Disable Poll', font="Helvetica", key='disable_poll', button_color=('white', 'red'), )],
            [sg.Button('Show Poll', font="Helvetica", key='show_poll', button_color=('white', 'green'), ),
             sg.Button('Hide Poll', font="Helvetica", key='hide_poll', button_color=('white', 'red'), )],
            [sg.Button('Reset Poll', font="Helvetica", key='reset_poll', button_color=('white', 'red'), ), ]
        ], element_justification='center', title_location='n')],
        [sg.Button('Remove OBS Sources', font="Helvetica", key='remove_sources', button_color=('white', 'red'), )],
    ]


def stream_chat_wars_layout():
    return [
        [sg.Text('Chat Plays Control Panel', justification='center', font=("Helvetica", 30), size=(800, 1),
                 relief=sg.RELIEF_RIDGE, key='title', text_color='white', background_color='blue', border_width=3)],
        [sg.HSeparator()],
        # Input Server Controls Frame
        [sg.Column(layout=[
            [sg.Frame(title="Main Controls", layout=[
                [sg.Column(layout=[
                    [sg.Frame(title='Input Server Controls', title_color='Orange', relief=sg.RELIEF_SUNKEN,
                              title_location='n', key='input_server_controls',
                              layout=[
                                  [sg.Text('Controls for the Input Server')],
                                  [sg.Button('Start Input Server', font="Helvetica", key='start_input_server',
                                             button_color=('white', 'green'),
                                             border_width=3)],
                                  [sg.Button('Stop Input Server', font="Helvetica", key='stop_input_server',
                                             button_color=('white', 'red'),
                                             border_width=3)]
                              ], element_justification='center')],
                ], justification='center'),

                    # Chat Wars Controls Frame
                    sg.Frame(title='Chat Plays Controls', title_color='orange', relief=sg.RELIEF_SUNKEN,
                             title_location='n', key='stream_chat_wars_controls', layout=[
                            [sg.Text('Select a game:', font=("Helvetica", 15)),
                             sg.Combo(games.get_game_names(), default_value='none', key='selected_game',
                                      font=("Helvetica", 12), size=(18, 1))],
                            [sg.Button('Start Chat plays', font="Helvetica", key='start_stream_chat_wars',
                                       button_color=('white', 'green'),
                                       border_width=3)],
                            [sg.Button('Stop Chat Plays', font="Helvetica", key='stop_stream_chat_wars',
                                       button_color=('white', 'red'),
                                       border_width=3)]
                        ], element_justification='center')
                ],
                [sg.Frame(title='Input Switches', title_color='orange', relief=sg.RELIEF_SUNKEN, key='input_switches',
                          layout=[
                              [sg.Text('Accept Chat Input:', font=("Helvetica", 15), key='chat_input_status'),
                               sg.Button('On', font="Helvetica", key='accept_chat_input_on',
                                         button_color=('white', 'green'), border_width=3),
                               sg.Button('Off', font="Helvetica", key='accept_chat_input_off',
                                         button_color=('white', 'red'), border_width=3)],
                              [sg.Text('Random Inputs:', font=("Helvetica", 15), key='random_inputs_status'),
                               sg.Button('On', font="Helvetica", key='random_inputs_on',
                                         button_color=('white', 'green'), border_width=3),
                               sg.Button('Off', font="Helvetica", key='random_inputs_off',
                                         button_color=('white', 'red'), border_width=3)],
                              [sg.Text('Reset Teams:', font=("Helvetica", 15), key='reset_teams_text'),
                               sg.Button('Reset', font="Helvetica", key='reset_teams', button_color=('white', 'red'),
                                         border_width=3)],
                          ], title_location='n'),
                 sg.Frame(title='Chat Wars Controls', title_color='orange', relief=sg.RELIEF_SUNKEN,
                          key='chat_wars_controls',
                          layout=[
                              [sg.Text('Failsafe Hotkey:', font=("Helvetica", 15), key='failsafe_hotkey_text'),
                               sg.Text('None', font=("Helvetica", 15), key='failsafe_hotkey')],
                              [sg.Text('Chat Input Hotkey:', font=("Helvetica", 15), key='chat_input_hotkey_text'),
                               sg.Text('None', font=("Helvetica", 15), key='chat_input_hotkey')],
                              [sg.Text('Random Inputs Hotkey:', font=("Helvetica", 15),
                                       key='random_inputs_hotkey_text'),
                               sg.Text('None', font=("Helvetica", 15), key='random_inputs_hotkey')],
                              [sg.Text('Reset Teams Hotkey:', font=("Helvetica", 15), key='reset_teams_hotkey_text'),
                               sg.Text('None', font=("Helvetica", 15), key='reset_teams_hotkey')],
                          ], title_location='n')
                 ],
                [
                    sg.Frame(title='Status Panel', title_color='orange', relief=sg.RELIEF_SUNKEN, key='status_panel',
                             layout=[
                                 # Input Server Status
                                 [sg.Text('Input Server Status:', font=("Helvetica", 15)),
                                  sg.Text('Off', key='input_status', text_color='red')],
                                 # Stream Chat Wars Status
                                 [sg.Text('Chat Plays Status:', font=("Helvetica", 15)),
                                  sg.Text('Off', key='stream_chat_wars_status', text_color='red')],
                                 # Chat Input Status
                                 [sg.Text('Chat Input:', font=("Helvetica", 15)),
                                  sg.Text('Off', key='chat_input', text_color='red')],
                                 # Random Inputs Status
                                 [sg.Text('Random Inputs:', font=("Helvetica", 15)),
                                  sg.Text(('Off' if GlobalEventStates.state_random_action is False else 'On'),
                                          key='random_inputs', text_color='red')],
                             ], title_location='n'),
                ],
            ], title_location='n', element_justification='center', vertical_alignment='center', key='main_controls',
                      relief=sg.RELIEF_SUNKEN)],
            [sg.HSeparator()],
            [sg.Button('Main Menu', font="Helvetica", key='Menu', button_color=('white', 'red'),
                       border_width=3), ]
        ], justification='center', element_justification='center', vertical_alignment='center')]
    ]


def login_layout():
    return [

        [sg.Text('Twitch Login', justification='center', font=("Helvetica", 30), size=(800, 1))],
        [sg.Text('WHATEVER YOU DO DONT EVER SHOW THIS ON STREAM!!', justification='center', font=("Helvetica", 15),
                 text_color='red', size=(800, 1))],
        [sg.HSeparator()],
        [sg.Column(layout=[
            [sg.Frame(title='Login', title_location='n', title_color='purple', relief=sg.RELIEF_SUNKEN,
                      key='twitch_login', layout=[
                    [sg.Text('Bot Username:', font=("Helvetica", 15)),
                     sg.InputText(key='bot_username', font=("Helvetica", 15), size=(20, 1))],
                    [sg.Text('Bot OAuth:', font=("Helvetica", 15)),
                     sg.InputText(key='bot_oauth', font=("Helvetica", 15), size=(30, 1), password_char='*')],
                    [sg.Text('Twitch API Client ID: ', font=("Helvetica", 15)),
                     sg.InputText(key='twitch_api_client_id', font=("Helvetica", 15), size=(30, 1))],
                    [sg.Text('Twitch API Client Secret: ', font=("Helvetica", 15)),
                     sg.InputText(key='twitch_api_client_secret', font=("Helvetica", 15), size=(30, 1),
                                  password_char='*')],
                    [sg.Text('OBS Websocket Host: ', font=("Helvetica", 15)),
                     sg.InputText(key='obs_websocket_host', font=("Helvetica", 15), size=(30, 1))],
                    [sg.Text('OBS Websocket Port: ', font=("Helvetica", 15)),
                     sg.InputText(key='obs_websocket_port', font=("Helvetica", 15), size=(30, 1))],
                    [sg.Text('OBS Poll Address: ', font=("Helvetica", 15)),
                     sg.InputText(key='obs_poll_address', font=("Helvetica", 15), size=(20, 1))],
                    [sg.Button('Login', font="Helvetica", key='bot_login', button_color=('white', 'green'))],
                ], vertical_alignment='center', element_justification='center')],
            [sg.Button('Exit', font="Helvetica", key='Exit_1', button_color=('white', 'red'),
                       border_width=3)]
        ], justification='center', vertical_alignment='center', element_justification='center')]
    ]


def remove_temp_files():
    if os.path.exists(ACCEPT_INPUT_FILE):
        os.remove(ACCEPT_INPUT_FILE)
    if os.path.exists(RANDOM_ACTIONS_FILE):
        os.remove(RANDOM_ACTIONS_FILE)


OBS_HOST = ""
OBS_PORT = None
OBS_WEBSERVER = ""


def set_values(host, port, webserver):
    global OBS_HOST, OBS_PORT, OBS_WEBSERVER
    OBS_HOST = host
    OBS_PORT = port
    OBS_WEBSERVER = webserver


def is_obs_running():
    for proc in psutil.process_iter():
        try:
            if proc.name().lower() == 'obs64.exe':
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False


def is_gba_emulator_running():
    for proc in psutil.process_iter():
        try:
            if proc.name().lower() == 'visualboyadvance-m.exe':
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False


def is_snes_emulator_running():
    for proc in psutil.process_iter():
        try:
            if proc.name().lower() == 'emuhawk.exe':
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False


def check_login_values(values):
    if values['bot_username'] == '':
        return False
    elif values['bot_oauth'] == '':
        return False
    elif values['twitch_api_client_id'] == '':
        return False
    elif values['twitch_api_client_secret'] == '':
        return False
    elif values['obs_websocket_host'] == '':
        return False
    elif values['obs_websocket_port'] == '':
        return False
    elif values['obs_poll_address'] == '':
        return False
    return True


class GUI:
    config: ConfigDict
    credentials: CredentialDict
    channel_set: set[str]

    def __init__(self):
        """
        Here is the list of layouts that are used in the GUI
        """
        self.bot = None
        self.status_panel_thread = threading.Thread(target=self.update_status_panel, args=())
        self.status_panel_thread.daemon = True

        self.current_layout = None  # Current used layout
        self.layout_list = []  # List of all layouts
        ##########################################################
        '''
        Here is the list of variables that are used in the GUI
        '''

        self.input_server_started = False
        self.input_server_process = None
        self.stream_chat_wars_started = False
        self.stream_chat_wars_process = None
        self.saved_config = None
        self.saved_game = None
        self.obs_hook = None
        ##########################################################
        sg.theme('DarkAmber')
        sg.set_options(font=("Helvetica", 15))
        sg.theme_input_background_color('black')
        sg.theme_input_text_color('white')

        self.load_layouts()
        self.current_layout = 'Main'
        self.__main__()

    def load_layouts(self):
        self.layout_list = [[sg.Column(main_layout(), key=f'-COL_Main-'),
                             sg.Column(stream_chat_wars_layout(), visible=False, key=f'-COL_Stream_Chat_Wars-'),
                             sg.Column(chat_picks_layout(), visible=False, key=f'-COL_Chat_Picks-'),
                             sg.Column(login_layout(), visible=False, key=f'-COL_Login-')]
                            ]

    def __main__(self):
        self.window = sg.Window('Stream Extensions', self.layout_list, size=(800, 700), finalize=True,
                                icon='userinterface/icon.ico')
        self.status_panel_thread.start()

        self.check_twitch_credentials()  # Check if twitch credentials are present
        # self.validate_credentials()  # Validate Twitch Credentials

        while True:
            event, values = self.window.read(timeout=1000)
            if event == sg.WIN_CLOSED or event == 'exit' or event == 'Exit' or event == 'Exit_1':  # Exit
                print('Shutting down...')
                print('Closing all processes...')
                if self.stream_chat_wars_started:
                    print('Stopping Stream Chat Wars Server...')
                    self.stop_stream_chat_wars_server()
                    print('Stream Chat Wars Server Stopped')
                if self.input_server_started:
                    print('Stopping Input Server...')
                    self.stop_input_server()
                    print('Input Server Stopped')
                if self.obs_hook is not None:
                    print('Disconnecting from OBS...')
                    self.obs_hook.close_connection()
                    print('Disconnected from OBS')
                print('Removing temporary files...')
                remove_temp_files()
                print('Exiting...')
                exit(0)
            elif event == 'Menu' or event == 'Main_Menu':  # Main Menu
                self.update_current_layout('Main')
                pass
            elif event == 'chat_picks':  # Chat Picks
                self.update_current_layout('Chat_Picks')
            elif event == 'bot_login':  # Twitch Login
                if check_login_values(values):
                    self.set_new_credentials(values)
            elif event == 'start_webserver':
                # if not is_obs_running():
                #     sg.popup('OBS is not running, please start OBS first')
                #     pass
                # else:
                self.obs_hook = obsplugin.start_connection()
                self.window['selected_scene'].update(values=self.obs_hook.get_obs_scenes(), value='none')
                if not self.obs_hook.is_obs_setup():
                    self.window['obs_setup'].update(visible=True)
                    self.window['controls'].update(visible=False)
                else:
                    self.window['obs_setup'].update(visible=False)
                    self.window['controls'].update(visible=True)
                    self.window['scene_setup'].update(self.obs_hook.get_scene())
            elif event == 'stop_webserver':
                if self.obs_hook is not None:
                    self.stop_obs_server()
            elif event == 'reset_credentials':
                os.remove(DEFAULT_CREDENTIAL_FILE)
                self.check_twitch_credentials()
            elif event == 'test_button':
                if self.obs_hook is not None:
                    self.obs_hook.test_function()
            elif event == 'setup_obs':
                if values['selected_scene'] != 'none' and values['streamer_name'] != '':
                    self.obs_hook.setup_obs(values['selected_scene'], values['streamer_name'])
                    self.window['obs_setup'].update(visible=False)
                    self.window['controls'].update(visible=True)
                    self.window['scene_setup'].update(self.obs_hook.get_scene())
            elif event == 'go_to_scene':
                self.obs_hook.swap_to_scene()
            elif event == 'set_visible':
                if self.obs_hook is not None:
                    self.obs_hook.set_scene_visibity(True, self.obs_hook.image_source_name)
            elif event == 'set_invisible':
                if self.obs_hook is not None:
                    self.obs_hook.set_scene_visibity(False, self.obs_hook.image_source_name)
            elif event == 'show_poll':
                if self.obs_hook is not None:
                    self.obs_hook.set_scene_visibity(True, self.obs_hook.poll_source_name)
            elif event == 'hide_poll':
                if self.obs_hook is not None:
                    self.obs_hook.set_scene_visibity(False, self.obs_hook.poll_source_name)
            elif event == 'upload_image':
                self.obs_hook.set_image(values['-FILEIN-'])
            elif event == 'clear_image':
                self.obs_hook.set_image('')
            elif event == 'enable_poll':
                self.obs_hook.enable_poll()
            elif event == 'disable_poll':
                self.obs_hook.disable_poll()
            elif event == 'reset_poll':
                self.obs_hook.reset_poll()
            elif event == 'remove_sources':
                self.obs_hook.remove_sources()
                self.window['obs_setup'].update(visible=True)
                self.window['controls'].update(visible=False)
            elif event == 'stream_chat_wars':  # Stream Chat Wars
                self.update_current_layout('Stream_Chat_Wars')
            elif event == 'start_input_server':  # Start Input Server
                self.start_input_server()
            elif event == 'stop_input_server':  # Stop Input Server
                self.stop_input_server()
            elif event == 'start_stream_chat_wars':  # Start Stream Chat Wars
                self.start_stream_chat_wars_server(values)
            elif event == 'stop_stream_chat_wars':  # Stop Stream Chat Wars
                self.stop_stream_chat_wars_server()
            elif event == 'accept_chat_input_on':  # Start Chat Input
                if not os.path.exists(ACCEPT_INPUT_FILE):
                    print('Enabling Chat Input')
                    open(ACCEPT_INPUT_FILE, 'x')
            elif event == 'accept_chat_input_off':  # Stop Chat Input
                if os.path.exists(ACCEPT_INPUT_FILE):
                    print('Disabling Chat Input')
                    os.remove(ACCEPT_INPUT_FILE)
            elif event == 'random_inputs_on':  # Random Inputs
                print('Enabling Random Inputs')
                if not os.path.exists(RANDOM_ACTIONS_FILE):
                    open(RANDOM_ACTIONS_FILE, 'x')
            elif event == 'random_inputs_off':  # Random Inputs
                print('Disabling Random Inputs')
                if os.path.exists(RANDOM_ACTIONS_FILE):
                    os.remove(RANDOM_ACTIONS_FILE)
            elif event == 'reset_teams':  # Reset Teams
                print('Resetting Teams')
                pydirectinput.press(self.config.get("events").get("hotkeys").get("reset_teams", 'F15').lower())

    def start_input_server(self):
        if not self.input_server_started:
            print('Starting Input Server...')
            self.input_server_process = subprocess.Popen('python -m input_server'.split(),
                                                         stderr=subprocess.PIPE)
        else:
            sg.popup('Input Server already started.')

    def stop_input_server(self):
        if self.input_server_started:
            print('Stopping Input Server...')
            subprocess.call(['taskkill', '/F', '/T', '/PID', str(self.input_server_process.pid)])
            self.input_server_started = False
        else:
            sg.popup('Input Server not started.')

    def start_stream_chat_wars_server(self, values):
        if self.input_server_started:
            if not self.stream_chat_wars_started:
                game = values['selected_game']
                if game != 'none':
                    selected_config = games.get_selected_game_config(game)
                    self.saved_config = selected_config
                    self.saved_game = game
                    self.config, self.credentials = read_json_configs(selected_config)
                    irc_setting: IRC_Settings = extract_irc_settings(self.config, self.credentials.get("TwitchChat"),
                                                                     channels)
                    print('Starting Stream Chat Wars for ' + game + '...')
                    self.stream_chat_wars_process = subprocess.Popen(
                        ['python', '-m', 'streamchatwars', selected_config],
                        stdin=subprocess.PIPE)

                    if game == games.GAME_POKEMON_FIRE_RED['name']:
                        if not is_gba_emulator_running():
                            os.startfile("userinterface\\pokemon\\Pokemon_FireRed.gba")
                            self.bot: BackupBot = BackupBot(irc_setting, self)
                            self.bot.create_thread()
                            self.bot.start_thread()
                    if game == games.GAME_POKEMON_EMERALD['name']:
                        if not is_gba_emulator_running():
                            self.bot: BackupBot = BackupBot(irc_setting, self)
                            self.bot.create_thread()
                            self.bot.start_thread()
                            os.startfile("userinterface\\pokemon\\Pokemon_Emerald.GBA")
                    if game == games.GAME_EARTHBOUND['name']:
                        if not is_snes_emulator_running():
                            self.bot: BackupBot = BackupBot(irc_setting, self)
                            self.bot.create_thread()
                            self.bot.start_thread()
                            os.startfile("userinterface\\SNES\\BizHawk\\EmuHawk.exe")
                else:
                    sg.popup('Please select a game to run Chat Plays for.')
        else:
            sg.popup('Please start the Input Server first.')

    def stop_stream_chat_wars_server(self):
        if self.stream_chat_wars_started:
            print('Stopping Stream Chat Wars...')
            subprocess.call('taskkill /F /T /PID ' + str(self.stream_chat_wars_process.pid))
            self.window['stream_chat_wars_status'].update('Stopped', text_color='red')
            self.stream_chat_wars_started = False
        else:
            sg.popup('Chat Plays not started.')

    def restart_chat_plays(self):
        if self.stream_chat_wars_started:
            self.stop_stream_chat_wars_server()
        self.start_stream_chat_wars_server(values={'selected_game': self.saved_game})

    def restart_input_server(self):
        if self.input_server_started:
            self.stop_input_server()
        self.start_input_server()

    def fix_chat_input_file(self):
        if os.path.exists(ACCEPT_INPUT_FILE):
            os.remove(ACCEPT_INPUT_FILE)
            sleep(2)
            open(ACCEPT_INPUT_FILE, 'x')
            return
        if not os.path.exists(ACCEPT_INPUT_FILE):
            open(ACCEPT_INPUT_FILE, 'x')
            return

    def update_current_layout(self, layout):
        self.window[f'-COL_{self.current_layout}-'].update(visible=False)
        self.current_layout = layout
        self.window[f'-COL_{self.current_layout}-'].update(visible=True)

    def check_process_state(self):  # Check if the servers are running
        if self.input_server_started:  # Check if the Input Server is running
            if self.input_server_process.poll() is None:
                pass
            else:
                print(self.input_server_process.poll())
                pass

        if self.stream_chat_wars_started:  # Check if the Stream Chat Wars is running
            if self.stream_chat_wars_process.poll() is None:
                pass
            else:
                print('# Stream Chat Wars crashed - Attempting to automatically restart')
                self.stream_chat_wars_process = subprocess.Popen(
                    ['python', '-m', 'streamchatwars', self.saved_config],
                    stdin=subprocess.PIPE)

    def check_twitch_credentials(self):
        config_arg: str | None = sys.argv[1] if len(sys.argv) > 1 else None
        credentials_arg: str | None = sys.argv[2] if len(sys.argv) > 2 else None
        try:
            self.config, self.credentials = read_json_configs(config_arg, credentials_arg)
            print("Credentials file exists, checking credentials...")
            self.validate_credentials()
        except (OSError, JSONDecodeError, ValidationError):
            self.config, self.credentials = read_json_configs()
            self.update_current_layout('Login')
            # sg.popup("Invalid Twitch Chat credentials found. Go yell at thundercookie15 to send you new ones.")

    def validate_credentials(self) -> None | bool:
        chat_credentials: TwitchChatCredentialDict | None
        chat_credentials = self.credentials.get("TwitchChat", None)

        if not chat_credentials:
            print("No Twitch chat credentials provided.")
            sg.popup("No Twitch Chat credentials found. Go yell at thundercookie15 to send you new ones.")
            return False
        try:
            self.channel_set: set[str] = set()
            for team in GlobalData.Teams.get_all_teams():
                self.channel_set.update(team.channels)
            irc_setting: IRC_Settings = extract_irc_settings(self.config, chat_credentials, self.channel_set)
            username = irc_setting.username
            oauth = irc_setting.oauth_token
            host = self.credentials.get("OBS", {}).get("host").get("value")
            port = self.credentials.get("OBS", {}).get("port").get("value")
            webserver = self.credentials.get("OBS", {}).get("webserver").get("value")
            if username == "YOUR_BOT_USERNAME_LOWERCASE" or oauth == "YOUR_BOT_OAUTH_TOKEN":
                raise InvalidCredentialsError
            set_values(host, port, webserver)
            print('Credentials validated...')
            self.update_current_layout('Main')
        except InvalidCredentialsError:
            sg.popup("Invalid Twitch Chat credentials found. Go yell at thundercookie15 to send you new ones.")
            self.update_current_layout('Login')
            return False

    def set_new_credentials(self, values):
        username = values['bot_username']
        oauth = values['bot_oauth']
        client_id = values['twitch_api_client_id']
        client_secret = values['twitch_api_client_secret']
        obs_host = values['obs_websocket_host']
        obs_port = values['obs_websocket_port']
        obs_poll_address = values['obs_poll_address']
        self.credentials.get("TwitchChat").get("username").update({"value": username})
        self.credentials.get("TwitchChat").get("oauth_token").update({"value": oauth})
        self.credentials.get("TwitchAPI").get("client_id").update({"value": client_id})
        self.credentials.get("TwitchAPI").get("client_secret").update({"value": client_secret})
        self.credentials.get("OBS").get("host").update({"value": obs_host})
        self.credentials.get("OBS").get("port").update({"value": obs_port})
        self.credentials.get("OBS").get("webserver").update({"value": obs_poll_address})
        json_utils.write_credentials_file(self.credentials, DEFAULT_CREDENTIAL_FILE)
        self.check_twitch_credentials()

    def update_status_panel(self):
        while True:
            if self.current_layout == 'Chat_Picks':
                if self.obs_hook is not None:
                    if self.obs_hook.is_obs_setup:
                        if self.obs_hook.get_poll_status().get('active'):
                            self.window['poll_status_text'].update('Active', text_color='green')
                        else:
                            self.window['poll_status_text'].update('Inactive', text_color='red')
                        if not self.obs_hook.get_current_scene() == self.obs_hook.get_scene():
                            self.window['go_to_scene'].update(visible=True)
                        else:
                            self.window['go_to_scene'].update(visible=False)
                    self.window['scene_text'].update(self.obs_hook.get_current_scene())
            if self.current_layout == 'Stream_Chat_Wars':
                self.check_process_state()
                if self.input_server_process is not None:
                    if self.input_server_process.poll() is None:
                        self.input_server_started = True
                    else:
                        self.input_server_started = False
                if self.input_server_started:
                    self.window['input_status'].update('Running', text_color='green')
                else:
                    self.window['input_status'].update('Stopped', text_color='red')

                # Stream Chat Wars bullshit
                if self.stream_chat_wars_process is not None:
                    if self.stream_chat_wars_process.poll() is None:
                        self.stream_chat_wars_started = True
                    else:
                        self.stream_chat_wars_started = False
                if self.stream_chat_wars_started:
                    self.window['chat_input'].update('On' if os.path.exists(ACCEPT_INPUT_FILE) else 'Off',
                                                     text_color='green' if os.path.exists(ACCEPT_INPUT_FILE) else 'red')
                    self.window['random_inputs'].update('On' if os.path.exists(RANDOM_ACTIONS_FILE) else 'Off',
                                                        text_color='green' if os.path.exists(RANDOM_ACTIONS_FILE) else
                                                        'red')
                    self.window['stream_chat_wars_status'].update(
                        'Running' if self.stream_chat_wars_process.poll() is None
                        else 'Failed to start', text_color='green'
                        if self.stream_chat_wars_process.poll() is None else 'red')
                    hotkeys = self.config.get("events").get("hotkeys")
                    self.window['failsafe_hotkey'].update(f'{hotkeys.get("failsafe", "Shift+Backspace")}')
                    self.window['chat_input_hotkey'].update(f'{hotkeys.get("accept_input", "F13")}')
                    self.window['random_inputs_hotkey'].update(f'{hotkeys.get("random_action", "F14")}')
                    self.window['reset_teams_hotkey'].update(f'{hotkeys.get("reset_teams", "F15")}')
                if not self.stream_chat_wars_started:
                    self.window['stream_chat_wars_status'].update('Stopped', text_color='red')

                if self.input_server_started:
                    self.window['input_status'].update('Running' if self.input_server_process.poll() is None else
                                                       'Failed to start', text_color='green' if
                    self.input_server_process.poll() is None else 'red')
                    if not self.input_server_started:
                        self.window['input_status'].update('Stopped', text_color='red')

            self.window.refresh()

    def stop_obs_server(self):
        self.obs_hook.close_connection()
        self.obs_hook = None
        self.window['obs_setup'].update(visible=False)
        self.window['controls'].update(visible=False)


class BackupBot(
    SingleServerIRCBot,
    AbstractMessageSender,
    AbstractThreadSupport
):
    reactor_class: type[Custom_Reactor] = Custom_Reactor
    reactor: Custom_Reactor
    host: str
    port: int
    channel_set: set[str]
    message_interval: float
    connection_timeout: float
    join_rate_limit_amount: int
    join_rate_limit_time: float
    last_message_time: float
    '''Keep track of time when last message was sent to keep within rate-limits'''
    message_queue: deque[tuple[str, str]]
    keep_running: bool
    finished_startup: bool = False
    message_queue_thread: threading.Thread

    def __init__(self, irc_settings: IRC_Settings, gui) -> None:
        self.gui = gui
        server_list: list[tuple[str, int, str]] = [(
            irc_settings.host,
            irc_settings.port,
            irc_settings.oauth_token
        )]

        self.host = irc_settings.host
        self.port = irc_settings.port

        nickname: str = irc_settings.username
        realname: str = irc_settings.username

        self.channel_set = irc_settings.channel_set

        self.message_interval = irc_settings.message_interval
        self.connection_timeout = irc_settings.connection_timeout
        self.join_rate_limit_amount = irc_settings.join_rate_limit_amount
        self.join_rate_limit_time = irc_settings.join_rate_limit_time

        self.last_message_time = 0
        self.message_queue = deque()

        self.keep_running = True

        self.message_queue_thread = threading.Thread(
            target=self.handle_message_queue,
            daemon=True)
        self.message_queue_thread.start()

        # let base class handle the rest
        super().__init__(
            server_list,
            nickname,
            realname,
            connect_factory=self.create_connect_factory()
        )

    def create_connect_factory(self) -> Factory:
        '''
        We only need this to make the connection SSL compatible.
        Because for some reason nobody thought that SSL connections should be an
        easy default instead of diving into the code and finding out what needs
        to be wrapped...
        '''
        ssl_context: SSLContext = create_default_context()
        wrapping_func: partial[SSLSocket] = partial(
            ssl_context.wrap_socket,
            server_hostname=self.host
        )
        ssl_factory: Factory = Factory(wrapper=wrapping_func)
        return ssl_factory

    def stop_bot(self) -> None:
        '''
        Disconnect from the IRC server and stop all looping operations
        (including self.reactor), so the bot's thread can be shut down.
        '''
        self.keep_running = False
        while self.message_queue_thread.is_alive():
            # Wait until sub-thread has shutdown so we're never in the
            # awkward position of trying to send messages after the connection
            # to the server has been disconnected.
            sleep(0.1)
        self.disconnect("Bye")
        self.reactor.keep_running = False

    def handle_message_queue(self) -> None:
        '''
        Sub-thread function that sends out queued messages when rate limits allow.
        '''
        while self.keep_running:
            try:
                channel, message = self.message_queue.popleft()
                # This is kinda hacky, but it gets the job done.
                # Basically retry sending every 0.1 seconds
                # until rate limits allow sending and the message is out.
                while self.keep_running and not self.send_message(channel, message):
                    sleep(0.1)
            except IndexError:
                sleep(0.1)

    def on_disconnect(self, connection: ServerConnection, event: threading.Event) -> None:
        '''
        Called when the bot has been disconnected from the server.
        '''
        thread_print_timestamped(ColorText.error(
            f"Disconnected from {self.host}:{self.port}!"
        ))
        if not self.finished_startup:
            # If the bot hasn't finished startup yet, we try an accelerated
            # reconnection attempt.
            sleep(1)
            self.start()

    def join_channels(self, connection: ServerConnection) -> None:
        '''
        Join all channels in `self.channel_set` while respecting rate limits
        set by `self.join_rate_limit_amount` and `self.join_rate_limit_time`.

        Intended to be used in its own thread to prevent rate limit cooldowns
        stopping event processing for the rest of the bot.
        '''
        rate_limit_counter: int = 0
        join_set: set[str] = set()
        channel: str
        for channel in self.channel_set:
            if rate_limit_counter < self.join_rate_limit_amount:
                # Collect channels to join in one go a long as rate limit isn't reached
                join_set.add(channel)
                rate_limit_counter += 1
            else:
                # Rate limit reached: Join the collected channels and reset + wait
                thread_print(f"Attempting to join channels: {', '.join(join_set)}")
                for chan in join_set:
                    if not self.keep_running:  # Safety: don't join in dead connection
                        self.stop_bot()
                        return
                    connection.join(chan)
                join_set.clear()
                thread_print(ColorText.warning(
                    f"Join rate limit reached. Waiting {self.join_rate_limit_time} "
                    "seconds before attempting further joins."
                ))
                sleep(self.join_rate_limit_time)
                rate_limit_counter = 0
        # Join remaining channels
        if join_set:
            thread_print(f"Attempting to join channels: {', '.join(join_set)}")
            for chan in join_set:
                if not self.keep_running:  # Safety: don't join in dead connection
                    self.stop_bot()
                    return
                connection.join(chan)

    def on_join(self, c: ServerConnection, e: Event) -> None:
        '''
        IRC Event (executes when users are joining a channel)

        Only used for output to keep user in the loop.
        '''
        if str(e.source).split("!")[0] == c.nickname:
            thread_print(f"Joined channel {e.target}")

    def check_all_joined(self) -> None:
        '''
        Cancel the connection attempt if some channels could not be joined.

        Tell the user where the problem lies, so they get a chance to fix
        possible malformed configuration files.
        '''
        time_slept: float = 0
        missing_channel_set: set[str] = set()
        while time_slept <= self.connection_timeout:
            if not self.keep_running:
                self.stop_bot()
                return
        sleep(CHECK_JOIN_INTERVAL)
        time_slept += CHECK_JOIN_INTERVAL
        missing_channel_set = self.channel_set - set(self.channels.keys())
        if len(missing_channel_set) == 0:
            thread_print(ColorText.good(
                ">> Joined all channels, you're good to go! <<"
            ))
            self.finished_startup = True
            self.finish_connecting()
            return
        thread_print(ColorText.error(
            "Some channels could not be joined in time: "
            f"{' '.join(missing_channel_set)}"
        ))
        thread_print(ColorText.error("Aborting!"))
        self.stop_bot()
        self.abort_connection()

    # ----------------------------------------------------------------------------

    def finish_connecting(self) -> None:
        '''
        Entry point for a mock method to test other things that require a
        server connection or wrap up testing.

        Does nothing in its default implementation by design!
        '''
        pass

    def start_and_check(self) -> None:
        '''
        Start the bot and establish a connection to the chat server.

        Since the bot operates in a blocking way, check if the
        connection was successful in another thread.
        '''
        self.finished_startup = False
        threading.Thread(target=self.check_all_joined).start()
        thread_print(ColorText.warning(
            f"Attempting connection to {self.host}:{self.port}"
        ))
        try:
            self.start()
        except ValueError as e:
            # sometimes start() raises an exception after die() has been called.
            if e.args[0] != "Read on closed or unwrapped SSL socket.":
                raise
        except ServerNotConnectedError:
            thread_print(ColorText.error("Server Connection lost!"))
            self.keep_running = False
            self.reactor.keep_running = False
            return
        except StopBotException:
            thread_print(ColorText.warning("Stopped bot."))
            return
        return

    def create_thread(self) -> None:
        '''
        Create thread.
        '''
        self.thread = threading.Thread(
            target=self.start_and_check,
            daemon=True
        )

    def start_thread(self) -> None:
        '''
        Start thread.
        '''
        self.thread.start()

    # ----------------------------------------------------------------------------

    def stop_thread(self) -> None:
        '''
        Stop thread.
        '''
        self.stop_bot()

    def queue_message(self, channel: str, message: str) -> None:
        '''
        Send a `message` to the chosen `channel` (when rate limits allow).

        The message could be sent immediately, any time after, or never
        (if the bot disconnects before the message queue can be emptied).
        Don't use this function, if you need the message out there immediately!
        '''
        self.message_queue.append((channel, message))

    def abort_connection(self) -> None:
        '''
        Entry point for a mock method to test naturally failed connection
        attempts. (It happens sometimes in the real world)

        Does nothing in its default implementation by design!
        '''
        pass

    def on_welcome(self, connection: ServerConnection, event: Event) -> None:
        '''
        IRC EVENT (executes after successfully establishing a connection
        to the server)

        Request IRCv3 capabilities and join all relevant channels.
        '''
        thread_print_timestamped(
            f"Connected to {self.host}:{self.port} as user "
            f"{ColorText.info(connection.username)}, joining channels..."
        )
        connection.cap('REQ', ':twitch.tv/membership')
        connection.cap('REQ', ':twitch.tv/tags')
        connection.cap('REQ', ':twitch.tv/commands')
        # outsource joining into an extra thread to have events continue
        # to be processed while waiting for rate limit delays.
        threading.Thread(target=self.join_channels, args=[connection], daemon=True).start()

    def on_pubmsg(self, connection: ServerConnection, event: threading.Event) -> None:
        '''
        IRC EVENT (executes when a message is sent in a channel)

        Relevant event data is contained in `event` and needs some touch-up
        before being passed on to the rest of the application.
        '''
        msg: ChatMessage = ChatMessage.from_event(event, parent=self)
        GlobalData.Session.Chat.log_message(msg)
        if GlobalData.Prefix.Command.message_is_command(msg):
            if msg.message == '?restartchatplays':
                if msg.user in mods:
                    print('Restarting Chat Plays...')
                    GUI.restart_chat_plays(self.gui)
            if msg.message == '?restartinputserver':
                if msg.user in mods:
                    print('Restarting Input Server...')
                    GUI.restart_input_server(self.gui)
            if msg.message == '?fixchatinputfile':
                if msg.user in mods:
                    print('Fixing Chat Input File...')
                    GUI.fix_chat_input_file(self.gui)

    def send_message(self, channel: str, message: str) -> bool:
        '''
        Send a `message` to the chosen `channel` (if rate limits allow).

        Don't rely on this function to send the message in the first place.

        Return `True` on success, `False` if message hasn't been sent.
        '''
        if time() - self.last_message_time > self.message_interval:
            self.send_priority_message(channel, message)
            return True
        return False

        # ----------------------------------------------------------------------------

    def send_priority_message(self, channel: str, message: str) -> None:
        '''
        Send a `message` to the chosen `channel` (ignore rate limits).

        This function will ignore any rate limits and just send the message
        anyways.

        Be cautious, because you are responsible for not getting
        your bot forcibly disconnected for spamming!
        '''
        # ignore last_message_time check
        self.connection.privmsg(channel, message)
        self.last_message_time = time()
