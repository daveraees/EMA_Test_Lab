# this module defines the scripts with 


class Script_database:
    def __init__(self):
        # structure with all the test scipts available
        self.category_all_name = 'All'
        self.script_base_categories = {}
        self.script_base_categories[self.category_all_name]=[]
        
        return
    def add_script(self, script, category=None):
        """
        inserts script in the database in given category,
        and into gategory 'All'
        """
        if category == None: 
            category = self.category_all_name
        if category in self.script_base_categories.keys():
            self.script_base_categories[category].append(script())
            if not (category == self.category_all_name):
                self.script_base_categories[self.category_all_name].append(script())
        else:
            # create category
            self.script_base_categories[category] = []
            self.add_script(script, category)
        return
    def get_script_listing(self):
        """
        construct the script list database
        """
        scriptCategoriesList = []
        for key in self.script_base_categories.keys():
            scriptCategoriesList.append(key)
            scriptNameList = []
            for script in self.script_base_categories[key]:
                scriptNameList.append(script.get_Name())
            scriptCategoriesList.append(scriptNameList)
        return scriptCategoriesList
    def find_script(self,category,scriptname):
        """
        returns a script object of the given name in give category
        """
        script = None
        for script in self.script_base_categories[category]:
            if script.get_Name() == scriptname:
                description = script.get_Description()
                break
        return script
    def get_script_categories(self):
        """
        construct the list of script categories
        """
        # scriptCategoriesList = []
        scriptCategoriesList = self.script_base_categories.keys()
        return scriptCategoriesList
    def get_scripts_in_category(self,category):
        scriptNameList = []
        for script in self.script_base_categories[category]:
            scriptNameList.append(script.get_Name())
        return scriptNameList
    def get_script_description(self,category,scriptname):
        description = 'ERROR: Script "' + scriptname +'" not found'
        script = self.find_script(category, scriptname)
        if not (script == None):
            description = script.get_Description()
        return description

            
    
ScriptsBase = Script_database()

    
if __name__ == "__main__":
    pass
