import sys
import os
import requests
import json

class BadgeOneClient():

    claim_prov_url = None
    claim_prov_url_token    = '/api/token.php'
    claim_prov_url_list     = '/api/badgedata.php'
    claim_prov_url_claim    = '/api/claim_badge.php'
    claim_prov_url_checkearn = '/api/checkearn.php'

    def set_url(self, url):
        self.claim_prov_url = url


    def make_full_url(self, url):
        """
        Join base url and the url path we need.
        """
        return "%s%s" % ( self.claim_prov_url, url)

    def get_auth_token(self, pusr, ppwd):
        """
        Get Auth Token to authenticate transactions

        Keyword arguments:
        pusr -- the username
        ppwd -- the secret_key
        """
        result = ''
        pdata = {'grant_type':'client_credentials'}
        if pusr!='' and ppwd!='':
            res  = requests.post(self.make_full_url(self.claim_prov_url_token), data=pdata, auth=(pusr,ppwd))

            data = json.loads(res.content)

            result = ''
            if data !='':
                for key,value in data.items():
                    if key == 'access_token':
                        result = value
        return result

    def get_badge_data (self,ptoken,bgid,datatype='info'):
        """
        Retry badge information from external server

        Keyword arguments:
        ptoken -- the token auth
        bgid -- the badge id
        datatype -- the type of data to retry (default info)
        """
        pdata = {'bgid':bgid,'datatype':datatype}
        headers = {'Authorization' : 'Bearer '+ptoken+'' }
        res = requests.post(self.make_full_url(self.claim_prov_url_list), data=pdata, headers=headers)
        return res.content

    def convert_dict2querystring(self, dict):
        """
        Convert dict to query-string
        """
        import urllib
        text = ''
        count = 0
        for i in dict:
            if count > 0:
                text+= "&"
            text+= str(i) + "=" + str(dict[i])
            count += 1
        return text

    def check_earn_badge (self,ptoken,uemail,bgid):
        """
        Ask the server if the badge was earned before

        Keyword arguments:
        ptoken -- the token auth
        uemail -- the user email
        bgid -- the badge id
        """
        import json
        pdata   = {'email':uemail, 'id':bgid}
        headers = {'Authorization' : 'Bearer '+ptoken+'' }
        res     = requests.post(self.make_full_url(self.claim_prov_url_checkearn), data=pdata, headers=headers)
        data    = json.loads(res.content, object_hook=self._decode_dict)
        result = ''
        if data!='':
            for key,value in data.iteritems():
                if key == "badge_url":
                    return data
        return result


    def build_evidences_form(self, data_evidences):
        """
        Build the html form tags for evidences

        Keyword arguments:
        data_evidences -- evaulated data from sever response
        """
        result = ''
        if data_evidences:
            for evidence in data_evidences:
                # required data
                id = evidence.get("param_id", 0)
                description = evidence.get("description", 'None')
                type = evidence.get("type", 'None')
                required = evidence.get("required", 'N')
                label = evidence.get("label", 'N')
                # allowed evidences
                if id>0 and (type =='url' or type =='text' ) :
                    # controls
                    if description == None:
                        description = 'Description'
                    if required  == 'Y':
                        required = 'required'
                    # contruct html
                    result +='<tr>'
                    result +='<td>%s</td>' % (description)
                    result +='<tr><tr><td>'
                    if type == "textarea":
                        result +='<textarea name="evidence|%s" id="evidence|%s" style="width:820px;resize:vertical;height:200px; overflow:auto" %s></textarea>' % (id,id,required)
                    else:
                        result +='<input type="url" name="evidence|%s" id="evidence|%s" value="" %s  style="width:820px;"><br><span style="font-size:small;font-style:italic;">Note: just online http addresess (URL) are allowed</span>' % (id,id,required)
                    result +='</td>'
                    result +='</tr><tr><td>&#160;</td></tr>'
        return result



    def build_badge_preview(self, obj_sel_badge):
        """
        Build the html to preview the badge to earn

        Keyword arguments:
        obj_sel_badge -- badge object
        """
        view = ''
        if obj_sel_badge and obj_sel_badge[0].id > 0:
            view  = "<table cellpadding=4 cellspacing=4 style='border:solid 1px #333;'>"
            view += "<tr>"
            view += "<td><img src='%s' style='max-width:300px;'></td>" % (obj_sel_badge[0].image)
            view += "<td valign=top>"
            view += "       <div style='padding-top:14px;>'<b>%s</b></div>" % (obj_sel_badge[0].name)
            view += "       <br>%s" % (obj_sel_badge[0].description)
            view += "</td>"
            view += "</tr>"
            view += "</table><br>"
        return view

    def build_badge_form(self, f_claim_name,f_claim_mail,f_form_text,obj_sel_badge):
        """
        Build the html form to claim a new badge

        Keyword arguments:
        f_claim_name -- student complete name
        f_claim_mail -- student email
        f_form_text -- label description to present the form
        obj_sel_badge -- badge object
        """
        if obj_sel_badge[0].id > 0:
            # get params (evidence) and construct html
            if obj_sel_badge[0].evidences:
                data_evidences = obj_sel_badge[0].evidences
                if data_evidences:
                    f_claim_evidences = self.build_evidences_form(data_evidences)
            else:
                f_claim_evidences = ''
            # split student complete name (firstname, lastname)
            f_claim_full_name = f_claim_name.split(' ')
            f_claim_s_first_name = f_claim_full_name[0]
            if len(f_claim_full_name) > 1:
                    f_claim_s_last_name = f_claim_name[len(f_claim_s_first_name):]
                    f_claim_s_last_name = f_claim_s_last_name.strip()
            else:
                    f_claim_s_last_name = '.'
        # Preview the badge to be claim
        form  = self.build_badge_preview(obj_sel_badge)
        # Build complete form to complete the claim process
        form += "<form action='student_claim_save' name='badge_claimer' id='badge_claimer' method='post'>"
        form += '<input type="hidden" name="id" value="%s" requried>' % (obj_sel_badge[0].id)
        form += '<input type="hidden" name="first_name" value="%s">' % (f_claim_s_first_name)
        form += '<input type="hidden" name="last_name" value="%s">' % (f_claim_s_last_name)
        form += '<input type="hidden" name="email" value="%s">' % (f_claim_mail)
        form += "<table>"
        form += "<tr><td><span style='color:#666666;'><b>%s</b></span></td></tr>" % (f_form_text)
        form += "<tr><td>&#160;</td></tr>"
        form += "%s" % (f_claim_evidences)
        form += "<tr><td>&#160;</td></tr>"
        form += "<tr><td><input type='submit' name='claim-button' value='CLAIM YOUR BADGE'></td></tr>"
        form += "</table>"
        form += "</form>"
        return form

    def set_form_data_to_award(self, app_form_data):
        """
        Prepare data given in the claim form
        to send as querystring request to the server

        Keyword arguments:
        app_form_data -- the data retrieved from the claim form
        """
        import urllib
        #define vars
        data_dict   = {}
        form        = app_form_data
        # decode some chars for evidences
        for k,v in form.iteritems():
            #decode chars for evidences
            v = v.replace('%3A',':')
            v = v.replace('%2F','/')
            v = v.replace('%40','@')
            k = k.replace('%7C','|')
            if v != 'None':
                data_dict[k] = v
        return data_dict

    def claim_and_award_single_badge(self,token,award_data):
        """
        Claim a new badge
        sending form data to server

        Keyword arguments:
        token -- the token auth
        award_data -- the formatted data retrieved from the form
        """
        pdata = award_data
        headers = {'Authorization' : 'Bearer '+token+'' }
        res = requests.post(self.make_full_url(self.claim_prov_url_claim), data=pdata, headers=headers)
        return res.content

    def get_award_result(self, data2parse):
        """
        Parse the json data retrieved
        server after claim a new badge
        and try to evaluate if was create.
        If badge_url param exists and is not empty
        the badge was earned successfully
        """
        result = 'error'
        if data2parse != '':
            for key,val in data2parse.iteritems():
                if key == "badge_url":
                    return val
        return result

    def get_award_result_formatted(self, resultdata,congratulations):
        """
        Print the result of a claimed badge

        Keyword arguments:
        resultdata -- string with two possible results ('error' or the url of the earned badge)
        congratulations -- free text defined in studio view
        """
        result =''
        if resultdata != 'error':
            result  ='<div style="color:green;">'
            result +="<h1 style='color:green;'>%s</h1>" % (congratulations)
            result +='<div><a href="%s" target="_blank">%s</a></div>' % (resultdata,resultdata)
            result +='</div>'
        else:
            result  ='<div style="color:red;">'
            result +='<div><h1 style="color:red">Error: The award could not be created</h1></div>'
            result +='</div>'
        return result

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
