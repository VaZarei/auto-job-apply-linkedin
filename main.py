import os
import subprocess
import yaml
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from validate_email import validate_email
from webdriver_manager.chrome import ChromeDriverManager
from linkedinZero import LinkedinZ


 #Open a linkedin page in terminal by this link (include double qotations):
 # "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\selenium-profile"



def init_browser():
    browser_options = Options()
    options = ['--disable-blink-features',
               '--no-sandbox',
               '--start-maximized',
               '--disable-extensions',
               '--ignore-certificate-errors',
               '--disable-blink-features=AutomationControlled',
               '--remote-debugging-port=9222']

    for option in options:
        browser_options.add_argument(option)

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=browser_options,)
    driver.implicitly_wait(1) # wait time in seconds to allow loading of elements
    driver.set_window_position(0, 0)
    driver.maximize_window()
    return driver

def connect_to_existing_browser():
    
    # Configure Selenium to connect to the existing Chrome session
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    
    try:
        # Connect to the existing Chrome session
        driver = webdriver.Chrome(options=chrome_options)
        print(f"Connected to existing browser")
        
        
        if driver:
        # Check if already on LinkedIn
            if "python" not in driver.current_url:
                print("Navigating to LinkedIn login page...") # uncomment the link below to navigate to the Python Selenium page
                #driver.get("https://selenium-python.readthedocs.io/locating-elements.html")
            else:
                print("You are already on Python Selenium Site.")
        else:
            print("Failed to connect to an existing browser session.")


        return driver
    except Exception as e:
        print(f"Error connecting to existing browser: {e}")
        return None

def validate_yaml(yaml_file_path):
    with open(yaml_file_path, 'r') as stream:
        try:
            parameters = yaml.safe_load(stream)
            
        except yaml.YAMLError as exc:
            raise exc

    mandatory_params = ['email',
                        'password',
                        'disableAntiLock',
                        'remote',
                        'lessthanTenApplicants',
                        'experienceLevel',
                        'jobTypes',
                        'date',
                        'positions',
                        'locations',
                        'residentStatus',
                        'distance',
                        'outputFileDirectory',
                        'checkboxes',
                        'universityGpa',
                        'languages',
                        'experience',
                        'personalInfo',
                        'eeo',
                        'uploads']

    for mandatory_param in mandatory_params:
        if mandatory_param not in parameters:
            raise Exception(mandatory_param + ' is not defined in the config.yaml file!')

    assert validate_email(parameters['email'])
    assert len(str(parameters['password'])) > 0
    assert isinstance(parameters['disableAntiLock'], bool)
    assert isinstance(parameters['remote'], bool)
    assert isinstance(parameters['lessthanTenApplicants'], bool)
    assert isinstance(parameters['residentStatus'], bool)
    assert len(parameters['experienceLevel']) > 0
    experience_level = parameters.get('experienceLevel', [])
    at_least_one_experience = False

    for key in experience_level.keys():
        if experience_level[key]:
            at_least_one_experience = True
    assert at_least_one_experience

    assert len(parameters['jobTypes']) > 0
    job_types = parameters.get('jobTypes', [])
    at_least_one_job_type = False
    for key in job_types.keys():
        if job_types[key]:
            at_least_one_job_type = True

    assert at_least_one_job_type
    assert len(parameters['date']) > 0
    



    
    checkboxes = parameters.get('checkboxes', [])
    assert isinstance(checkboxes['driversLicence'], bool)
    assert isinstance(checkboxes['requireVisa'], bool)
    assert isinstance(checkboxes['legallyAuthorized'], bool)
    assert isinstance(checkboxes['certifiedProfessional'], bool)
    assert isinstance(checkboxes['urgentFill'], bool)
    assert isinstance(checkboxes['commute'], bool)
    assert isinstance(checkboxes['backgroundCheck'], bool)
    assert isinstance(checkboxes['securityClearance'], bool)
    assert 'degreeCompleted' in checkboxes
    assert isinstance(parameters['universityGpa'], (int, float))

    languages = parameters.get('languages', [])
    language_types = {'none', 'conversational', 'professional', 'native or bilingual'}
    for language in languages:
        assert languages[language].lower() in language_types

    experience = parameters.get('experience', [])
    for tech in experience:
        assert isinstance(experience[tech], int)
    assert 'default' in experience

    assert len(parameters['personalInfo'])
    personal_info = parameters.get('personalInfo', [])
    for info in personal_info:
        assert personal_info[info] != ''

    assert len(parameters['eeo'])
    eeo = parameters.get('eeo', [])
    for survey_question in eeo:
        assert eeo[survey_question] != ''

    return parameters

def export_data_organiser(root_path):

    
    keep_files   = ["uncover_questions.txt"]
    keep_folders = ["tempforms", "apply_status", "errors", "discard_company", "uncover_questions" ] 
    
    def create_history_of_path(root_path):
        """  create a history of root path files and folders """
        all_files = []
        all_folders = []

        for dirpath, dirnames, filenames in os.walk(root_path):
        
            all_folders.append(dirpath)
            for filename in filenames:
                all_files.append(os.path.join(dirpath, filename))
        
        return all_files, all_folders
    
    def delete_files_except_keep_files(keep_files, all_files):

        for line in all_files:
            
                if line.split("\\")[-1] not in keep_files:
                
                    #print(f"Deleted file : {line.split("\\")[-1]} ")
                    os.remove(line)

                else:
                    #print("------------------------------> Keep   file : ", {line.split("\\")[-1]})
                    continue
    
    def delete_folders_except_keep_folders(keep_folders, all_folders):


        split_nested_folder = lambda folder : folder.split("/")
        keep_folders_details = [fold for folder in keep_folders for fold in split_nested_folder(folder)]


        already_folders = []
        for line in all_folders:
                if line.split("\\")[-1] not in keep_folders_details:
                    # print("folder name : ", line.split("\\")[-1])
                    try:
                        os.removedirs(line)
                        #print(f"Deleted folder : {line.split("\\")[-1]} ")

                    except:
                        #print("------------------------------> Keep   folder : ", {line.split("\\")[-1]})
                        already_folders.append(line.split("\\")[-1])
                        continue

        return already_folders
                    
   
    all_files, all_folders = [],[]
    # if root path not exist then create it
    if not os.path.exists(root_path):

        os.makedirs(root_path)
        
    else:                                                                       
        all_files, all_folders = create_history_of_path(root_path)
    
  

    delete_files_except_keep_files(keep_files, all_files)
    already_folders = delete_folders_except_keep_folders(keep_folders, all_folders)


    # create folder :
    for folder in keep_folders:
        if folder not in already_folders:
            if not os.path.exists(root_path +"//"+ folder):
                os.makedirs(root_path +"//"+ folder)


   
if __name__ == '__main__':

    subprocess.run("pip freeze > requirements.txt", shell=True, check=True)



    yaml_file_path = "config.yaml"     
    parameters = validate_yaml(yaml_file_path)

    export_data_organiser(parameters["outputFileDirectory"])
    
    browser = connect_to_existing_browser()

    bot = LinkedinZ(parameters, browser)
    # bot.login()
    #bot.security_check()
    bot.start_applying()
   
    
