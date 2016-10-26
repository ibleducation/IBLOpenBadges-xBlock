

import pkg_resources
import ast
import json

from xblock.core import XBlock
from xblock.fields import Scope, Integer, String
from xblock.fragment import Fragment
from xmodule.fields import RelativeTime

import edxappBadges
import badges_client

class IBLstudiosbadges(XBlock):
    """
    IBLstudiosbadges Class
    """

    # xblock module name is the name of the field set in mongodb
    xblock_name_field = 'iblstudiosbadges'
    # mongodb data
    xblock_mongodb_xmoduledb = 'edxapp'
    xblock_mongodb_modulestore = 'modulestore'
    xblock_mongodb_modulestore_structures = 'modulestore.structures'
    xblock_mongodb_modulestore_activevers = 'modulestore.active_versions'
    xblock_mongodb_modulestore_definitions = 'modulestore.definitions'
    
    # mysql data
    mysql_database = 'edxapp'
    mysql_user = 'root'
    mysql_pwd = ''
    # general data
    display_name = String(display_name="Display Name", default="IBL Studios Badges", scope=Scope.settings, help="Name of the component in the edxplatform")
    form_text = String(display_name="text_desc", default=" ", scope=Scope.content, help="Badge text description")
    congratulations_text = String(display_name="congratulations_desc", default=" ", scope=Scope.content, help="Congratulations text description")
    enough_text = String(display_name="enough_desc", default=" ", scope=Scope.content, help="Not-enough-score text description")
    bg_id = String(display_name="id", default="1", scope=Scope.content, help="Id of the Badge")
    n_course_id = String(display_name="CourseId", default="0", scope=Scope.user_state, help="Id of teh current course")
    n_user_id = String(display_name="UserId", default="0", scope=Scope.user_state, help="Id of the current user")
    user_score = String(display_name="UserScore", default="0", scope=Scope.user_state, help="Current section user score")
    required_score = String(display_name="RequiredScore", default="50", scope=Scope.content, help="Requireds core")
    debug_mode = String(display_name="debug", default="0", scope=Scope.content, help="Enable debug mode")
    # badges provider data
    claim_prov_usr = String(display_name="ProviderUSER", default="provider_user", scope=Scope.content, help="Badge provider user")
    claim_prov_pwd = String(display_name="ProviderPass", default="provider_key_secret", scope=Scope.content, help="Badge provider pass")
    # badges xblock data
    claim_name = String(display_name="ClaimUserName", default="Jhon", scope=Scope.user_state, help="")
    claim_mail = String(display_name="ClaimUserMail", default="users@email.local", scope=Scope.user_state, help="")
    claim_db_user_data = 'None'
    claim_db_user_id = 'None'
    claim_db_user_course = 'None'
    claim_db_user_name = 'None'
    claim_db_user_email = 'None'
    claim_db_user_score = '0'
    # control errors
    claim_badge_errors = ''
    iblclient = None
    iblsettings = {
        'module':'iblstudiosbadges.BadgeOne_client.BadgeOneClient',
        'base_url': "https://badgeone.com",
    }

    def __init__(self, *args, **kwargs):
        self.iblclient = badges_client.BadgesClient(self.iblsettings['module'])
        self.iblclient.set_url(self.iblsettings["base_url"])
        super(IBLstudiosbadges, self).__init__(*args, **kwargs)

    def resource_string(self, path):
        # Handy helper for getting resources from our kit
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    def student_view(self, context):
        """
        The primary view for the students
        """

        # Setup data to claim a badge
        self.n_user_id = self.get_student_id()
        self.claim_db_user_data = self.DB_get_user_data()
        self.claim_db_user_id = self.claim_db_user_data[0]
        self.claim_db_user_course = self.claim_db_user_data[1]
        self.claim_db_user_name = self.claim_db_user_data[2]
        self.claim_db_user_email = self.claim_db_user_data[3]
        self.claim_db_user_score = self.claim_db_user_data[4]
        self.claim_db_problems_lists = self.claim_db_user_data[5]
        self.claim_db_problems_total_score = self.claim_db_user_data[6]
        self.claim_db_problems_partial_score = self.claim_db_user_data[7]
        self.claim_db_problems_percent_score = self.claim_db_user_data[8]
        self.claim_db_badge_problems_score = self.claim_db_user_data[9]
        self.user_score = self.claim_db_user_data[4]
        claim_name = self.claim_db_user_name
        claim_mail = self.claim_db_user_email
        self.claim_badge_errors = self.claim_badge_errors
        self.claim_badge_form = ''
        self.check_earned = ''
        self.preview_badge = ''
        # Check out provider badge data
        if self.claim_badge_errors == "":
            self.claim_prov_access_token = self.iblclient.get_auth_token(self.claim_prov_usr, self.claim_prov_pwd)
            if self.claim_prov_access_token != "":
                badge_info = self.iblclient.get_badge_data(self.claim_prov_access_token, self.bg_id, 'info')
                badge_params = self.iblclient.get_badge_data(self.claim_prov_access_token, self.bg_id, 'params')
                obj_badge = self.iblclient.create_obj_badge(badge_info, badge_params)
                self.check_earned = self.iblclient.check_earn_badge(self.claim_prov_access_token, self.claim_db_user_email, self.bg_id)
                self.preview_badge = self.iblclient.build_badge_preview(obj_badge)
                if obj_badge :
                    # check if user has been awarded yet
                    if self.check_earned != '':
                        self.award_earn_prov = self.iblclient.get_award_result (self.check_earned)
                        self.award_earned = self.iblclient.get_award_result_formatted(self.award_earn_prov, self.congratulations_text)
                    else:
                        self.claim_badge_form = self.iblclient.build_badge_form(self.claim_db_user_name, self.claim_db_user_email, self.form_text, obj_badge)
                else:
                    self.claim_badge_errors = 'Could not retrieve the information associated with the Badge ID selected. Please, verify your data.'
            else:
                self.claim_badge_errors = 'Could not connect to provider. Please, verify your credentials.'
        # Initialize html view
        self.claim_data = ""
        if self.claim_badge_errors == "":
            if self.debug_mode == "1":
                html = self.resource_string("static/html/debug.html")
            else:
                if int(self.user_score) < int(self.required_score):
                    html = self.resource_string("static/html/student_view_noscore.html")
                else:
                    if self.check_earned != '':
                        html = self.resource_string("static/html/student_view_earn_badge.html")
                    else:
                        html = self.resource_string("static/html/student_view_claim_badge.html")
            frag = Fragment(html.format(self=self))
            frag.add_css(self.resource_string("static/css/style.css"))
            if self.check_earned == '':
                frag.add_javascript(self.resource_string("static/js/src/student_view_scripts.js"))
            frag.initialize_js('StudentViewBadge')
        else:
            if self.debug_mode == "1":
                html = self.resource_string("static/html/result_errors_debug.html")
            else:
                html = self.resource_string("static/html/result_errors.html")
            frag = Fragment(html.format(self=self))
            frag.add_css(self.resource_string("static/css/style.css"))
        return frag

    def get_student_id(self):
        """
         Get data from student_id
        """
        if hasattr(self, "xmodule_runtime"):
            s_id = self.xmodule_runtime.anonymous_student_id
        else:
            if self.scope_ids.user_id == None:
                s_id = "None"
            else:
                s_id = unicode(self.scope_ids.user_id)
        return s_id

    def DB_get_user_data(self):
        """
        Get student data from the DB
        """
        results = edxappBadges.resultBadgesScores(self)
        return results

    def studio_view(self, context=None):
        """
        The primary view for Studio
        """

        html = self.resource_string("static/html/studio_view_edit.html")
        frag = Fragment(html.format(self=self))
        frag.add_css(self.resource_string("static/css/style.css"))
        frag.add_javascript(self.resource_string("static/js/src/studio_view_edit.js"))
        frag.initialize_js('StudentEditBadge')
        return frag

    @XBlock.json_handler
    def student_claim_save(self, claimdata, suffix=''):
        """
        From student view claim and save a Badge
        """

        # parse data to claim a badge
        award_result = 'error'
        if claimdata:
            # connect to server and get a new token
            self.claim_prov_access_token = self.iblclient.get_auth_token(self.claim_prov_usr, self.claim_prov_pwd)
            # parse data to claim a badge
            claimdata_dict = dict(entry.split('=') for entry in claimdata.split('&'))
            award_data = self.iblclient.set_form_data_to_award(claimdata_dict)
            set_award_single = self.iblclient.claim_and_award_single_badge(self.claim_prov_access_token, award_data)
            # mode debug to get provider response
            if self.debug_mode == "1":
                debug_result = set_award_single
                return { 'result' : debug_result }
            # result from earn request
            award_result_prov = self.iblclient.get_award_result (ast.literal_eval(set_award_single))
            award_result = self.iblclient.get_award_result_formatted(award_result_prov, self.congratulations_text)
        return { 'result' :  award_result }

    @XBlock.json_handler
    def studio_save(self, data, suffix=''):
        """
        Configure provider information and xblock data
        """

        self.debug_mode = data['debug_mode']
        self.bg_id = data['bg_id']
        self.form_text = data['form_text']
        self.congratulations_text = data['congratulations_text']
        self.enough_text = data['enough_text']
        self.required_score = data['required_score']
        self.claim_prov_usr = data['badge_pro_user']
        self.claim_prov_pwd = data['badge_pro_pwd']
        self.display_name = data['badge_display_name']
        return { 'result': 'success' }

    @staticmethod
    def workbench_scenarios():
        """
        A canned scenario for display in the workbench.
        """

        return [
            ("IBLStudiosBadges",
            """<vertical_demo>
                <iblstudiosbadges/>
                <iblstudiosbadges/>
                <iblstudiosbadges/>
                </vertical_demo>
            """),
        ]
