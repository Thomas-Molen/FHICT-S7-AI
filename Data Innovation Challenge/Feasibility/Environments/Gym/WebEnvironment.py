from typing import Optional
import gym
from gym import spaces
import numpy as np

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium import webdriver

class WebEnv(gym.Env):
    metadata = {"render_modes": ["human", "headless"]}

    def __init__(self,
                 render_mode: Optional[str] = None, 
                 url=None, 
                 keywords=[]):
        if (url is None): # Block env if it does not have any target the use
            raise TypeError("A valid url has to be provided")
        
        self.render_mode = render_mode # Pass render_mode to base env
        super(WebEnv, self).__init__() # Initialize base Gym env
        
        # Set environment values
        self.keyword_targets = keywords # to be used when evaluation the webpage for convergence pressuring
        self.target_url = url # To be used during setup of Selenium webdriver as starting state

        # Set base observation space
        # {
        #   keywords: 
        #   {
        #     keyword: count (0-inf),
        #     ... etc
        #   } 
        # }
        self.observation_space = spaces.Dict({
            # keyword: count
            'keywords': spaces.Dict({
                keyword: spaces.Box(
                    low=0, 
                    high=np.inf, 
                    shape=(1, ), 
                    dtype=np.float16) for keyword in keywords})
        })

        # Set base action space
        self.action_space = spaces.Discrete(1)

        # Set Selenium options
        web_driver_options = Options()
        # Initialize the Selenium web driver
        if (self.render_mode == 'headless'): # If render mode is not human, the browser can be run in a headless mode
            web_driver_options.add_argument('--headless=new')
        self._web_service = Service(executable_path="Environments/chromedriver.exe") #TODO: The executable_path is relative from the executing file, not the source file
        self._web_driver = webdriver.Chrome(service=self._web_service, options=web_driver_options)

    def _get_keywords_from_page(self):
        return {keyword: 0 for keyword in self.keyword_targets}
    
    def _get_current_state(self):
        keyword_count = self._get_keywords_from_page()
        state = {
            'keywords': keyword_count
        }
        return state # State as observation_state shape
    
    def _get_current_info(self):
        current_url = self._web_driver.current_url
        # Return a dictionary of environment info
        return {
            'url': current_url,
        }

    # Reset environment
    def reset(self, seed: Optional[str] = None, options: Optional[str] = None):
        # Send web driver back to original target_url
        self._web_driver.get(self.target_url)

        initial_state = self._get_current_state()
        initial_info = self._get_current_info()
        return (initial_state, initial_info) # return tuple of state, info

    # Invoke action to move agent to next state
    def step(self, action):
        raise NotImplementedError()

    # Manually call renderer
    def render(self):
        # As the Selenium service used does not run in headless mode, a render frame is already provided that updates automatically
        raise NotImplementedError("render is taken care of by Selenium, and does not have to be called manually for now")
    
    # Close the environment
    def close(self):
        # clean-up the web driver
        self._web_driver.quit()