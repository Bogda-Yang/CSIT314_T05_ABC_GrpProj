# U1-5 BCE Mapping

This document lists only the currently implemented `U1-5` user-story methods and where they appear in the codebase.

Scope:

- `U1 Register`
- `U2 Login`
- `U3 Logout`
- `U4 Update Profile`
- `U5 Change Password`

The file and line references below cover only methods that belong to those user stories.

## U1 Register

| BCE Class | File / Line | Methods / Line |
|---|---|---|
| `RegisterPage` | `templates/auth.html:114-141`, `static/auth.js:204-280` | `EnterUsername()`, `EnterEmail()`, `EnterPassword()`, `RequestVerificationCode()`, `EnterVerificationCode()`, `SubmitRegistration()`, `DisplayRegistrationResult()` |
| `AuthController` | `main.py:1485-1568` | `ValidateRegistrationInput()` `main.py:1485`, `CheckEmail()` `main.py:1507`, `SendVerificationEmail()` `main.py:1513`, `VerifyEmailAddress()` `main.py:1518`, `RequestVerificationCode()` `main.py:1523`, `ValidationVerificationCode()` `main.py:1533`, `CreateAccount()` `main.py:1538` |
| `UserAccount` | `main.py:130-158` | `CreateUser()` `main.py:130`, `SaveUser()` `main.py:141`, `CheckEmail()` `main.py:149` |
| `EmailVerification` | `main.py:94-116` | `GenerateCode()` `main.py:96`, `StoreCode()` `main.py:101`, `CheckCode()` `main.py:108` |

## U2 Login

| BCE Class | File / Line | Methods / Line |
|---|---|---|
| `LoginPage` | `templates/auth.html:95-112`, `static/auth.js:176-201` | `EnterEmail()`, `EnterPassword()`, `SubmitLogin()`, `DisplayLoginResult()` |
| `AuthController` | `main.py:1569-1603` | `ValidateCredentials()` `main.py:1569`, `CreateSession()` `main.py:1577`, `Login()` `main.py:1597` |
| `UserAccount` | `main.py:145-158` | `GetUserByEmail()` `main.py:145`, `CheckPassword()` `main.py:153` |
| `UserSession` | `main.py:320-339` | `CreateSession()` `main.py:320`, `StoreSession()` `main.py:329` |
| `AuthenticationToken` | `main.py:355-370` | `CreateToken()` `main.py:355`, `FindToken()` `main.py:364`, `RevokeToken()` `main.py:370` |

## U3 Logout

| BCE Class | File / Line | Methods / Line |
|---|---|---|
| `DashboardPage` | `templates/index.html`, `templates/about.html`, `templates/projects.html`, `templates/profile.html`, `templates/settings.html` | Shared user dropdown `Log Out` action in the authenticated navigation |
| `SessionController` | `main.py:1607-1639` | `RequestLogout()` `main.py:1607`, `Logout()` `main.py:1612`, `TerminateSession()` `main.py:1619`, `ClearAuthentication()` `main.py:1636` |
| `UserSession` | `main.py:333-339` | `FindSession()` `main.py:333`, `InvalidateSession()` `main.py:339` |
| `AuthenticationToken` | `main.py:364-370` | `FindToken()` `main.py:364`, `RevokeToken()` `main.py:370` |

## U4 Update Profile

| BCE Class | File / Line | Methods / Line |
|---|---|---|
| `ProfilePage` | `templates/profile.html:91-223`, `static/site.js:149-214` | `ViewProfile()`, `EditUsername()`, `EditContactDetails()`, `SubmitProfileUpdate()`, `DisplayUpdateResult()` |
| `ProfileController` | `main.py:1644-1818` | `ViewCurrentProfile()` `main.py:1644`, `GetProfile()` `main.py:1649`, `ValidateProfileInput()` `main.py:1681`, `UpdateProfile()` `main.py:1714`, `SaveProfileChanges()` `main.py:1755` |
| `UserProfile` | `main.py:202-242` | `GetProfileDetails()` `main.py:202`, `UpdateProfileDetails()` `main.py:206`, `SaveProfile()` `main.py:242` |
| `UserAccount` | `main.py:158` | `GetUserAccount()` `main.py:158` |

## U5 Change Password

| BCE Class | File / Line | Methods / Line |
|---|---|---|
| `ChangePasswordPage` | `templates/settings.html:95-150`, `static/site.js:266-294` | `EnterCurrentPassword()`, `EnterNewPassword()`, `ConfirmNewPassword()`, `SubmitPasswordChange()`, `DisplayChangeResult()` |
| `PasswordController` | `main.py:1824-1961` | `ValidationCurrentPassword()` `main.py:1824`, `ValidateNewPassword()` `main.py:1836`, `ValidatePasswordPolicy()` `main.py:1865`, `SendPasswordChangeNotification()` `main.py:1881`, `UpdatePassword()` `main.py:1891` |
| `UserProfile` | `main.py:268-272` | `GetPasswordHash()` `main.py:268`, `UpdatePasswordHash()` `main.py:272` |
| `PasswordHistory` | `main.py:289-300` | `StorePasswordHistory()` `main.py:289`, `GetPreviousPasswords()` `main.py:300` |

## U1-5 Routes

| Route | File / Line | Purpose |
|---|---|---|
| `GET /auth` | `main.py:3511-3528` | Register and login boundary page |
| `GET /profile` | `main.py:3444-3481` | Profile boundary page |
| `GET /settings` | `main.py:3484-3508` | Change-password boundary page |
| `GET /logout` | `main.py:3529-3562` | Logout |
| `POST /api/auth/send-code` | `main.py:3564-3570` | Send registration verification code |
| `POST /api/auth/register` | `main.py:3572-3589` | Register account |
| `POST /api/auth/login` | `main.py:3591-3598` | Login |
| `POST /api/profile/update` | `main.py:3629-3657` | Update profile information |
| `POST /api/settings/change-password` | `main.py:3659-3674` | Change password |
