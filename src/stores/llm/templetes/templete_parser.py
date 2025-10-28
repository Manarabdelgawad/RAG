import os

class TemplateParser:

    def __init__(self,language:str=None,defualt_language='en'):
        self.current_path=os.path.dirname(os.path.abspath(__file__))
        self.default_language=defualt_language

    def set_language(self,language:str):

        if not language:
            self.language=self.defualt_language

        
        language_path=os.path.join(self.current_path,"locales",language)

        if os.path.exists(language_path):
            self.language=language
        else:
            self.language=self.defualt_language


    def get(self,group:str,key:str,vars:dict{} ):
        if not group or not key:
            return None

        group_path=os.path.join(self.current_path,"locales",self.language,f"{group}.py")
        targeted_language=self.language

        if not os.path.exists(group_path):
            group_path=os.path.join(self.current_path,"locales",self.default_language,f"{group}.py")
            targeted_language=self.default_language

        if not os.path.exists(group_path):
            return None

        #import moodule
        module=__import__(f"store.llm.templates.locales{targeted_language}.{group}",fromlist=[group])

        if not module:
            return None

        key_attribute=getattr(module,key)
        return key_attribute.substitute(vars)


