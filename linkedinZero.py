import time, random, pyautogui, traceback, sys
import inspect
from datetime import datetime, timedelta
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from datetime import date, datetime
from itertools import product
from selenium.common.exceptions import NoSuchElementException
import json
from variable_values import css_codes





class LinkedinZ:
    def __init__(self, parameters, driver):
        self.browser = driver
        self.parameters = parameters
        self.email = parameters['email']
        self.password = parameters['password']
        self.disable_lock = parameters['disableAntiLock']
        self.company_blacklist = parameters.get('companyBlacklist', []) or []
        self.title_blacklist = parameters.get('titleBlacklist', []) or []
        self.poster_blacklist = parameters.get('posterBlacklist', []) or []
        self.positions = parameters.get('positions', [])
        self.locations = parameters.get('locations', [])
        self.residency = parameters.get('residentStatus', [])
        self.base_search_url = self.get_base_search_url(parameters)
        self.seen_jobs = []
        self.file_name = "../output_"
        self.unprepared_questions_file_name = "../unprepared_questions"
        self.output_file_directory = parameters['outputFileDirectory']
        self.resume_dir = parameters['uploads']['resume']
        if 'coverLetter' in parameters['uploads']:
            self.cover_letter_dir = parameters['uploads']['coverLetter']
        else:
            self.cover_letter_dir = ''
        self.checkboxes = parameters.get('checkboxes', [])
        self.university_gpa = parameters['universityGpa']
        self.salary_minimum = parameters['salaryMinimum']
        self.notice_period = int(parameters['noticePeriod'])
        self.languages = parameters.get('languages', [])
        self.experience = parameters.get('experience', [])
        self.personal_info = parameters.get('personalInfo', [])
        self.eeo = parameters.get('eeo', [])
        self.experience_default = int(self.experience['default'])
        self.maintenance = True                 # True for debuging and maintenancing, Fulse for lunching
        self.log_main_functions_flag = True     # True For print main Function Status
        self.log_submain_functions_flag = True  # True For print submain Function Status 
        self.log_more_informations_flag = True
        self.log_error_message_flag = True

    def log_main_functions(func):
        def wrapper(self, *args, **kwargs):
            if self.log_main_functions_flag:
                print("\033[92m" + "+" * 40 + f" Start  Function: {func.__name__}" + "\033[0m")  # Green
            result = func(self, *args, **kwargs)
            if self.log_main_functions_flag:
                print("\033[94m" + "-" * 40 + f" Finish Function: {func.__name__}" + "\033[0m")  # Blue
            return result
        return wrapper
    
    def log_submain_functions(func):
        def wrapper(self, *args, **kwargs):
            if self.log_submain_functions_flag:
                print("\033[90m" + "+" * 10 + f" Start  Function: {func.__name__}" + "\033[0m")  # Green
            result = func(self, *args, **kwargs)
            if self.log_submain_functions_flag:
                print("\033[90m" + "-" * 10 + f" Finish Function: {func.__name__}" + "\033[0m")  # Blue
            return result
        return wrapper

    def log_more_informations(self, function, value_description, value):
        if  self.log_more_informations_flag:
            print("\033[0m" + function + ";" + str(value_description) + str(value)  + "\033[0m")
            
            
    

    
    # extract class
    @log_submain_functions
    def get_label_info(self, element):
        """Extract label text using both explicit labels and parent/sibling text"""
        # Try to find explicit label
        element_id = element.get_attribute('id')
        if element_id:
            label = self.browser.find_elements(By.CSS_SELECTOR, f'label[for="{element_id}"]')
            if label:
                return label[0].text.strip()
        
        # Look for parent label
        parent_label = element.find_elements(By.XPATH, "./ancestor::label")
        if parent_label:
            return parent_label[0].text.strip()
        
        return ""
    
    @log_submain_functions
    def get_question_text(self, element):
        """Get question text from fieldset/legend or nearest heading"""
        # Check for fieldset/legend
        fieldset = element.find_elements(By.XPATH, "./ancestor::fieldset")
        if fieldset:
            legend = fieldset[0].find_elements(By.TAG_NAME, "legend")
            if legend:
                return legend[0].text.strip()
        
        # Look for nearest heading
        headings = element.find_elements(
            By.XPATH, 
            "./preceding::h1[1]|./preceding::h2[1]|./preceding::h3[1]|./preceding::h4[1]"
        )
        if headings:
            return headings[-1].text.strip()
        
        return ""
    
    @log_submain_functions
    def extract_text_fields(self, container):
        """Extract all text input fields"""
        text_fields = {}
        inputs = container.find_elements(By.CSS_SELECTOR, 'input[type="text"], input[type="email"], input[type="password"]')
        
        warning = ""
        for index, input_field in enumerate(inputs):

            # Find Error binded next to the question
            error_message_id = input_field.get_attribute(css_codes["field_content_warning_message"]) 
            
            if error_message_id:
                error_message = self.browser.find_element(By.ID, error_message_id)
                if error_message.is_displayed():
                    warning = error_message.text
            else:
                warning == ""
                error_message_id == ""

            info = {
                "type": input_field.get_attribute("type"),
                "classes": input_field.get_attribute("class"),
                "label": self.get_label_info(input_field),
                "required": input_field.get_attribute("required") is not None,
                "id": input_field.get_attribute("id"),
                "error_message_id": error_message_id,
                "warning" : warning,
            }
            text_fields[f"field_{index}"] = info
            
        return text_fields
    
    @log_submain_functions
    def extract_radio_buttons(self, container):
        """Extract all radio button groups"""
        radio_fields = {}
        radio_groups = {}
        
        # Group radio buttons by name attribute
        radios = container.find_elements(By.CSS_SELECTOR, 'input[type="radio"]')
        for radio in radios:
            name = radio.get_attribute("name")
            if name not in radio_groups:
                radio_groups[name] = []
            radio_groups[name].append(radio)
        
        for index, (name, group) in enumerate(radio_groups.items()):
            options = []
            for radio in group:
                options.append({
                    "value": radio.get_attribute("value"),
                    "label": self.get_label_info(radio)
                })
            

            info = {
                "type": "radio",
                "question": self.get_question_text(group[0]),
                "classes": group[0].get_attribute("class"),
                "label": self.get_label_info(group[0]),
                "required": group[0].get_attribute("required") is not None,
                "options": options,
                "id": group[0].get_attribute("id")
            }
            radio_fields[f"field_{index}"] = info
            
        return radio_fields
    
    @log_submain_functions
    def extract_checkboxes(self, container):
        """Extract all checkboxes"""
        checkboxes = {}
        checkbox_elements = container.find_elements(By.CSS_SELECTOR, 'input[type="checkbox"]')
        
        for index, checkbox in enumerate(checkbox_elements):
            info = {
                "type": "checkbox",
                "question": self.get_question_text(checkbox),
                "classes": checkbox.get_attribute("class"),
                "label": self.get_label_info(checkbox),
                "required": checkbox.get_attribute("required") is not None,
                "id": checkbox.get_attribute("id")
            }
            checkboxes[f"field_{index}"] = info
            
        return checkboxes
    
    @log_submain_functions
    def extract_dropdowns(self, container):
        """Extract all dropdown/select elements"""
        dropdowns = {}
        select_elements = container.find_elements(By.TAG_NAME, "select")
        
        for index, select in enumerate(select_elements):
            options = []
            for option in select.find_elements(By.TAG_NAME, "option"):
                options.append({
                    "text": option.text,
                    "value": option.get_attribute("value")
                })
                
            info = {
                "type": "select",
                "classes": select.get_attribute("class"),
                "label": self.get_label_info(select),
                "required": select.get_attribute("required") is not None,
                "options": options,
                "id": select.get_attribute("id")
            }
            dropdowns[f"field_{index}"] = info
            
        return dropdowns
    
    @log_submain_functions
    def extract_buttons(self, container):
        """Extract all buttons"""
        buttons = {}
        button_elements = container.find_elements(By.CSS_SELECTOR, 'button, input[type="submit"], input[type="button"]')
        
        for index, button in enumerate(button_elements):
            info = {
                "type": button.tag_name,
                "classes": button.get_attribute("class"),
                "label": button.text or button.get_attribute("value"),
                "required": False,
                "id": button.get_attribute("id")
            }
            buttons[f"field_{index}"] = info
            
        return buttons
    
    @log_submain_functions
    def extract_headers(self, container):
        """Extract header tags (h2, h3)"""
        headers = {}
        for tag in ['h2', 'h3']:
            header_elements = container.find_elements(By.TAG_NAME, tag)
            for index, header in enumerate(header_elements):
                info = {
                    "type": tag,
                    "classes": header.get_attribute("class"),
                    "text": header.text,
                    "required": False,
                    "id": header.get_attribute("id")
                }
                headers[f"field_{tag}{index}"] = info
                
        return headers
    
    @log_submain_functions
    def extract_upload_fields(self, container):
        """Extract file upload fields"""
        upload_fields = {}
        file_inputs = container.find_elements(By.CSS_SELECTOR, 'input[type="file"]')
        
        for index, upload in enumerate(file_inputs):
            info = {
                "type": "file",
                "classes": upload.get_attribute("class"),
                "title": self.get_question_text(upload),
                "label": self.get_label_info(upload),
                "required": upload.get_attribute("required") is not None,
                "id": upload.get_attribute("id")
            }
            upload_fields[f"field_{index}"] = info
            
        return upload_fields
    
    @log_submain_functions
    def get_footer_details(self):
        """
        Finds details inside the footer, handling cases where a checkbox is not present.
        """
        

        footer_components = {}
        try:
            footer = self.browser.find_element(By.TAG_NAME, "footer")
        except NoSuchElementException:
            
            self.log_more_informations(inspect.currentframe().f_code.co_name, "Warning: No footer element found on this page." ,"")
            return footer_components #Return empty dict if no footer

        footer_details = {
            "type": footer.get_attribute("role"),
            "class": footer.get_attribute("class"),
            "id": footer.get_attribute("id"),
            "label" : ""
        }
        footer_components["footer_details"] = footer_details

        try:
            checkbox = footer.find_element(By.CSS_SELECTOR, "input[type='checkbox']")
            related_text_element = checkbox.find_element(By.XPATH, "following-sibling::*")
            related_text = related_text_element.text if related_text_element else None #Handle cases where the element is not found
            checkbox_info = {
                "type": "checkbox",
                "label": "Checkbox",
                "classes": checkbox.get_attribute("class"),
                "id": checkbox.get_attribute("id"),
                "related text": related_text,
            }
            footer_components["checkbox"] = checkbox_info
        except NoSuchElementException:
            pass
              # Checkbox is not present, continue without adding to the dictionary

        #footer_components["buttons"] = {}  # Initialize buttons dictionary
        buttons = footer.find_elements(By.TAG_NAME, "button")

        for index, button in enumerate(buttons):
            button_info = {
                "type": "button",
                "label": button.text,
                "classes": button.get_attribute("class"),
                "id": button.get_attribute("id"),
            }
            #footer_components["buttons"][str(index)] = button_info #Convert index to string to use as key
            footer_components[str(index)] = button_info #Convert index to string to use as key

        
        return footer_components

    @log_main_functions
    def extract_all_components(self, form_number, button_text):
        
        
        """Main method to extract all components"""

                
        
        form_data = {"fields" : {} , "title" : ""}

        if button_text.lower() == ("next") :
           
            forms = self.browser.find_elements(By.TAG_NAME, "form")
            for form_index, form in enumerate(forms):
                if form_index != form_number :
                    continue
                
                

                element_counter = 0
                if text_fields := self.extract_text_fields(form):
                    for key, value in text_fields.items():  
                        form_data["fields"][f"field_{element_counter}"] = value 
                        element_counter += 1

                if radio_buttons := self.extract_radio_buttons(form):
                    for key, value in radio_buttons.items():  
                        form_data["fields"][f"field_{element_counter}"] = value 
                        element_counter += 1

                if checkboxes := self.extract_checkboxes(form):
                    for key, value in checkboxes.items():  
                        form_data["fields"][f"field_{element_counter}"] = value 
                        element_counter += 1

                if dropdowns := self.extract_dropdowns(form):
                    for key, value in dropdowns.items():  
                        form_data["fields"][f"field_{element_counter}"] = value 
                        element_counter += 1

                if buttons := self.extract_buttons(form):
                    for key, value in buttons.items():  
                        if value["label"]:
                            form_data["fields"][f"field_{element_counter}"] = value 
                            element_counter += 1

                if upload_fields := self.extract_upload_fields(form):
                    for key, value in upload_fields.items():  
                        form_data["fields"][f"field_{element_counter}"] = value 
                        element_counter += 1
              
                if headers := self.extract_headers(form):
                   
                    header = list(headers.values())[0]["text"]
                    if header == "":
                       
                        self.log_more_informations(inspect.currentframe().f_code.co_name, " the header is empty, title = no_title" ,"")
                        
                        header = "no_title"
                    form_data["title"] = header.lower().replace(" ", "_")
                    element_counter += 1
                


            
            self.log_more_informations(inspect.currentframe().f_code.co_name, "-----------------> Form title is: ", form_data["title"])

            with open(f"./export_data/tempforms/{form_data["title"]}_form_components_details.json", "w") as f:
                            json.dump(form_data, f, indent=4)

            
                
            return form_data["title"], form_data
            
       
        if "review"  in button_text.lower() :

            form_data = {"fields" : {} , "title" : "review"}
            element_counter = 0

            footer_components = self.get_footer_details()
            

            footer_details = footer_components["footer_details"]

            for index , key in enumerate(footer_components) :
                form_data["fields"][f"field_{index}"] = footer_components[key]
                
            form_data["footer_details"] = footer_details

            

            try:
                print(">"*100,"value[type]", type(value["type"]), value["type"])
                footer_botton_list = [value["label"] for value in footer_components["footer_details"].values() if value["type"]=="button" ]
                self.log_more_informations(inspect.currentframe().f_code.co_name, "footer_botton_list:\n", footer_botton_list)

            except Exception:
              
                self.log_more_informations(inspect.currentframe().f_code.co_name, " this is not a review form ", "")
                self.log_error_to_file(self.log_error_message_flag)
            
            
            
       

    
  



        if form_data["title"]:
               title = form_data["title"]
        else:
                form_data["title"] = "no_title"
                title = form_data["title"]

        
        with open(f"./export_data/tempforms/{title}_form_components_details.json", "w") as f:
                        json.dump(form_data, f, indent=4)
    


        self.log_more_informations(inspect.currentframe().f_code.co_name, "  -----------------> Form title is: ", form_data["title"])
            
        return title, form_data
    
    
    def get_base_search_url(self, parameters):
        remote_url = ""
        lessthanTenApplicants_url = ""

        if parameters.get('remote'):
            remote_url = "&f_WT=2"
        else:
            remote_url = ""
            # TO DO: Others &f_WT= options { WT=1 onsite, WT=2 remote, WT=3 hybrid, f_WT=1%2C2%2C3 }

        if parameters['lessthanTenApplicants']:
            lessthanTenApplicants_url = "&f_EA=true"

        level = 1
        experience_level = parameters.get('experienceLevel', [])
        experience_url = "f_E="
        for key in experience_level.keys():
            if experience_level[key]:
                experience_url += "%2C" + str(level)
            level += 1

        distance_url = "?distance=" + str(parameters['distance'])

        job_types_url = "f_JT="
        job_types = parameters.get('jobTypes', [])
        # job_types = parameters.get('experienceLevel', [])
        for key in job_types:
            if job_types[key]:
                job_types_url += "%2C" + key[0].upper()

        date_url = ""
        dates = {"all time": "", "month": "&f_TPR=r2592000", "week": "&f_TPR=r604800", "24 hours": "&f_TPR=r86400"}
        date_table = parameters.get('date', [])
        for key in date_table.keys():
            if date_table[key]:
                date_url = dates[key]
                break

        easy_apply_url = "&f_AL=true"

        extra_search_terms = [distance_url, remote_url, lessthanTenApplicants_url, job_types_url, experience_url]
        extra_search_terms_str = '&'.join(
            term for term in extra_search_terms if len(term) > 0) + easy_apply_url + date_url

        return extra_search_terms_str

    @log_submain_functions 
    def avoid_lock(self):
        if self.disable_lock:
            return

        pyautogui.keyDown('ctrl')
        pyautogui.press('esc')
        pyautogui.keyUp('ctrl')
        time.sleep(1.0)
        pyautogui.press('esc')
    
    @log_submain_functions
    def next_job_page(self, position, location, job_page):  # Uncomment refresh page
        self.browser.get("https://www.linkedin.com/jobs/search/" + self.base_search_url +
                            "&keywords=" + position + location + "&start=" + str(job_page * 25))
        self.avoid_lock()

    @log_submain_functions 
    def scroll_slow(self, scrollable_element, start=0, end=3600, step=100, reverse=False):
        if reverse:
            start, end = end, start
            step = -step

        for i in range(start, end, step):
            self.browser.execute_script("arguments[0].scrollTo(0, {})".format(i), scrollable_element)
            time.sleep(random.uniform(0.3, 1.6))

    @log_main_functions
    def start_applying(self):
        
        now = datetime.now().strftime("%H:%M:%S")
        print(f"Starting the application process at {now} ...")


        searches = list(product(self.positions, self.locations))
        random.shuffle(searches)

        page_sleep = 0
        

        for (position, location) in searches:
            location_url = "&location=" + location
            job_page_number = -1

            print("Starting the search for " + position + " in " + location + ".")
            
            

            try:
                while True:
                    page_sleep += 1
                    job_page_number += 1
                    print("Going to job page " + str(job_page_number))


                    self.next_job_page(position, location_url, job_page_number)
                    time.sleep(random.uniform(1.5, 3.5))
                    print("Starting the application process for this page...")


                    location = location.replace(" ", "_").lower()
                    position = position.replace(" ", "_").lower()
                    str_location_position_page = f"{location}_{position}_{str(job_page_number+1)}"
                    time.sleep(random.uniform(10,15))
                    self.apply_jobs(str_location_position_page)
                    print("Job applications on this page have been successfully completed.")
                    
                    delay = 2 # minutes

                    now = datetime.now()
                    start_time = now + timedelta(minutes = delay)
                    print("Start time: ", start_time.strftime("%H:%M:%S"))

                    for i in range (delay):
                        print(delay - i ," Minutes to lunch ... ", end="\r")
                        time.sleep(60)

                
  
            except Exception:
                self.log_error_to_file(self.log_error_message_flag)
                
    
    @log_main_functions
    def apply_jobs(self, str_location_position_page):
        """
        a function to apply jobs on the job list page,
        after finishing, need to moving to next page by a external function
        """
        
        
        
        applied_counter = 1
        applied_history = {}
        easy_apply_counter = 1
        easy_apply_history = {}
        discard_companies = []
        

        while True:
           
            try:
                status = ""
                jobs_part_status = self.scroll_job_list_section(css_codes["job_lists"])
                job_list = jobs_part_status[1]


                process_on_jobs_container = True
                if process_on_jobs_container:

                    
                    
                    
                    for index, job_tile in enumerate(job_list):
                        

                        if job_tile.text:
                           pass  
                        else:

                            self.no_jobtile_no_title()  # Need to cover by try except
                            break

                        applied_history, applied_counter = self.log_applied_job_export_to_file(job_tile.text, applied_history, applied_counter, str_location_position_page )
                        push_easy_apply_button_flag, easy_apply_history, easy_apply_counter, company = self.log_easy_apply_job_export_to_file(job_tile.text, easy_apply_history, easy_apply_counter, discard_companies, str_location_position_page )
                        
                        if push_easy_apply_button_flag:

                            job_tile.click()
                            time.sleep(6)

                            easy_apply_status = self.button_easy_apply(css_codes["apply_button"])
                            if easy_apply_status['process'] == ('done'):  
                                process_on_forms = True
                    
                            else:
                                process_on_forms = False                            
                                continue  
                        else:
                            process_on_forms = False                            
                            continue  
                                    
                    
                                    
                                
                        if process_on_forms:

                            
                            button_text = "next"
                            title_counter = {}
                            current_button_counter = {}


                            submit_application_text = 'Submit application'
                            while submit_application_text != button_text:

                                try:
                                    
                                
                                    # extracts all field information into a structured dictionary
                                    form_title, analyzed_form_components_details = self.extract_all_components( 0, button_text )

                                    if form_title == ("no_title"):
                                        
                                        self.no_jobtile_no_title()
                                        process_on_forms = False
                                        button_text = "next"
                                        break
                                    

                                    # preparing answers for form's questions
                                    answerd_form = self.form_answering(analyzed_form_components_details)


                                    # fill the all fields of form and push the next button
                                    button_text = self.fill_up_form(answerd_form)                             
         
                                    if button_text in submit_application_text :
                                        
                                        time.sleep(10)
                                        next_button = self.browser.find_element(By.CLASS_NAME, css_codes["close_filled_form"])
                                        next_button.click()
                                        
                                        time.sleep(random.uniform(4,6))


                                    
                                    time.sleep(10)

                                    status = self.save_or_discard_referesh(title_counter, current_button_counter, form_title, button_text, company, discard_companies)
                                    
                                    if status == ("exceeded"):
                                        self.log_more_informations(inspect.currentframe().f_code.co_name, "-----------------> Exceed happend", "")
                                        
                                        time.sleep(15)
                                        button_text = ""
                                        process_on_forms = False
                                        break 
                                       
                                    


                                    

                                    
                                except Exception as e:
                                    self.log_more_informations(inspect.currentframe().f_code.co_name, "There are some error inside process_on_form \n", "")
                                    self.log_error_to_file(self.log_error_message_flag)
                                        

                    else: 
                            
                            self.log_more_informations(inspect.currentframe().f_code.co_name, "@"*40, " --->End of jobs in the page\n\n\n")
                            time.sleep(20)
                            break      
                                    


                                
           
            except Exception:
                
                self.log_more_informations(inspect.currentframe().f_code.co_name, "Something is wrong with main while...", "")
                self.log_error_to_file(self.log_error_message_flag)
                
               

    @log_submain_functions
    def refresh_page(self):
                                
                               # Need to improve by saving the url before coming inside the function

                                saved_url = self.browser.current_url
                                self.browser.get("https://www.linkedin.com")
                                time.sleep(10)
                                self.browser.get(saved_url)
                                time.sleep(15)

                                """
                                searches = list(product(self.positions, self.locations))
                                random.shuffle(searches)

                                page_sleep = 0
                                
                                for (position, location) in searches:
                                    location_url = "&location=" + location
                                    job_page_number = -1

                                print("Starting the search for " + position + " in " + location + ".")
                                self.next_job_page(position, location_url, job_page_number)
                                """
                              
    
    @log_submain_functions
    def scroll_job_list_section(self, strClassName):
            
        """
        Scrolls the job list section of the linkedin page on left side. 
        Original class name is 'scaffold-layout__list', documents_pic/1.png.

        """

        
        report = {"process": "" , "error": ""}
         
        while True:
            time.sleep(random.uniform(5,10.6))
            try:
                parent_div = self.browser.find_element(By.CLASS_NAME, strClassName)     # documents_pic\1.png
                sub_classes = parent_div.find_elements(By.XPATH, ".//*[contains(@class, '')]")
                
                """
                Leave this code here for debugging and finding the magic class
                # for i, obj in enumerate(sub_classes):
                #     print(f"{i}: {obj.get_attribute("class")}")
                #     time.sleep(3)
                """



                magic_class = sub_classes[15].get_attribute("class")                               # documents_pic\4.png
                self.log_more_informations(inspect.currentframe().f_code.co_name, "-----------------> The magic_class value: ", magic_class)
             
                
                scrollable_element = self.browser.find_element(By.CLASS_NAME, magic_class)  
                scrollable_element.click()
                self.scroll_slow(scrollable_element, step=400, reverse=True)
                job_list = self.browser.find_elements(By.CSS_SELECTOR, f".{strClassName} li")

                
            except:
                self.log_error_to_file(self.log_error_message_flag)
                # Refresh the page
                self.log_more_informations(inspect.currentframe().f_code.co_name, " -----------------> Refresh the page is going on ","")
                self.refresh_page()
                time.sleep(random.uniform(15,20))

            else:
                if scrollable_element and job_list:
                    self.log_more_informations(inspect.currentframe().f_code.co_name, "----------------->" , " scrollable_element and job_list   : available")
                    break



        

        report = {"process": "accept" , "error": ""}
        return [report , job_list]

    @log_submain_functions
    def fill_dropdown(self, str_element_id, int_index_Answer, lable_name) :
    
        """
          a function to fill dropdown field by index 
          str_element_ID : the ID of element
          int_index_Answer :
          output:

        """
        
        
        self.log_more_informations(inspect.currentframe().f_code.co_name, "lable name: ", lable_name)
        
        report = {"process": "" , "error": ""}
        
        
        try:
            time.sleep(random.uniform(3.5,5.5))
            dropdown = self.browser.find_element(By.ID, str_element_id)

            # Create a Select object from the dropdown element
            select = Select(dropdown)

            # Select the option by index (index starts at 0, so n)
            select.select_by_index(int_index_Answer)
            # select.select_by_visible_text("vaxrei@gmail.com")

            
            report = {"process": "done" , "error": ""}
            return report

        except Exception as e:   

            self.log_error_to_file(self.log_error_message_flag)
            self.log_more_informations(inspect.currentframe().f_code.co_name, "something is wrong with the function dropdown", "")

            error_details = traceback.format_exc()
            report = {"process": "failed" , "error": error_details}
            return report

    
    @log_submain_functions
    def fill_textField(self, str_element_id, str_answer, lable_name):

        """
          a function to fill Text field by string answer 
          str_element_ID : the ID of element
          strAnswer : answer will put inside the field
          output:

        """  
        
        self.log_more_informations(inspect.currentframe().f_code.co_name, "lable name: ", lable_name)

        report = {"process": "" , "error": ""}
        try:
            time.sleep(random.uniform(3.5,5.5))
            # Find the text input field by its ID
            text_field = self.browser.find_element(By.ID, str_element_id)

            # Clear any existing text in the field (important to avoid appending)
            text_field.clear()

            # Send the desired text to the field
            text_field.send_keys(str_answer)



            
            
            

            report = {"process": "done" , "error": ""}
            return report




        except Exception:   
            self.log_error_to_file(self.log_error_message_flag)
            self.log_more_informations(inspect.currentframe().f_code.co_name, "something is wrong with function : fill_textField", "")

            error_details = traceback.format_exc()  # Get full traceback
            report = {"process": "failed" , "error": error_details}
            return report
       


    @log_submain_functions
    def button_easy_apply(self, strClassName):

        """
        Clicks the Easy Apply button by class name.
        
        strClassName: the class name for 'easy apply' button. Original class name is 'jobs-apply-button', documents_pic/5.png.
        
        
        """
        
        
        
        time.sleep(random.uniform(3.5, 6.5))
        report = {"process": "" , "error": ""}
        try:
            easy_apply_button = self.browser.find_element(By.CLASS_NAME, strClassName)  # documents_pic\5.png
            if easy_apply_button:
                easy_apply_button.click()
                time.sleep(random.uniform(4,6))


            
            report = {"process": "done" , "error": ""}
            return report 
        except:   
            
           
            self.log_more_informations(inspect.currentframe().f_code.co_name, "The Easy Apply button doesn't load or the job has already applied", "")
            report = {"process": "failed" , "error": ""}
            return report
            


    @log_submain_functions
    def button_next(self, element_id, str_lable):

        """
        a function to push the next button
        ags:
          element_id: the "id" of button. documents_pic/6.png
        
        return: 
           button_text is the lable of next button.
           output is str
           
        
        """

        self.log_more_informations(inspect.currentframe().f_code.co_name, "lable name: ", str_lable)
        
        report = {"process": "" , "error": ""}
        time.sleep(random.uniform(4.2,6.3))
        try:
            next_button = self.browser.find_element(By.CLASS_NAME, element_id)
            next_button.click()
             
            report = {"process": "done" , "error": ""}
            return report
            
        except Exception as e:   
            self.log_error_to_file(self.log_error_message_flag)
            self.log_more_informations(inspect.currentframe().f_code.co_name, "Something is wrong with the function", "")

            error_details = traceback.format_exc()  # Get full traceback
            report = {"process": "failed" , "error": error_details}
            return report




    @log_submain_functions
    def select_radio_button(self, question: str, options: dict):
        
        """
        #######################/////******** problem for clicking because of qutations and signs inside question. delete them YYYYYYYYYYYYYYYY
        Selects the radio button based on the question text.

        Parameters:
        - question (str): The question text associated with the radio buttons.
        - options (list): A list of dictionaries where each dictionary contains:
                          { "value": "value", "label": "label" }.

        Raises:
        - NoSuchElementException: If the question or matching radio button cannot be found.
        """

        self.log_more_informations(inspect.currentframe().f_code.co_name, "Question: ", question)
        report = {"process": "" , "error": ""}
     

       
        try:

            def escape_xpath_text(text):
                if "'" in text and '"' in text:
                    # If the text contains both single and double quotes, use concat() in XPath
                    return 'concat("' + text.replace('"', '", \'"\', "') + '")'
                elif "'" in text:
                    # If the text contains only single quotes, use double quotes around the text
                    return f'"{text}"'
                else:
                    # If the text contains no single quotes, use single quotes around the text
                    return f"'{text}'"

            # Refine the question text
            escaped_question = escape_xpath_text(question)

            # Locate the container with the question text
            question_container = self.browser.find_element(By.XPATH, f"//*[contains(text(), {escaped_question})]/ancestor::div[1]")

            # Find all radio buttons in the same container
            radio_buttons = question_container.find_elements(By.XPATH, ".//input[@type='radio']")
            

            for key in options.keys():
                
                value_to_match = options["value"] 
                label_to_match = options["label"] 

                for radio_button in radio_buttons:
                    # Get the radio button's value and associated label
                    value = radio_button.get_attribute("value")
                    label_id = radio_button.get_attribute("id")
                    label = question_container.find_element(By.XPATH, f".//label[@for='{label_id}']")

                    if value in value_to_match and label.text in label_to_match:
                    

                        start_time = time.time()
                        duration = 3  # Click for 10 seconds

                        while time.time() - start_time < duration:
                            label.click()
                            time.sleep(0.5)

                        
                        report = {"process": "done" , "error": ""}
                        return report



        except Exception:   
            self.log_error_to_file(self.log_error_message_flag)
            error_details = traceback.format_exc()  # Get full traceback
            report = {"process": "failed" , "error": error_details}
            
        
            
            return report

    @log_main_functions      
    def fill_up_form(self, dict_components_details):
        """
        fill_up_form is a function to fill a form with all fields inside
        dict_components_details: is a dictionary come from the output of 'analyze_form' function, included components details such as id, class name, lable, ...

        output: filling form and pushing next button 
        """

        self.log_more_informations(inspect.currentframe().f_code.co_name, "\ndict_components_details:\n " , dict_components_details)
        
            
        
        button_text = ""
        comp = dict_components_details
        tracking = {}
        info = {
            "index" : "",
            "key": "",
            "id" : "",
            "answer": "",
            "label": ""
        }




        for index , key in enumerate(comp.keys()):
  

            # dropdown
            try:
                if "dropdown" in comp[key]["function"]:
                    report = self.fill_dropdown(comp[key]["str_element_id"], comp[key]["int_index_Answer"], comp[key]["lable_name"])
                    
            except :
                self.log_more_informations(inspect.currentframe().f_code.co_name, "dropdown function doesn't work","")
                self.log_error_to_file(self.log_error_message_flag)
                info = {
                        "index" : index,
                        "key": key,
                        "id" : comp[key]["str_element_id"],
                        "answer": comp[key]["int_index_Answer"],
                        "label": comp[key]["lable_name"]
                        }
                tracking["dropdown"] = info
         
                




            # textfield
            try: 
                if "textfield" in comp[key]["function"]:
                    report = self.fill_textField(comp[key]["str_element_id"], comp[key]["str_answer"], comp[key]["lable_name"])

            except:
            
                self.log_more_informations(inspect.currentframe().f_code.co_name, "textfield function doesn't work","")
                info = {
                        "index" : index,
                        "key": key,
                        "id" : comp[key]["str_element_id"],
                        "answer": comp[key]["str_answer"],
                        "label": comp[key]["lable_name"]
                        }
                tracking["textfield"] = info
        
                

            


            # radio
            try:
                if "radio" in comp[key]["function"]:

                    report = self.select_radio_button(comp[key]["question"], comp[key]["options"])
                    
            except:
                
                self.log_more_informations(inspect.currentframe().f_code.co_name, "radio function doesn't work","")
                self.log_error_to_file(self.log_error_message_flag)

                info = {
                        "index" : index,
                        "key": key,
                        "id" : "",
                        "classes" : "",
                        "answer": comp[key]["options"],
                        "label": ""
                        }
                tracking["radio"] = info
           
                
           
            
            
            # checkbox
            try:
                
                if comp[key]["function"] and "checkbox" in comp[key]["function"]:
                    print("comp[key]: " , comp[key])
                    try:
                        checkbox = self.browser.find_element(By.CLASS_NAME, comp[key]["classes"])  # Replace 'checkbox_id' with the actual id

                        time.sleep(random.uniform(3.5,6.5))  
                        if checkbox.is_selected():
                            time.sleep(random.uniform(2.5,4.5))  
                            checkbox.click()  
                            
                
                            
                    except:
                        self.log_more_informations(inspect.currentframe().f_code.co_name, "unmark checkbox doesn't work","")
                        self.log_error_to_file(self.log_error_message_flag)
            except:
                self.log_error_to_file(self.log_error_message_flag)
     
           




            # button
            try:

                if "button" in comp[key]["function"] :
                    report = self.button_next(comp[key]["str_element_id"], comp[key]["lable_name"])
                    button_text = comp[key]["lable_name"]
                    
            except:
                
                self.log_more_informations(inspect.currentframe().f_code.co_name, "button function doesn't work","")
                self.log_error_to_file(self.log_error_message_flag)
                
                info = {
                        "index" : index,
                        "key": key,
                        "id" : comp[key]["str_element_id"],
                        "answer": comp[key]["options"],
                        "label": comp[key]["lable_name"]
                        }
                tracking["buttun"] = info
     
                
        # if len(tracking) >0 :
        #     print("\n\n\n","tracking: " , tracking , "\n\n\n" )
            

        


            
        return button_text
        
    @log_main_functions
    def form_answering(self, analayzed_form):
        """
        to answer the peresent form questions

        """    
        


        contact_answers = {}
        filed_info = {}

        
        data = self.parameters
        for index, field in enumerate(analayzed_form["fields"].values()):

                    

            if "contact" in analayzed_form["title"].lower():


                answer = None
                       
                       
                # Email address
                if any(word == ("email") for word in ((field["label"].lower()).split(" "))):
                        
                    if field["type"] in ("select", "select-one"):
                        answer = 1
                        filed_info = self.answer_organiser(index, field, answer)

                    if field["type"] == ("text"):
                        answer = data["email"]
                        filed_info = self.answer_organiser(index, field, answer)

   
                # Phone country code
                if any(word in ("country", "code") for word in ((field["label"].lower()).split(" "))):

                    if field["type"] in ("select", "select-one"):
                            answer = 1
                            filed_info = self.answer_organiser(index, field, answer)

                    if field["type"] == ("text"):
                        answer = data["personalInfo"]['Phone Country Code']
                        filed_info = self.answer_organiser(index, field, answer)
                
                    
                # Mobile phone number
                if any(word in ("mobile", "phone") for word in ((field["label"].lower()).split(" "))):

                    if field["type"] == ("text"):
                        answer = data['personalInfo']['Mobile Phone Number']
                        filed_info = self.answer_organiser(index, field, answer)

                # Full Name
                if any(word == ("full") for word in ((field["label"].lower()).split(" "))):

                    if field["type"] == ("text"):
                        answer = f"{data["personalInfo"]['First Name']}+ {data["personalInfo"]['Last Name']}"
                        filed_info = self.answer_organiser(index, field, answer)

                # first Name
                if any(word == ("first") for word in ((field["label"].lower()).split(" "))):

                    if field["type"] == ("text"):
                        answer = f"{data["personalInfo"]['First Name']}"
                        filed_info = self.answer_organiser(index, field, answer)
                
                # last Name
                if any(word == ("last") for word in ((field["label"].lower()).split(" "))):

                    if field["type"] == ("text"):
                        answer = f"{data["personalInfo"]['Last Name']}"
                        filed_info = self.answer_organiser(index, field, answer)

                # location
                if any(word == ("location") for word in ((field["label"].lower()).split(" "))):
                        
                    if field["type"] in ("select", "select-one"):
                        answer = 1
                        filed_info = self.answer_organiser(index, field, answer)

                    if field["type"] == ("text"):
                        answer = data["personalInfo"]["City"]
                        filed_info = self.answer_organiser(index, field, answer) 
                            
                if answer is None:
                    filed_info = self.answer_organiser(index, field, answer)

                contact_answers[index] = filed_info 
                        
            if "resume" in analayzed_form["title"].lower():
                pass

            if "additional" in analayzed_form["title"].lower():
                answer = None
                question = field["label"].lower().split(" ")
                
               
                if any(word in ("experience", "how", "many") for word in question):
                       
                        
                    for skill in (data["experience"].keys()):
                        # if skill.lower() in question :
                        #     answer = data["experience"][skill]
                        #     break
                        skill_splited = skill.lower().split(" ")
                        for word in skill_splited:
                            if word in question:
                                answer = data["experience"][skill]
                                break

                
                    if answer is None:
                        answer = data["experience"]["default"]
                        message = f"text-field: {field['label']}"
                        self.write_to_txtfile("./export_data/uncover_questions/uncover_questions.txt", message)
                    
                if any(word in ("salary", "monthly salary") for word in question):
                    answer = data["salaryMinimum"]
                    
                    

                if any(word in ("rate", "day rate") for word in question):
                    answer = round(data["salaryMinimum"]/24)
                   
                if any(word in ("notice", "period") for word in question):
                    answer = data["noticePeriod"]

                if any(word in ("sponsor", "sponsorship") for word in question):
                    answer = data["checkboxes"]["requireVisa"]


                    




                # if answer is None
                # dropdown
                if field["type"] in ("select", "select-one"):
                    answer = 1
                    filed_info = self.answer_organiser(index, field, answer)

                # text
                if field["type"] == ("text"):
                    filed_info = self.answer_organiser(index, field, answer)

                # Radio
                if field["type"] == ("radio"):
                    answer = field["options"][0]
                    filed_info = self.answer_organiser(index, field, answer)


                contact_answers[index] = filed_info 

            if "authorization" in analayzed_form["title"].lower():
                answer = None
                if answer is None:
                    filed_info = self.answer_organiser(index, field, answer)
                                   
            if "review" == analayzed_form["title"].lower():
                      

                        for index, field in enumerate(analayzed_form["fields"].values()):
                          
                            
                             if field["type"] == ("checkbox"):
                                
                            #         filed_info = { 
                            #                     "function":"checkbox",
                            #                     "type" : field["type"],
                            #                     "label": "Unfollow Company",
                            #                     "str_element_id" : "",      
                            #                     "str_element_class" : "t-black--light",
                            #                     "str_answer" : None,
                            #                     "lable_name" : field["label"]
                            #         }

                            #     # if field["type"] in ("button") and any(word in ('next','submit', 'review') for word in field["label"].lower().split(" ")):

                                filed_info = { 
                                            "function":"button",
                                            "type" : field["type"],
                                            "str_element_id" : "artdeco-button--primary",      #(field["classes"].split(" ")[2]), #"artdeco-button--primary",          # field["id"],
                                            "str_element_class" : field["classes"],
                                            "str_answer" : None,
                                            "lable_name" : field["label"]
                                }

                                contact_answers[field["label"]] = filed_info
                      
                   
            # next button    
            if field["type"] == ("button") and any(word in ('next','submit', 'review') for word in field["label"].lower().split(" ")):
                    
                    
                    class_splited = field["classes"].split(" ")
                    class_button = class_splited[2]
                    filed_info = { 
                                "function":"button",
                                "type" : field["type"],
                                "str_element_id" : class_button,      #(field["classes"].split(" ")[2]), #"artdeco-button--primary",          # field["id"],
                                "str_element_class" : class_button,
                                "str_answer" : None,
                                "lable_name" : field["label"]
                    }
                    




                    contact_answers[index] = filed_info         

            #contact_answers[field["label"]] = filed_info  

        
        return contact_answers
    
    @log_submain_functions
    def write_to_txtfile(self, file_name, sentence):
        # Open the file in append mode; create it if it doesn't exist
        with open(file_name, 'a' , encoding="utf-8") as file:
            file.write(sentence + '\n')  # Add the sentence with a newline
    
    @log_submain_functions
    def submit_footer_elements(self, str_footer_role):
        """
        find footer elements and ansewring and submit.
        """
        
    
        try:
            footer_role_name = f"footer[role={str_footer_role}]"  # "presentation"
            # Locate the footer tag with role="presentation"
            footer = self.browser.find_element(By.CSS_SELECTOR, footer_role_name)

            # Find all checkboxes and buttons inside the footer
            checkboxes = footer.find_elements(By.CSS_SELECTOR, 'input[type="checkbox"]')
            buttons = footer.find_elements(By.CSS_SELECTOR, 'button')

            # Extract details of checkboxes
            for checkbox in checkboxes:
                    checkbox_info = {
                    "type": checkbox.get_attribute("type"),
                    "classes": checkbox.get_attribute("class"),
                    "label": checkbox.get_attribute("aria-label") or checkbox.get_attribute("name") or "",
                    "required": checkbox.get_attribute("required") == "true",
                    "validation_message": checkbox.get_attribute("validationMessage"),
                    "hidden": checkbox.get_attribute("hidden") == "true",
                    "id": checkbox.get_attribute("id"),
                    }
                    
                    self.log_more_informations(inspect.currentframe().f_code.co_name, "Checkbox Info: ", checkbox_info)
               
                    

            # Extract details of buttons
            for button in buttons:
                    button_info = {
                    "type": button.get_attribute("type"),
                    "classes": button.get_attribute("class"),
                    "label": button.text or button.get_attribute("aria-label") or "",
                    "hidden": button.get_attribute("hidden") == "true",
                    "id": button.get_attribute("id"),
                    }
                    

        except Exception:
            self.log_error_to_file(self.log_error_message_flag)


        
        try:
            follow_checkbox = self.browser.find_element(By.XPATH,
                                                        "//label[contains(.,\'to stay up to date with their page.\')]").click()
            follow_checkbox.click()
        except:
            pass
       
        
        try:
            self.button_next("artdeco-button--primary", "label")
        except:
          
            self.log_more_informations(inspect.currentframe().f_code.co_name, " Submit button doesn't work", "")

        try:
            scrollable_element = self.browser.find_element(By.CLASS_NAME, "scaffold-layout__list") 
            scrollable_element.click()
        except:
            
            self.log_more_informations(inspect.currentframe().f_code.co_name, " after submit form clicking does not work","")
            self.log_error_to_file(self.log_error_message_flag)



        
        return checkbox_info, button_info
    
    @log_submain_functions
    def answer_organiser(self, index: int, field: dict , answer: any):

        """
        a function to orgenise the answer and finding suitble function to prepare pre info file to send fill up function
        """
       

           
        filed_info = {}

        def extract_integers(sentence):

            digit_inside_warning = [int(word) for word in sentence.split() if word.isdigit()]

             

        # if any(word in ("number") for word in ((field["warning"].lower()).split(" "))):
        #     pass

        if field["type"] in ("select", "select-one") :
            if answer is None :
                answer = 1

            filed_info = { 
                        "function":"dropdown",
                        "type" : field["type"],
                        "str_element_id" : field["id"],
                        "int_index_Answer" : answer,
                        "lable_name" : field["label"]
            }

        if field["type"] == ("text") :
            if answer is None :
                answer = "yes"
            filed_info = { 
                        "function":"textfield",
                        "type" : field["type"],
                        "str_element_id" : field["id"],
                        "str_answer" : answer,
                        "lable_name" : field["label"]
            }
        
        if field["type"] == ("radio"):
            if answer is None :
                answer = field["options"][0]
                            
            raw_question = field["question"].split("\n")
            question = raw_question[0]
            

            filed_info = { 
                        "function":"radio",
                        "type" : field["type"],
                        "str_element_id" : field["id"],
                        "classes" :  field["classes"],
                        "question" : question,
                        "options" : answer
                        
            }
        
        if field["type"] == ("checkbox"):
            if answer is None :
                answer = ""
                                
            filed_info = { 
                        "function":"checkbox",
                        "type" : field["type"],
                        "label": "Unfollow Company",
                        "str_element_id" : "",      
                        "str_element_class" : field["classes"],
                        "str_answer" : answer,
                        "lable_name" : field["label"]
            }
        

        

       
        return filed_info
    

    @log_submain_functions
    def save_or_discard_referesh(self, title_counter, current_button_counter, form_title, button_text, company, discard_companies):
        """
        to Control errors


        """
        

    # Check if the sentence exists in the page
        if "Use your mobile device to verify" in self.browser.page_source:
            try:
                
                self.log_more_informations(inspect.currentframe().f_code.co_name, " Verification sentence found.","")
                time.sleep(30)
                
                # Find the button with "verifications" in its class name
                button = self.browser.find_element(By.XPATH, "//button[contains(@class, 'verifications')]")
                
                # Click the button
                button.click()
                self.log_more_informations(inspect.currentframe().f_code.co_name, " Verification button clicked.","")

                

            except Exception as e:
                self.log_more_informations(inspect.currentframe().f_code.co_name, " Verification button has problem.","")
                self.log_error_to_file(self.log_error_message_flag)
        
        if len(form_title)>1:
            if form_title in title_counter.keys() :
                title_counter[form_title] +=1
            else:
                title_counter[form_title] = 1
        
        self.log_more_informations(inspect.currentframe().f_code.co_name, " ************************** title_counter:", title_counter)
        
     



        if len(button_text)>1:
            if button_text in current_button_counter.keys():
                current_button_counter[button_text] +=1
            else:
                current_button_counter[button_text] = 1

        self.log_more_informations(inspect.currentframe().f_code.co_name, " ***************** current_button_counter:", current_button_counter)
      
        

        combine_values = sorted(set(list(title_counter.values()) + list(current_button_counter.values())))
        self.log_more_informations(inspect.currentframe().f_code.co_name, " ************************* combine_values:", combine_values)
        


        if combine_values[-1] > 4 and combine_values[-1] < 7 :
            
            self.log_more_informations(inspect.currentframe().f_code.co_name, " |||||||||||||||||||| Combine Value Exceeded:", combine_values)

            

            try:
                
                # To push close button of window
                if close_sign_button := self.browser.find_element(By.CLASS_NAME, css_codes["close_filled_form"]):
                    close_sign_button.click()
                    time.sleep(random.uniform(3.3,5))
                    

                    # to push save button
                    save_button = self.browser.find_element(By.CSS_SELECTOR, '[data-control-name="save_application_btn"]')
                    if save_button:
                        save_button.click()
                        
                    discard_companies.append(company)
                    with open(f"./export_data/discard_company/discard_company.json", "w") as f:
                         json.dump(discard_companies, f , indent=4)
                          

                
                # to push discard button
                if discard_button := self.browser.find_element(By.CLASS_NAME, css_codes["continue_applying"]):
                    discard_button.click()
                    time.sleep(random.uniform(2.2,8))
                 
                
                # to push close_sign_button
                if close_sign_button := self.browser.find_element(By.CLASS_NAME, css_codes["close_filled_form"]):
                    close_sign_button.click()
                    time.sleep(random.uniform(2.3,4))
                  

            except Exception:
                
                self.log_more_informations(inspect.currentframe().f_code.co_name, " Error in the function", "")
                self.log_error_to_file(self.log_error_message_flag)

             
                

        if combine_values[-1] > 7 :

            discard_companies.append(company)

            with open(f"./export_data/discard_company/discard_company.json", "w") as f:
                json.dump(discard_companies, f , indent=4)

                return "exceeded" 
    
        return "" 




    @log_submain_functions
    def no_jobtile_no_title(self):
        """
        to Control Errors
        click on Done Button 
        click on Continue Applying Button
        or else refresh the page
        
        """
        
        try:
            done_button = self.browser.find_element(By.CLASS_NAME, css_codes["close_filled_form"])
            continue_applying_button = self.browser.find_element(By.CLASS_NAME, css_codes["continue_applying"])
            
            # Close buton on the top right corner
            if done_button:
                done_button = self.browser.find_element(By.CLASS_NAME, css_codes["close_filled_form"])
                done_button.click()
                time.sleep(10)
            
            elif continue_applying_button:   
                continue_applying_button.click()
                time.sleep(random.uniform(5.8,4))
            
            else:
    
                self.refresh_page()
                time.sleep(random.uniform(5.8,4))
        except Exception as e:

            self.log_more_informations(inspect.currentframe().f_code.co_name, " There is an error with the Function ...", "")
            self.log_error_to_file(self.log_error_message_flag)

       

    #@log_submain_functions
    def log_applied_job_export_to_file(self, job_tile_text, applied_history, applied_counter, str_location_position_page ):
        
        """
        A function to export applied job to a json file

        inputs:
            job_tile_text: this is job_tile.text comes from job_list
            applied_history: a dictionary to save applied jobs, defined outside of the function
            applied_counter: a counter to count applied jobs in the page
            job_page_number: job page number comes from any function call apply_jobs
            position, location: come from apply_jobs function

        output:
            a json file with applied file
            and print applied job in the console

        """

       

        if "Applied" in (job_tile_text) and len(job_tile_text) > len("Applied"):
                            
                            
            job_tile_text = job_tile_text
            lines = job_tile_text.splitlines()

            job_title = lines[0]
            company_name = lines[2]
            location = lines[3]

            company_names_list = [value["company_name"] for value in applied_history.values()]
            job_titles_list = [value["job_title"] for value in applied_history.values()]
            locations_list = [value["location"] for value in applied_history.values()]

            if company_name in company_names_list and job_title in job_titles_list and location in locations_list: 

                pass
            else:
                
                applied_history[applied_counter] = {
                                "job_title": job_title,
                                "company_name": company_name,
                                "location": location,
                                "status": "Applied"
                            }
                
                # print('-'*50,'\n', f"{applied_counter}-Job List: \n", job_tile_text,'\n', '-'*50)
                applied_counter +=1

                
                with open(f"./export_data/apply_status/applied_history_{str_location_position_page}.json", "w") as f:
                        json.dump(applied_history, f, indent=4)
        
       

        return applied_history, applied_counter
    

    #@log_submain_functions
    def log_easy_apply_job_export_to_file(self, job_tile_text, easy_apply_history, easy_apply_counter, discard_companies, str_location_position_page ):
        
        """
        A function to export applied job to a json file

        inputs:
            job_tile_text: this is job_tile.text comes from job_list
            unapplied_history: a dictionary to save applied jobs, defined outside of the function
            unapplied_counter: a counter to count applied jobs in the page
            job_page_number: job page number comes from any function call apply_jobs
            position, location: come from apply_jobs function

        output:
            a json file with applied file
            and print applied job in the console

        """
     

        if "Easy Apply" in (job_tile_text) and len(job_tile_text) > len("Easy Apply"):

          
                            
                            
            job_tile_text = job_tile_text
            lines = job_tile_text.splitlines()

            job_title = lines[0]
            company_name = lines[2]
            location = lines[3]


            if company_name in discard_companies: 

                push_easy_apply_button_flag = False
                self.log_more_informations(inspect.currentframe().f_code.co_name, " This company is already discarded :", company_name)

            else:
                push_easy_apply_button_flag = True
                easy_apply_history[easy_apply_counter] = {

                                "job_title": job_title,
                                "company_name": company_name,
                                "location": location,
                                "status": "Easy apply"
                            }
                
               
                self.log_more_informations(inspect.currentframe().f_code.co_name, f"----> {easy_apply_counter}" , f": {job_tile_text}")
                easy_apply_counter +=1

           
                with open(f"./export_data/apply_status/easy_apply_history_{str_location_position_page}.json", "w") as f:
                        json.dump(easy_apply_history, f, indent=4)

                
           
            return push_easy_apply_button_flag, easy_apply_history, easy_apply_counter, company_name
            
        else:

            push_easy_apply_button_flag = False
            company_name = ""
            return push_easy_apply_button_flag, easy_apply_history, easy_apply_counter, company_name

    #@log_submain_functions
    def log_error_to_file(self, flag= True):  

        filename="export_data/errors/error_log.txt"

        if flag:
        
            try:
                error_trace = traceback.format_exc()
                stack = traceback.extract_tb(sys.exc_info()[2])
                func_name = stack[-1].name if stack else "<no function>"
                
                with open(filename, 'a') as file:
                    file.write("_ " * 60 + "\n")
                    file.write(f"Time: {datetime.now()}\n")
                    file.write(f"Function: {func_name}\n")
                    file.write(error_trace)
                    file.write("\n")
            except Exception as file_error:
                print(f"Failed to write to file: {file_error}")
        

        