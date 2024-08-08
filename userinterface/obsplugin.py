from obswebsocket import obsws, requests
from requests import get, post


def start_connection():
    return ObsSocket()


def image_input_settings(twitch_name):
    from userinterface.main import OBS_WEBSERVER
    return {
        'css': 'body { background-color: rgba(0, 0, 0, 0); margin: 0px auto; overflow: hidden; }',
        'fps_custom': True,
        'fps': 30,
        'url': f'http://{OBS_WEBSERVER}:8081/?channel={twitch_name}&type=bar&timeout=60&requiredPings=3',
        'width': 500,
        'height': 100,
    }


class ObsSocket:

    def __init__(self):
        from userinterface.main import OBS_WEBSERVER, OBS_HOST, OBS_PORT
        self.client = obsws(host=OBS_HOST, port=OBS_PORT)
        self.scene = None
        self.image_source_name = "Chat_Picks_Image"
        self.poll_source_name = "Chat_Picks_Poll"
        self.finished_source_name = "Chat_Picks_Setup_Finished"
        self.poll_status_url = f'http://{OBS_WEBSERVER}:5000/status'
        self.activate_poll_url = f'http://{OBS_WEBSERVER}:5000/setactive'
        self.deactivate_poll_url = f'http://{OBS_WEBSERVER}:5000/inactive'
        self.client.connect()

    def setup_obs(self, scene_name, twitch_name):
        print('Setting up OBS')
        self.scene = scene_name
        self.client.call(
            requests.CreateInput(sceneName=scene_name, inputName=self.image_source_name, inputKind='browser_source', inputSettings={'url': ''}))
        self.client.call(
            requests.CreateInput(sceneName=scene_name, inputName=self.poll_source_name, inputKind='browser_source',
                                 inputSettings=image_input_settings(twitch_name)))
        finished_id = self.client.call(requests.CreateInput(sceneName=scene_name, inputName=self.finished_source_name,
                                                            inputKind='text_gdiplus_v2')).datain.get('sceneItemId')
        # Set the dummy text source to be the lowest possible and locks it
        self.client.call(requests.SetSceneItemIndex(sceneName=scene_name, sceneItemId=finished_id, sceneItemIndex=0))
        self.client.call(
            requests.SetSceneItemLocked(sceneName=scene_name, sceneItemId=finished_id, sceneItemLocked=True))
        # # Makes the OBS browser source for images invisible, so it doesn't show the ugly default on screen.
        # self.set_scene_visibity(False, self.image_source_name)

    def test_function(self):
        x = requests.post

    def set_image(self, image_url):
        self.client.call(
            requests.SetInputSettings(inputName=self.image_source_name, inputSettings={'url': image_url}))

    def create_source(self, setup_scene):
        self.scene = setup_scene
        self.client.call(
            requests.CreateInput(sceneName=setup_scene, inputName=self.image_source_name, inputKind='image_source'))

    def get_scene_item_id(self, item_name):
        return self.client.call(requests.GetSceneItemId(sceneName=self.scene, sourceName=item_name)).datain.get(
            'sceneItemId')

    def set_scene_visibity(self, visible, scene_name):
        self.client.call(
            requests.SetSceneItemEnabled(sceneName=self.scene, sceneItemId=self.get_scene_item_id(scene_name),
                                         sceneItemEnabled=visible))

    def is_obs_setup(self):
        # First checks the collection of Scenes in OBS
        scenes = self.client.call(requests.GetSceneList())
        # Check scenes if the item ChatPicksImage exists
        for scene in scenes.datain.get('scenes'):
            scene_name = scene.get('sceneName')
            scene_items = self.client.call(requests.GetSceneItemList(sceneName=scene.get('sceneName')))
            # Iterate through Scene Items to check for setup
            for item in scene_items.datain.get('sceneItems'):
                if item.get('sourceName') == self.finished_source_name:
                    self.scene = scene_name
                    return True
        return False

    def get_poll_status(self):
        return get(url=self.poll_status_url).json()

    def remove_sources(self):
        self.client.call(
            requests.RemoveSceneItem(sceneName=self.scene, sceneItemId=self.get_scene_item_id(self.image_source_name)))
        self.client.call(
            requests.RemoveSceneItem(sceneName=self.scene, sceneItemId=self.get_scene_item_id(self.poll_source_name)))
        self.client.call(requests.RemoveSceneItem(sceneName=self.scene,
                                                  sceneItemId=self.get_scene_item_id(self.finished_source_name)))

    def reset_poll(self):
        self.client.call(
            requests.PressInputPropertiesButton(inputName=self.poll_source_name, propertyName='refreshnocache'))

    def enable_poll(self):
        post(url=self.activate_poll_url)

    def disable_poll(self):
        post(url=self.deactivate_poll_url)

    def get_scene(self):
        return self.scene

    def get_current_scene(self):
        return self.client.call(requests.GetCurrentProgramScene()).datain.get('currentProgramSceneName')

    def swap_to_scene(self):
        self.client.call(requests.SetCurrentProgramScene(sceneName=self.scene))

    def get_obs_scenes(self):
        scenes = []
        for scene in self.client.call(requests.GetSceneList()).datain.get('scenes'):
            scenes.append(scene.get('sceneName'))
        return scenes

    def close_connection(self):
        self.client.disconnect()
