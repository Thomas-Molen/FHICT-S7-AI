from typing import Optional
import gym
from gym import spaces
import numpy as np

import selenium.common.exceptions
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains 
from selenium import webdriver
from selenium.webdriver.common.by import By

default_rewards_table = {"LOGS": {"SEVERE": 100, "WARNING": 10, "INFO": 0}, "ACTIONS": {"FAIL": -100}}
def ensure_reward_structure(original_structure, dynamic_structure):
        for key, value in original_structure.items():
            if key not in dynamic_structure:
                dynamic_structure[key] = value
            elif isinstance(value, dict) and isinstance(dynamic_structure[key], dict):
                ensure_reward_structure(value, dynamic_structure[key])
        return dynamic_structure

class WebEnv(gym.Env):
    metadata = {"render_modes": ["human", "headless"]}
    
    def __init__(self,
                 render_mode: Optional[str] = None, 
                 url=None, 
                 keywords=[],
                 rewards = {},
                 ):
        if (url is None): # Block env if it does not have any target the use
            raise TypeError("A valid url has to be provided")
        
        self.render_mode = render_mode # Pass render_mode to base env
        super(WebEnv, self).__init__() # Initialize base Gym env
        
        # Set environment values
        self.keyword_targets = keywords # To be used when evaluation the webpage for convergence pressuring
        self.target_url = url # To be used during setup of Selenium webdriver as starting state
        self.reward_table = ensure_reward_structure(default_rewards_table, rewards) # Reward lookup table that will be used to give rewards, if user has edited the rewards table, any missing values will be populated with the default structure

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
                    dtype=np.float16) for keyword in keywords}),
            'interactables': spaces.Box(
                    low=0, 
                    high=np.inf, 
                    shape=(1, ), 
                    dtype=np.float16),
            'actions_taken': spaces.Box(
                    low=0, 
                    high=np.inf, 
                    shape=(1, ), 
                    dtype=np.float16),
        })

        # Set base action space
        # 0: Next element
        # 1: Interact
        self.action_space = spaces.Discrete(2)

        # Set value to contain the internal action elements
        self._action_elements = []
        self._current_action_element = 0
        self._steps_since_interaction = 0

        # Set Selenium options
        web_driver_options = Options()
        # Initialize the Selenium web driver
        if (self.render_mode == 'headless'): # If render mode is not human, the browser can be run in a headless mode
            web_driver_options.add_argument('--headless=new')
        self._web_service = Service(executable_path="Environments/chromedriver.exe") #TODO: The executable_path is relative from the executing file, not the source file
        self._web_driver = webdriver.Chrome(service=self._web_service, options=web_driver_options)

    # Queries the current HTML for the count of set keywords
    def _get_keywords_from_page(self):
        results = {}
        for keyword in self.keyword_targets:
            try:
                # Find elements that contain the given keyword as text
                results[keyword] = len(self._web_driver.find_elements(By.XPATH, f"//*[contains(text(), {keyword})]"))
            except selenium.common.exceptions.NoSuchElementException: 
                # If no elements where found, set count to zero instead of throwing
                results[keyword] = 0
        return results
    
    # Obtains current observation space data
    def _get_current_state(self):
        # self._web_driver.execute_script("console.log(Array.from(document.querySelectorAll('*')).map(element => {const listeners = getEventListeners(element)return {element: element,listeners: Object.keys(listeners).map(key => {return {event: key,listeners: listeners[key]};})};}).filter(item => item.listeners.length))")
        keyword_count = self._get_keywords_from_page()
        state = {
            'keywords': keyword_count,
            'interactables': len(self._action_elements),
            'actions_taken': self._steps_since_interaction
        }
        return state # State as observation_state shape
    
    # Obtains current webpage info
    def _get_current_info(self):
        current_url = self._web_driver.current_url
        # Return a dictionary of environment info
        return {
            'driver': self._web_driver,
            'url': current_url,
            'interactables': self._action_elements,
            'interaction_idx': self._current_action_element
        }
    
    # Will find all interactable HTML elements on the current page
    def _get_interactable_elements(self):
        # TODO: Currently returns all button elements instead of inherently interactable elements such as elements with click listeners
        return self._web_driver.execute_script("return document.getElementsByTagName('button')")
    # Will select given element via index as currently selected index
    def _select_interactable_element(self, index):
        self._current_action_element = index
        # Create action chain to hover over element, this can help with human rendering visual indicator of what is selected
        try:
            action = ActionChains(self._web_driver)
            action.move_to_element(self._action_elements[index]).perform() 
        except:
            # If action chain fails to hover element, just return
            return

    def _get_logs(self, *severities):
        """
        :Args:
         - severities: one or multiple of the following: SEVERE, WARNING, INFO, CONFIG, FINE, FINER, FINEST
        """
        logs = self._web_driver.get_log('browser') # Obtain all new browser logs
        results = {}
        for severity in severities:
            severity_logs = []
            for log in logs:
                if (log['level'] == severity):
                    severity_logs.append(log)
            results[severity] = severity_logs # add the logs of the severity in the form of a dict
        return results
    # Reset environment
    def reset(self, seed: Optional[str] = None, options: Optional[str] = None):
        # Clean up any extra windows, so that only the currently targeted one is open
        windows = self._web_driver.window_handles
        window_to_keep = self._web_driver.current_window_handle
        for window in windows:
            if (window != window_to_keep):
                self._web_driver.switch_to.window(window)
                self._web_driver.close()
        self._web_driver.switch_to.window(window_to_keep) # Ensure the correct window will be target after cleanup
        # Get all currently loaded windows, so that window changes can be tracked
        self._windows = self._web_driver.window_handles
        # Send web driver back to original target_url
        self._web_driver.get(self.target_url)
        # Load initial internal list of interactable elements
        self._action_elements = self._get_interactable_elements()
        self._select_interactable_element(0)

        self._web_driver.get_log('browser') # Clear errors that are generated on page load

        initial_state = self._get_current_state()
        initial_info = self._get_current_info()
        return (initial_state, initial_info) # return tuple of state, info

    # Invoke action to move agent to next state
    def step(self, action):
        complete_action_phase = False # Indicator if current step should complete the action phase and thus calculate rewards
        self._action_elements = self._get_interactable_elements() # Re-query the interactable elements, as they might have changed, this might be wasteful as generally interactables only change on interactions, but timed events might change DOM unexpectedly
        reward = 0
        terminated = False
        truncated = False
        info = {}
        if (len(self._action_elements) != 0): # Only perform action if there are any interactable elements
            if (action == 0): # Select the next element
                self._select_interactable_element((self._current_action_element + 1) % len(self._action_elements))  # Get the next index, or loop back to first element if end was hit
                self._steps_since_interaction += 1
            elif (action == 1): # Interact with current element
                try:
                    self._action_elements[self._current_action_element].click()
                except:
                    # Failed to click element, this could be due to it being obscured by another element, or it is disabled
                    reward += self.reward_table["ACTIONS"]["FAIL"]
                # Post process action steps
                self._select_interactable_element(0) # Reset action element index
                complete_action_phase = True
                # TODO: Currently, if an interaction, leads to only the single same interactable being available, the environment action will get into an action loop.
        if (complete_action_phase):
            # Action phase has been completed, so calculate rewards based on web-page info
            logs = self._get_logs("SEVERE", "WARNING", "INFO")
            reward += len(logs["SEVERE"])*self.reward_table["LOGS"]["SEVERE"] # Add severe error reward
            reward += len(logs["WARNING"])*self.reward_table["LOGS"]["WARNING"] # Add warning error reward
            reward += len(logs["WARNING"])*self.reward_table["LOGS"]["INFO"] # Add info error reward
            self._steps_since_interaction = 0
        if (len(self._action_elements) == 0): # No elements left to interact with, so truncate the current session
            truncated = True
            info["truncated"] = "No interactable elements on page"
        if (self._windows != self._web_driver.window_handles): # If the stored windows are no longer inline with the open windows, refocus the environment
            self._web_driver.switch_to.window(self._web_driver.window_handles[-1]) # Switch to the last window, as this should be the newest one
            self._windows = self._web_driver.window_handles
        state = self._get_current_state()
        # Add extra auxiliary info
        info.update(self._get_current_info())
        return (state, reward, terminated, truncated, info, )

    # Manually call renderer
    def render(self):
        # As the Selenium service used does not run in headless mode, a render frame is already provided that updates automatically
        return
        # raise NotImplementedError("render is taken care of by Selenium, and does not have to be called manually for now") # Do not throw, to allow the environment to be seamlessly interchangeable with other environments that do require render
    
    # Close the environment
    def close(self):
        # clean-up the web driver
        self._web_driver.quit()