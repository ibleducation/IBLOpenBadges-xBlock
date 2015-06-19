from importlib import import_module

class IBLOpenBadges:
    """ Create a Badge Object """
    def __init__(self, id):
        self.id = id
        self.name  = None
        self.course_id = None
        self.description = None
        self.institution = None
        self.evidences = []
        self.image = None

class BadgesClient():

    backend = None



    def __init__(self, backend):
        backend_path = backend.split(".")

        the_class = backend_path[-1]
        del(backend_path[-1])

        the_module = ".".join(backend_path)

        module = import_module(the_module)
        object_class = getattr(module,the_class)

        #instantiate the object class, this is our actual connection object
        #we're just an interface to it 
        self.backend = object_class()
        

    #next functions define the general interface to the awards server
    def build_badge_preview(self, obj_sel_badge):
        return self.backend.build_badge_preview(obj_sel_badge)

    def set_url(self, url):
        self.base_url = url
        self.backend.set_url(url)

    def get_auth_token(self, user, password):
        return self.backend.get_auth_token(user,password)

    def get_badge_data(self, ptoken, bgid, datatype='info'):
        return self.backend.get_badge_data(ptoken, bgid, datatype)

    def check_earn_badge (self, ptoken, uemail, bgid):
        return self.backend.check_earn_badge(ptoken, uemail, bgid)

    def get_award_result(self, data2parse):
        return self.backend.get_award_result(data2parse)

    def get_award_result_formatted(self, resultdata, congratulations):
        return self.backend.get_award_result_formatted(resultdata, congratulations)

    def build_badge_form(self, f_claim_name,f_claim_mail,f_form_text,obj_sel_badge):
        return self.backend.build_badge_form(f_claim_name, f_claim_mail, f_form_text, obj_sel_badge)

    def set_form_data_to_award(self, app_form_data):
        return self.backend.set_form_data_to_award(app_form_data)
        
    def claim_and_award_single_badge(self,token,award_data):
        return self.backend.claim_and_award_single_badge(token,award_data)


    #this is a common function to create a badge object
    def create_obj_badge(self, jsondata,jsonparams):
        """
        Create the object badge with retrieved data
        
        Keyword arguments:
        jsondata -- the json badge data retrieved
        jsonparams -- the json badge params (evidence) retrieved
        """
        import json
        # load data from json expected format data
        jsonData = json.loads(jsondata, object_hook=self._decode_dict)
        jsonParams = json.loads(jsonparams, object_hook=self._decode_dict)
        # create a new badge object
        obj_Badge = []
        if 'bgid' in jsonData and jsonData.get('bgid')>0 :
            badgeid = jsonData.get('bgid')
            b = IBLOpenBadges( badgeid )
            b.id = badgeid
            b.name = jsonData.get('course').decode("utf8")
            b.description = jsonData.get('course_desc').decode("utf8")
            b.institution = jsonData.get('institution').decode("utf8")
            b.image = jsonData.get('bgimage')
            b.evidences = []
            # get params (evidence)
            if "success" in jsonParams:
                if "params" in jsonParams:
                    b.evidences  = jsonParams.get('params')
            obj_Badge.append(b)
        return obj_Badge

    def _decode_list(self, data):
        """ Decode json list """
        rv = []
        for item in data:
            if isinstance(item, unicode):
                item = item.encode('utf-8')
            elif isinstance(item, list):
                item = self._decode_list(item)
            elif isinstance(item, dict):
                item = self._decode_dict(item)
            rv.append(item)
        return rv

    def _decode_dict(self, data):
        """ Decode json dict """
        rv = {}
        for key, value in data.iteritems():
            if isinstance(key, unicode):
                key = key.encode('utf-8')
            if isinstance(value, unicode):
                value = value.encode('utf-8')
            elif isinstance(value, list):
                value = self._decode_list(value)
            elif isinstance(value, dict):
                value = self._decode_dict(value)
            rv[key] = value
        return rv

