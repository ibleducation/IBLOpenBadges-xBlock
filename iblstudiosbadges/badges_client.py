

from importlib import import_module

class IBLOpenBadges:
    """
    Create a Badge Object
    """
    def __init__(self, id):
        self.id = id
        self.name  = None
        self.course_id = None
        self.description = None
        self.institution = None
        self.evidences = []
        self.image = None

class BadgesClient():
    """
    This class includes methods and functions to perfom server transactions
    """
    backend = None

    def __init__(self, backend):
        """
        Constructor for BadgesClient's class

        Arguments:
            backend (str): Class path to the actual badge client to use
        """

        backend_path = backend.split(".")
        the_class = backend_path[-1]
        del(backend_path[-1])
        the_module = ".".join(backend_path)
        module = import_module(the_module)
        object_class = getattr(module,the_class)
        self.backend = object_class()

    def build_badge_preview(self, obj_sel_badge):
        """
        Creates a badge preview object, with html

        Arguments:
            obj_sel_badge (obj): Badge data object from get_badge_data

        Returns:
            str: html preview for the badge

        """
        return self.backend.build_badge_preview(obj_sel_badge)

    def set_url(self, url):
        """
        Set the basic url for this client

        Arguments:
            url (str): The server url

        Returns:
            str: The complete url string

        """

        self.base_url = url
        self.backend.set_url(url)

    def get_auth_token(self, user, password):
        """
        Returns an auth token from the client

        Arguments:
            user (str): The user
            password (str): The password

        """

        return self.backend.get_auth_token(user,password)

    def get_badge_data(self, ptoken, bgid, datatype='info'):
        """
        Returns basic badge data

        Arguments:
            ptoken (str): Is the auth token returned via get_auth_token
            bgid (int): Is the badge id
            datatype (str): Is sent to the client to define the kind of requested data

        """

        return self.backend.get_badge_data(ptoken, bgid, datatype)

    def check_earn_badge (self, ptoken, uemail, bgid):
        """
        Checks if the user earned the badge

        Arguments:
            ptoken (str):  Is the auth token returned via get_auth_token
            uemail (str): Is the user email to validate
            bgid (int): Is the badge id

        """

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

    def create_obj_badge(self, jsondata,jsonparams):
        """
        Create the object badge with retrieved data (common function)

        Arguments:
            jsondata (obj): The json badge data retrieved
            jsonparams (obj): The json badge params (evidence) retrieved

        """

        import json
        jsonData = json.loads(jsondata, object_hook=self._decode_dict)
        jsonParams = json.loads(jsonparams, object_hook=self._decode_dict)
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
            if "success" in jsonParams:
                if "params" in jsonParams:
                    b.evidences  = jsonParams.get('params')
            obj_Badge.append(b)
        return obj_Badge

    def _decode_list(self, data):
        """
        Decode json list
        """
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
        """
        Decode json dict
        """
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
