IBL OpenBadges XBlock
=====================

This is the XBlock to allow digital badges to be awarded from an online course using Open edX, which depends on [IBLOpenBadges-Server](https://github.com/iblstudios/IBLOpenBadges-Server).

The Open Badges XBlock was developed by [IBL Studios](http://iblstudios.com/) with conceptual and feature design by Lorena A. Barba and Michael Amigot. It was used in Prof. Barba's open online course ["Practical Numerical Methods with Python"](http://openedx.seas.gwu.edu/courses/GW/MAE6286/2014_fall/about), starting on December 2014. 
General consultancy on the principles of open digital badges in education was provided by [Prof. Daniel T. Hickey](http://remediatingassessment.blogspot.com/) and his team at Indiana University during Fall 2014.

## Summary of features

1. The badges can be awarded from a **"Graded Sub-section"** in a course in Open edX. The instructor sets the minimum score for the eligibility of the badge, and configures the badge component with the data of the badge service, badge ID, custom messages for the user, etc.
2. Once it's added to a Graded Sub-section, the open-badges XBlock will automatically check the user's score in that sub-section (when the user enters the sub-section).
3. While the user does not have a high-enough score for eligibility, the XBlock will display a custom message indicating that this is the case.
4. Once the user has a high-enough score, the XBlock will reveal the badge image and the input fields to claim the badge.
5. The user fills the claim form, entering URL fields providing evidence of her learning, etc.
6. Once awarded, the badge becomes privately available in the user's account on the badge service. The user then "claims" the badge to make it public (this is the normal operation of open-badge services.)

###Requirements:
* [IBLOpenBadges-Server](https://github.com/iblstudios/IBLOpenBadges-Server) platform.

###Install:
* Edit `iblstudiosbadges.py` and set up the `claim_prov_url` variable with the URL where the badges server is located.
  Note: the absolute path is required, therefore remove the last `/` character at the end of the URL if it exists (e.g. http://domain.tld).
  Ports are allowed. e.g. http://domain.tld:5000
  
  `base_url = "ABSOLUTE_PATH_URL_PROVIDER"`

* Set up the MySQL connection: `iblstudiosbadges.py`
  e.g. `mysql_database = 'edxapp'`, `mysql_user = 'root'`, `mysql_pwd = ''`

* Set up the MongoDB connection: `iblstudiosbadges.py`
  e.g. `xblock_mongodb_xmoduledb = 'edxapp'`, `xblock_mongodb_modulestore = 'modulestore'`

* Install the XBlock.
  Sample installation file: `installme.sh`. Change `'your_path'` to the local path where you downloaded the package.

---

_Note: Remember to set up the badge with the variable `debug_mode` set to `1`;
this will activate the application debug mode. Under production mode, remember
to turn off the `debug_mode` variable._

