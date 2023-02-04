Auth is depend on
- dj-rest-auth
- django-rest-au
- django-allauth


# Endpoints
## Auth

### registration (Done)
- /api/auth/user/registration/

### login & logout
- /api/auth/login/ 
  - [ ] TODO: make it email or username (currently only username)
- /api/auth/logout/ (Done)

### password
- /api/auth/password/change/ (Done)
- /api/auth/password/reset/ 
  - (TODO)
- /api/auth/password/reset/confirm/
  - (TODO)
  
### user
- /api/auth/user/ (Done, maybe need to add more fields in the future)


### verify email (TODO)
- /api/auth/user/registration/verify-email/
- /api/auth/user/registration/verify-email/resend/
- /api/auth/user/registration/verify-email/confirm/
- /api/auth/user/registration/verify-email/confirm/resend/