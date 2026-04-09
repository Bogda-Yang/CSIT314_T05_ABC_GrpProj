# U1-5 BCE Mapping

This file maps the current implementation to the BCE-style classes and methods used in the project.

## Register

| BCE Class | File | Methods / Implementation |
|---|---|---|
| `RegisterPage` | [templates/auth.html](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/templates/auth.html), [static/auth.js](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/static/auth.js) | `EnterUsername()`, `EnterEmail()`, `EnterPassword()`, `RequestVerificationCode()`, `EnterVerificationCode()`, `SubmitRegistration()`, `DisplayRegistrationResult()` are represented by the register form and button-driven registration flow |
| `AuthController` | [main.py](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/main.py) | `ValidateRegistrationInput()`, `CheckEmail()`, `RequestVerificationCode()`, `SendVerificationEmail()`, `ValidationVerificationCode()`, `VerifyEmailAddress()`, `CreateAccount()` |
| `UserAccount` | [main.py](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/main.py) | `CheckEmail()`, `CreateUser()`, `SaveUser()` |
| `EmailVerification` | [main.py](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/main.py) | `GenerateCode()`, `StoreCode()`, `CheckCode()` |

## Login

| BCE Class | File | Methods / Implementation |
|---|---|---|
| `LoginPage` | [templates/auth.html](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/templates/auth.html), [static/auth.js](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/static/auth.js) | `EnterEmail()`, `EnterPassword()`, `SubmitLoginResult()`, `DisplayLoginResult()` are represented by the login form and login action |
| `AuthController` | [main.py](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/main.py) | `ValidateCredentials()`, `Login()`, `CreateSession()` |
| `UserAccount` | [main.py](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/main.py) | `GetUserByEmail()`, `CheckPassword()` |
| `UserSession` | [main.py](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/main.py) | `CreateSession()`, `StoreSession()` |
| `AuthenticationToken` | [main.py](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/main.py) | `CreateToken()` |

## Logout

| BCE Class | File | Methods / Implementation |
|---|---|---|
| `DashboardPage` | [templates/index.html](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/templates/index.html), [templates/about.html](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/templates/about.html) | `ClickLogout()`, `DisplayLogoutResult()`, `RedirectToHome()` are represented by the user dropdown `Log Out` action |
| `SessionController` | [main.py](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/main.py) | `RequestLogout()`, `Logout()`, `TerminateSession()`, `ClearAuthentication()` |
| `UserSession` | [main.py](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/main.py) | `FindSession()`, `InvalidateSession()` |
| `AuthenticationToken` | [main.py](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/main.py) | `FindToken()`, `RevokeToken()` |

## Profile

| BCE Class | File | Methods / Implementation |
|---|---|---|
| `ProfilePage` | [templates/profile.html](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/templates/profile.html), [static/site.js](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/static/site.js) | `ViewProfile()`, `EditUsername()`, `EditContactDetails()`, `SubmitProfileUpdate()`, `DisplayUpdateResult()` are represented by the profile form and the single `Save Profile` action |
| `ProfileController` | [main.py](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/main.py) | `ViewCurrentProfile()`, `GetProfile()`, `ValidateProfileInput()`, `UpdateProfile()`, `SaveProfileChanges()` |
| `UserProfile` | [main.py](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/main.py) | `GetProfileDetails()`, `UpdateProfileDetails()`, `SaveProfile()` |
| `UserAccount` | [main.py](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/main.py) | `GetUserAccount()` |

Profile implementation notes:

- `Username` is now merged back into the same `SubmitProfileUpdate()` flow for BCE alignment.
- `Gender`, `Age`, `Occupation`, and `Personal Bio` are handled as extended profile attributes within the same update path.
- Avatar upload is implemented as an additional profile-related extension through `/api/profile/avatar`, outside the strict original BCE diagram.

## Change Password

| BCE Class | File | Methods / Implementation |
|---|---|---|
| `ChangePasswordPage` | [templates/settings.html](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/templates/settings.html), [static/site.js](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/static/site.js) | `EnterCurrentPassword()`, `EnterNewPassword()`, `ConfirmNewPassword()`, `SubmitPasswordChange()`, `DisplayChangeResult()` are represented by the settings page password form |
| `PasswordController` | [main.py](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/main.py) | `ValidationCurrentPassword()`, `ValidateNewPassword()`, `ValidatePasswordPolicy()`, `UpdatePassword()`, `SendPasswordChangeNotification()` |
| `UserProfile` | [main.py](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/main.py) | `GetPasswordHash()`, `UpdatePasswordHash()` |
| `PasswordHistory` | [main.py](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/main.py) | `StorePasswordHistory()`, `GetPreviousPasswords()` |

## Forgot Password

| BCE Style Extension Class | File | Methods / Implementation |
|---|---|---|
| `ForgotPasswordPage` | [templates/auth.html](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/templates/auth.html), [static/auth.js](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/static/auth.js) | Email input, reset code input, verification step, new password input, and reset action follow the same boundary style as the authentication BCE flow |
| `ForgotPasswordController` | [main.py](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/main.py) | `RequestResetCode()`, `ValidationResetCode()`, `ValidateResetPasswordInput()`, `ResetPassword()` |
| `PasswordResetVerification` | [main.py](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/main.py) | `GenerateCode()`, `StoreCode()`, `CheckCode()` |
| `PasswordController` | [main.py](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/main.py) | `ValidatePasswordPolicy()`, `SendPasswordChangeNotification()` are reused during password reset |

## Delete Account

| BCE Style Extension Class | File | Methods / Implementation |
|---|---|---|
| `DeleteAccountPage` | [templates/settings.html](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/templates/settings.html), [static/site.js](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/static/site.js) | Current password input and delete action are placed in the settings page delete-account section |
| `DeleteAccountController` | [main.py](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/main.py) | `ValidationCurrentPassword()`, `DeleteAccount()`, `ClearUserProfile()`, `ClearPasswordHistory()`, `ClearUserSessions()`, `ClearVerificationRecords()` |
| `UserAccount` | [main.py](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/main.py) | `DeleteUser()` |

## Implemented Routes

| Route | Purpose |
|---|---|
| `GET /` | Home page |
| `GET /about` | About Us page |
| `GET /profile` | Profile page |
| `GET /settings` | Settings page |
| `GET /auth` | Login / Register / Forgot Password page |
| `GET /logout` | Logout |
| `POST /api/auth/send-code` | Send registration verification code |
| `POST /api/auth/register` | Register account |
| `POST /api/auth/login` | Login |
| `POST /api/auth/send-reset-code` | Send password reset code |
| `POST /api/auth/verify-reset-code` | Verify password reset code |
| `POST /api/auth/reset-password` | Reset password |
| `POST /api/profile/update` | Update profile information |
| `POST /api/profile/avatar` | Upload profile avatar |
| `POST /api/settings/change-password` | Change password |
| `POST /api/settings/delete-account` | Delete account |
