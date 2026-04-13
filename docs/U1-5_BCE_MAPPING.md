# U1-5 BCE Mapping

This file maps the current strict BCE-aligned implementation for the `U1-5` user stories only.

Scope note:

- This document covers only `Register`, `Login`, `Logout`, `Profile Update`, and `Change Password`.
- Auxiliary features such as `Forgot Password`, `Delete Account`, and avatar upload remain available in the codebase, but they are outside the strict `U1-5` BCE scope documented here.
- Fundraiser campaign access has been removed from the profile boundary so that `ProfilePage` maps only to the `U4` profile-update flow.

## Register

| BCE Class | File | Methods / Implementation |
|---|---|---|
| `RegisterPage` | [templates/auth.html](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/templates/auth.html), [static/auth.js](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/static/auth.js) | `EnterUsername()`, `EnterEmail()`, `EnterPassword()`, `RequestVerificationCode()`, `EnterVerificationCode()`, `SubmitRegistration()`, `DisplayRegistrationResult()` |
| `AuthController` | [main.py](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/main.py) | `ValidateRegistrationInput()`, `CheckEmail()`, `RequestVerificationCode()`, `SendVerificationEmail()`, `ValidationVerificationCode()`, `VerifyEmailAddress()`, `CreateAccount()` |
| `UserAccount` | [main.py](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/main.py) | `CheckEmail()`, `CreateUser()`, `SaveUser()` |
| `EmailVerification` | [main.py](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/main.py) | `GenerateCode()`, `StoreCode()`, `CheckCode()` |

## Login

| BCE Class | File | Methods / Implementation |
|---|---|---|
| `LoginPage` | [templates/auth.html](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/templates/auth.html), [static/auth.js](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/static/auth.js) | `EnterEmail()`, `EnterPassword()`, `SubmitLoginResult()`, `DisplayLoginResult()` |
| `AuthController` | [main.py](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/main.py) | `ValidateCredentials()`, `Login()`, `CreateSession()` |
| `UserAccount` | [main.py](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/main.py) | `GetUserByEmail()`, `CheckPassword()` |
| `UserSession` | [main.py](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/main.py) | `CreateSession()`, `StoreSession()` |
| `AuthenticationToken` | [main.py](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/main.py) | `CreateToken()`, `FindToken()`, `RevokeToken()` |

## Logout

| BCE Class | File | Methods / Implementation |
|---|---|---|
| `DashboardPage` | [templates/index.html](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/templates/index.html), [templates/about.html](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/templates/about.html), [templates/projects.html](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/templates/projects.html), [templates/profile.html](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/templates/profile.html), [templates/settings.html](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/templates/settings.html) | `ClickLogout()`, `DisplayLogoutResult()`, `RedirectToHome()` are represented by the shared user dropdown `Log Out` action |
| `SessionController` | [main.py](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/main.py) | `RequestLogout()`, `Logout()`, `TerminateSession()`, `ClearAuthentication()` |
| `UserSession` | [main.py](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/main.py) | `FindSession()`, `InvalidateSession()` |
| `AuthenticationToken` | [main.py](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/main.py) | `FindToken()`, `RevokeToken()` |

## Profile

| BCE Class | File | Methods / Implementation |
|---|---|---|
| `ProfilePage` | [templates/profile.html](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/templates/profile.html), [static/site.js](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/static/site.js) | `ViewProfile()`, `EditUsername()`, `EditContactDetails()`, `SubmitProfileUpdate()`, `DisplayUpdateResult()` |
| `ProfileController` | [main.py](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/main.py) | `ViewCurrentProfile()`, `GetProfile()`, `ValidateProfileInput()`, `UpdateProfile()`, `SaveProfileChanges()` |
| `UserProfile` | [main.py](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/main.py) | `GetProfileDetails()`, `UpdateProfileDetails()`, `SaveProfile()` |
| `UserAccount` | [main.py](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/main.py) | `GetUserAccount()` |

## Change Password

| BCE Class | File | Methods / Implementation |
|---|---|---|
| `ChangePasswordPage` | [templates/settings.html](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/templates/settings.html), [static/site.js](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/static/site.js) | `EnterCurrentPassword()`, `EnterNewPassword()`, `ConfirmNewPassword()`, `SubmitPasswordChange()`, `DisplayChangeResult()` |
| `PasswordController` | [main.py](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/main.py) | `ValidationCurrentPassword()`, `ValidateNewPassword()`, `ValidatePasswordPolicy()`, `UpdatePassword()`, `SendPasswordChangeNotification()` |
| `UserProfile` | [main.py](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/main.py) | `GetPasswordHash()`, `UpdatePasswordHash()` |
| `PasswordHistory` | [main.py](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/main.py) | `StorePasswordHistory()`, `GetPreviousPasswords()` |

## Strict U1-5 Routes

| Route | Purpose |
|---|---|
| `GET /auth` | Register and login boundary page |
| `GET /profile` | Profile boundary page |
| `GET /settings` | Change-password boundary page |
| `GET /logout` | Logout |
| `POST /api/auth/send-code` | Send registration verification code |
| `POST /api/auth/register` | Register account |
| `POST /api/auth/login` | Login |
| `POST /api/profile/update` | Update profile information |
| `POST /api/settings/change-password` | Change password |
